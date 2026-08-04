#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import socket
import uuid

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn


# =========================================================
# API SETTINGS
# =========================================================


API_HOST = "127.0.0.1"
API_PORT = 8090

# openssl rand -hex 32 
API_TOKEN = "CHANGE_THIS_API_TOKEN"


# =========================================================
# ASTERISK AMI SETTINGS
# =========================================================

AMI_HOST = "127.0.0.1"
AMI_PORT = 5038

AMI_USERNAME = "call-api"
AMI_PASSWORD = "CHANGE_THIS_AMI_PASSWORD"

AMI_TIMEOUT = 8


# =========================================================
# CALL SETTINGS
# =========================================================


INTERNAL_TECH = "SIP"


OUTBOUND_CONTEXT = "from-internal"

# If you need to dial 9 to get an outside line, enter "9" here.
# OUTBOUND_PREFIX = "9"
OUTBOUND_PREFIX = ""

CALLER_ID = "Notification <1000>"


CALL_TIMEOUT_MS = 50000


# =========================================================
# ALLOWED DESTINATIONS
# =========================================================


ALLOWED_INTERNALS = {
    "201",
    "298"
}


ALLOWED_EXTERNALS = {
    "09123456789",
    "09121112233"
}


# =========================================================
# AUDIO FILES
# =========================================================

# notification:
# /var/lib/asterisk/sounds/custom/notification.wav
#
# critical:
# /var/lib/asterisk/sounds/custom/payment-reminder.wav
#
# disaster:
# /var/lib/asterisk/sounds/custom/service-expired.wav

AUDIO_FILES = {
    "notification": "custom/notification",
    "critical": "custom/critical",
    "disaster": "custom/disaster"
}


ASTERISK_SOUNDS_DIR = "/var/lib/asterisk/sounds"

AUDIO_EXTENSIONS = (
    ".wav",
    ".gsm",
    ".ulaw",
    ".alaw",
    ".sln"
)


# =========================================================
# ERRORS
# =========================================================

class AmiError(Exception):
    pass


# =========================================================
# SECURITY HELPERS
# =========================================================

def constant_time_compare(value1, value2):

    if value1 is None or value2 is None:
        return False

    if isinstance(value1, unicode):
        value1 = value1.encode("utf-8")
    else:
        value1 = str(value1)

    if isinstance(value2, unicode):
        value2 = value2.encode("utf-8")
    else:
        value2 = str(value2)

    if len(value1) != len(value2):
        return False

    result = 0

    for char1, char2 in zip(value1, value2):
        result |= ord(char1) ^ ord(char2)

    return result == 0


def safe_ami_value(value):

    if isinstance(value, unicode):
        value = value.encode("utf-8")
    else:
        value = str(value)

    if "\r" in value or "\n" in value:
        raise AmiError("Invalid AMI field value")

    return value


# =========================================================
# AUDIO HELPERS
# =========================================================

def audio_file_exists(audio_path):

    for extension in AUDIO_EXTENSIONS:
        full_path = os.path.join(
            ASTERISK_SOUNDS_DIR,
            audio_path + extension
        )

        if os.path.isfile(full_path):
            return True

    return False


# =========================================================
# AMI HELPERS
# =========================================================

def send_ami_action(file_object, fields):

    lines = []

    for key, value in fields:
        safe_key = safe_ami_value(key)
        safe_value = safe_ami_value(value)

        lines.append(
            "%s: %s\r\n" % (
                safe_key,
                safe_value
            )
        )

    payload = "".join(lines) + "\r\n"

    file_object.write(payload)
    file_object.flush()


def read_ami_message(file_object):

    fields = {}

    while True:
        line = file_object.readline()

        if not line:
            raise AmiError(
                "AMI connection closed unexpectedly"
            )

        line = line.rstrip("\r\n")

        if line == "":
            return fields

        if ": " not in line:
            continue

        key, value = line.split(": ", 1)
        fields[key] = value


def read_ami_response(file_object):

    for unused_index in range(30):
        message = read_ami_message(file_object)

        if "Response" in message:
            return message

    raise AmiError("AMI response was not received")


