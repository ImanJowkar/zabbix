#!/usr/bin/env python3

import hmac
import json
import re
import socket
import uuid

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


# ---------------------------------------------------------
#  API Settings
# ---------------------------------------------------------

API_HOST = "127.0.0.1"
API_PORT = 8090


# openssl rand -hex 32
API_TOKEN = "CHANGE-THIS-API-TOKEN"



AMI_HOST = "127.0.0.1"
AMI_PORT = 5038
AMI_USERNAME = "call-api"


AMI_PASSWORD = "CHANGE-THIS-AMI-PASSWORD"

AMI_TIMEOUT = 8


# if you use PJSIP
# INTERNAL_TECH = "PJSIP"

# if you use SIP
INTERNAL_TECH = "SIP"

OUTBOUND_CONTEXT = "from-internal"

CALLER_ID = "Notification <1000>"
CALL_TIMEOUT_MS = 30000



ALLOWED_INTERNALS = {
    "201",
}

ALLOWED_EXTERNALS = {
    "09123456789",
}



AUDIO_FILES = {
    "notification": "custom/notification",
}


class AmiError(Exception):
    pass


def validate_ami_value(value):

    value = str(value)

    if "\r" in value or "\n" in value:
        raise AmiError("Invalid AMI value")

    return value


def send_ami_action(file_object, fields):
    lines = []

    for key, value in fields.items():
        key = validate_ami_value(key)
        value = validate_ami_value(value)
        lines.append("{}: {}\r\n".format(key, value))

    payload = "".join(lines) + "\r\n"

    file_object.write(payload.encode("utf-8"))


def read_ami_message(file_object):
    fields = {}

    while True:
        raw_line = file_object.readline()

        if not raw_line:
            raise AmiError("AMI connection closed unexpectedly")

        line = raw_line.decode("utf-8", errors="replace")
        line = line.rstrip("\r\n")

        if line == "":
            return fields

        if ": " not in line:
            continue

        key, value = line.split(": ", 1)
        fields[key] = value


def read_ami_response(file_object):

    for _ in range(20):
        message = read_ami_message(file_object)

        if "Response" in message:
            return message

    raise AmiError("AMI response was not received")


def originate_call(channel, audio_file):
    action_id = uuid.uuid4().hex

    try:
        sock = socket.create_connection(
            (AMI_HOST, AMI_PORT),
            timeout=AMI_TIMEOUT,
        )
    except OSError as exc:
        raise AmiError("Could not connect to AMI: {}".format(exc))

    try:
        sock.settimeout(AMI_TIMEOUT)
        file_object = sock.makefile("rwb", buffering=0)

        
        banner = file_object.readline().decode(
            "utf-8",
            errors="replace",
        )

        if not banner.startswith("Asterisk Call Manager"):
            raise AmiError("Unexpected AMI banner: {}".format(banner.strip()))

        
        send_ami_action(
            file_object,
            {
                "Action": "Login",
                "Username": AMI_USERNAME,
                "Secret": AMI_PASSWORD,
                "Events": "off",
            },
        )

        login_response = read_ami_response(file_object)

        if login_response.get("Response") != "Success":
            raise AmiError(
                "AMI login failed: {}".format(
                    login_response.get("Message", "Unknown error")
                )
            )

       
        send_ami_action(
            file_object,
            {
                "Action": "Originate",
                "ActionID": action_id,
                "Channel": channel,
                "Context": "api-playback",
                "Exten": "s",
                "Priority": "1",
                "CallerID": CALLER_ID,
                "Timeout": str(CALL_TIMEOUT_MS),
                "Async": "true",
                "Variable": "AUDIO_FILE={}".format(audio_file),
            },
        )

        originate_response = read_ami_response(file_object)

        if originate_response.get("Response") != "Success":
            raise AmiError(
                "Originate failed: {}".format(
                    originate_response.get("Message", "Unknown error")
                )
            )

        
        try:
            send_ami_action(
                file_object,
                {
                    "Action": "Logoff",
                },
            )
        except Exception:
            pass

        return {
            "action_id": action_id,
            "ami_message": originate_response.get(
                "Message",
                "Originate queued",
            ),
        }

    finally:
        try:
            file_object.close()
        except Exception:
            pass

        sock.close()


def build_channel(call_type, destination):
    if call_type == "internal":
        if not re.fullmatch(r"[1-9][0-9]{1,5}", destination):
            raise ValueError("Invalid internal extension")

        if destination not in ALLOWED_INTERNALS:
            raise ValueError("Internal extension is not allowed")

        return "{}/{}".format(INTERNAL_TECH, destination)

    if call_type == "external":
        if not re.fullmatch(r"0[0-9]{9,10}", destination):
            raise ValueError("Invalid external telephone number")

        if destination not in ALLOWED_EXTERNALS:
            raise ValueError("External telephone number is not allowed")

        return "Local/{}@{}/n".format(
            destination,
            OUTBOUND_CONTEXT,
        )

    raise ValueError("type must be internal or external")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class ApiHandler(BaseHTTPRequestHandler):

    server_version = "IssabelCallAPI/1.0"

    def send_json(self, status_code, data):
        body = json.dumps(
            data,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def is_authorized(self):
        authorization = self.headers.get("Authorization", "")
        expected = "Bearer {}".format(API_TOKEN)

        return hmac.compare_digest(
            authorization,
            expected,
        )

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "ok": True,
                    "service": "issabel-call-api",
                },
            )
            return

        self.send_json(
            404,
            {
                "ok": False,
                "error": "Not found",
            },
        )

    def do_POST(self):
        if self.path != "/call":
            self.send_json(
                404,
                {
                    "ok": False,
                    "error": "Not found",
                },
            )
            return

        if not self.is_authorized():
            self.send_json(
                401,
                {
                    "ok": False,
                    "error": "Unauthorized",
                },
            )
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )
        except ValueError:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid Content-Length",
                },
            )
            return

        if content_length <= 0 or content_length > 4096:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid request size",
                },
            )
            return

        try:
            request_body = self.rfile.read(content_length)
            payload = json.loads(request_body.decode("utf-8"))
        except Exception:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON",
                },
            )
            return

        call_type = str(payload.get("type", "")).strip()
        destination = str(payload.get("destination", "")).strip()
        audio_key = str(payload.get("audio", "")).strip()

        audio_file = AUDIO_FILES.get(audio_key)

        if audio_file is None:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Audio file is not allowed",
                },
            )
            return

        try:
            channel = build_channel(
                call_type=call_type,
                destination=destination,
            )

            result = originate_call(
                channel=channel,
                audio_file=audio_file,
            )

        except ValueError as exc:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": str(exc),
                },
            )
            return

        except AmiError as exc:
            print(
                "AMI ERROR destination={} error={}".format(
                    destination,
                    exc,
                )
            )

            self.send_json(
                502,
                {
                    "ok": False,
                    "error": str(exc),
                },
            )
            return

        print(
            "CALL QUEUED action_id={} type={} destination={} audio={}".format(
                result["action_id"],
                call_type,
                destination,
                audio_key,
            )
        )

        self.send_json(
            202,
            {
                "ok": True,
                "status": "queued",
                "action_id": result["action_id"],
                "message": result["ami_message"],
            },
        )

    def log_message(self, message_format, *args):
        print(
            "{} - {}".format(
                self.client_address[0],
                message_format % args,
            )
        )


def main():
    print(
        "Starting API on http://{}:{}".format(
            API_HOST,
            API_PORT,
        )
    )

    server = ThreadedHTTPServer(
        (API_HOST, API_PORT),
        ApiHandler,
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()