var params = JSON.parse(value);

function required(name) {
    if (
        typeof params[name] === "undefined" ||
        params[name] === null ||
        String(params[name]).trim() === ""
    ) {
        throw "Required parameter is missing: " + name;
    }

    return String(params[name]).trim();
}

var url = required("url");
var token = required("token");
var destination = required("destination");
var severityOriginal = required("severity");

var severity = severityOriginal.toLowerCase().trim();
var audio;

switch (severity) {
    case "disaster":
        audio = "disaster";
        break;

    case "critical":
    case "high":
        audio = "critical";
        break;

    case "notification":
    case "average":
    case "warning":
    case "information":
    case "not classified":
        audio = "notification";
        break;

    default:
        throw "Unsupported Zabbix severity: " + severityOriginal;
}

var payload = {
    type: "external",
    destination: destination,
    audio: audio
};

Zabbix.log(
    4,
    "[Phone Call Webhook] Sending call request. " +
    "Destination: " + destination +
    ", Severity: " + severityOriginal +
    ", Audio: " + audio
);

var request = new HttpRequest();

request.addHeader("Content-Type: application/json");
request.addHeader("Authorization: Bearer " + token);

var response;

try {
    response = request.post(
        url,
        JSON.stringify(payload)
    );
} catch (error) {
    throw "Unable to connect to call API: " + error;
}

var status = request.getStatus();

Zabbix.log(
    4,
    "[Phone Call Webhook] HTTP status: " +
    status +
    ", Response: " +
    response
);

if (status < 200 || status >= 300) {
    throw "Call API returned HTTP " +
        status +
        ". Response: " +
        response;
}

return JSON.stringify({
    status: "success",
    http_status: status,
    destination: destination,
    severity: severityOriginal,
    audio: audio,
    response: response
});