def originate_call(channel, audio_path):

    action_id = uuid.uuid4().hex
    sock = None
    file_object = None

    try:
        sock = socket.create_connection(
            (AMI_HOST, AMI_PORT),
            AMI_TIMEOUT
        )

        sock.settimeout(AMI_TIMEOUT)

        file_object = sock.makefile(
            "rwb",
            0
        )

        banner = file_object.readline()

        if not banner.startswith("Asterisk Call Manager"):
            raise AmiError(
                "Unexpected AMI banner: %s"
                % banner.strip()
            )


        send_ami_action(
            file_object,
            [
                ("Action", "Login"),
                ("Username", AMI_USERNAME),
                ("Secret", AMI_PASSWORD),
                ("Events", "off")
            ]
        )

        login_response = read_ami_response(
            file_object
        )

        if login_response.get("Response") != "Success":
            raise AmiError(
                "AMI login failed: %s"
                % login_response.get(
                    "Message",
                    "Unknown error"
                )
            )


        send_ami_action(
            file_object,
            [
                ("Action", "Originate"),
                ("ActionID", action_id),
                ("Channel", channel),
                ("Application", "Playback"),
                ("Data", audio_path),
                ("CallerID", CALLER_ID),
                ("Timeout", str(CALL_TIMEOUT_MS)),
                ("Async", "true")
            ]
        )

        originate_response = read_ami_response(
            file_object
        )

        if originate_response.get("Response") != "Success":
            raise AmiError(
                "Originate failed: %s"
                % originate_response.get(
                    "Message",
                    "Unknown error"
                )
            )

        return {
            "action_id": action_id,
            "message": originate_response.get(
                "Message",
                "Originate successfully queued"
            )
        }

    except socket.timeout:
        raise AmiError(
            "AMI connection timed out"
        )

    except socket.error as error:
        raise AmiError(
            "AMI connection failed: %s"
            % error
        )

    finally:
        if file_object is not None:
            try:
                send_ami_action(
                    file_object,
                    [
                        ("Action", "Logoff")
                    ]
                )
            except Exception:
                pass

            try:
                file_object.close()
            except Exception:
                pass

        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass


# =========================================================
# DESTINATION VALIDATION
# =========================================================

def build_channel(call_type, destination):

    if call_type == "internal":
        if not re.match(
            r"^[1-9][0-9]{1,5}$",
            destination
        ):
            raise ValueError(
                "Invalid internal extension"
            )

        if destination not in ALLOWED_INTERNALS:
            raise ValueError(
                "Internal extension is not allowed"
            )

        return "%s/%s" % (
            INTERNAL_TECH,
            destination
        )

    if call_type == "external":
        if not re.match(
            r"^09[0-9]{9}$",
            destination
        ):
            raise ValueError(
                "Invalid external phone number"
            )

        if destination not in ALLOWED_EXTERNALS:
            raise ValueError(
                "External phone number is not allowed"
            )

        dialed_number = (
            OUTBOUND_PREFIX + destination
        )

        return "Local/%s@%s/n" % (
            dialed_number,
            OUTBOUND_CONTEXT
        )

    raise ValueError(
        "type must be internal or external"
    )


# =========================================================
# HTTP SERVER
# =========================================================

class ThreadedHTTPServer(
    ThreadingMixIn,
    HTTPServer
):
    daemon_threads = True
    allow_reuse_address = True


class CallApiHandler(BaseHTTPRequestHandler):

    server_version = "IssabelCallAPI/1.0"

    def send_json(self, status_code, data):
        body = json.dumps(
            data,
            ensure_ascii=True
        )

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Connection",
            "close"
        )

        self.end_headers()
        self.wfile.write(body)


    def is_authorized(self):
        authorization = self.headers.getheader(
            "Authorization",
            ""
        )

        expected = "Bearer %s" % API_TOKEN

        return constant_time_compare(
            authorization,
            expected
        )


    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "ok": True,
                    "service": "issabel-call-api",
                    "python": "2.7.5"
                }
            )
            return

        if self.path == "/audios":
            if not self.is_authorized():
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Unauthorized"
                    }
                )
                return

            items = []

            for audio_id in sorted(
                AUDIO_FILES.keys()
            ):
                audio_path = AUDIO_FILES[
                    audio_id
                ]

                items.append(
                    {
                        "id": audio_id,
                        "available": audio_file_exists(
                            audio_path
                        )
                    }
                )

            self.send_json(
                200,
                {
                    "ok": True,
                    "items": items
                }
            )
            return

        self.send_json(
            404,
            {
                "ok": False,
                "error": "Not found"
            }
        )


    def do_POST(self):
        if self.path != "/call":
            self.send_json(
                404,
                {
                    "ok": False,
                    "error": "Not found"
                }
            )
            return

        if not self.is_authorized():
            self.send_json(
                401,
                {
                    "ok": False,
                    "error": "Unauthorized"
                }
            )
            return

        content_type = self.headers.getheader(
            "Content-Type",
            ""
        )

        if not content_type.lower().startswith(
            "application/json"
        ):
            self.send_json(
                415,
                {
                    "ok": False,
                    "error": "Content-Type must be application/json"
                }
            )
            return

        content_length_text = self.headers.getheader(
            "Content-Length",
            "0"
        )

        try:
            content_length = int(
                content_length_text
            )
        except ValueError:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid Content-Length"
                }
            )
            return

        if content_length <= 0:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Request body is required"
                }
            )
            return

        if content_length > 4096:
            self.send_json(
                413,
                {
                    "ok": False,
                    "error": "Request body is too large"
                }
            )
            return

        try:
            raw_body = self.rfile.read(
                content_length
            )

            payload = json.loads(
                raw_body
            )

        except Exception:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON"
                }
            )
            return

        if not isinstance(payload, dict):
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "JSON body must be an object"
                }
            )
            return

        call_type = payload.get(
            "type",
            ""
        )

        destination = payload.get(
            "destination",
            ""
        )

        audio_id = payload.get(
            "audio",
            ""
        )

        if isinstance(call_type, unicode):
            call_type = call_type.encode(
                "ascii",
                "ignore"
            )

        if isinstance(destination, unicode):
            destination = destination.encode(
                "ascii",
                "ignore"
            )

        if isinstance(audio_id, unicode):
            audio_id = audio_id.encode(
                "ascii",
                "ignore"
            )

        call_type = str(
            call_type
        ).strip().lower()

        destination = str(
            destination
        ).strip()

        audio_id = str(
            audio_id
        ).strip().lower()

        audio_path = AUDIO_FILES.get(
            audio_id
        )

        if audio_path is None:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Unknown audio identifier",
                    "allowed_audios": sorted(
                        AUDIO_FILES.keys()
                    )
                }
            )
            return

        if not audio_file_exists(
            audio_path
        ):
            self.send_json(
                500,
                {
                    "ok": False,
                    "error": "Audio file is unavailable",
                    "audio": audio_id
                }
            )
            return

        try:
            channel = build_channel(
                call_type,
                destination
            )

            result = originate_call(
                channel,
                audio_path
            )

        except ValueError as error:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": str(error)
                }
            )
            return

        except AmiError as error:
            print(
                "AMI ERROR destination=%s "
                "audio=%s error=%s"
                % (
                    destination,
                    audio_id,
                    error
                )
            )

            self.send_json(
                502,
                {
                    "ok": False,
                    "error": str(error)
                }
            )
            return

        print(
            "CALL QUEUED action_id=%s "
            "type=%s destination=%s "
            "audio=%s channel=%s"
            % (
                result["action_id"],
                call_type,
                destination,
                audio_id,
                channel
            )
        )

        self.send_json(
            202,
            {
                "ok": True,
                "status": "queued",
                "action_id": result[
                    "action_id"
                ],
                "type": call_type,
                "destination": destination,
                "audio": audio_id,
                "message": result[
                    "message"
                ]
            }
        )


    def log_message(
        self,
        message_format,
        *args
    ):
        print(
            "%s - %s"
            % (
                self.client_address[0],
                message_format % args
            )
        )


# =========================================================
# MAIN
# =========================================================

def main():
    print(
        "Issabel Call API starting on "
        "http://%s:%s"
        % (
            API_HOST,
            API_PORT
        )
    )

    print(
        "Allowed internals: %s"
        % ", ".join(
            sorted(ALLOWED_INTERNALS)
        )
    )

    print(
        "Allowed external numbers: %s"
        % ", ".join(
            sorted(ALLOWED_EXTERNALS)
        )
    )

    print(
        "Available audios: %s"
        % ", ".join(
            sorted(AUDIO_FILES.keys())
        )
    )

    server = ThreadedHTTPServer(
        (API_HOST, API_PORT),
        CallApiHandler
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print(
            "\nStopping API..."
        )

    finally:
        server.server_close()


if __name__ == "__main__":
    main()