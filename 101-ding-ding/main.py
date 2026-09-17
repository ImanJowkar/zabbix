from enum import Enum
from time import sleep
import winsound

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="Zabbix Sound Alert API",
    description="Play Windows alert sounds based on Zabbix severity",
    version="1.0.0",
)


class Severity(str, Enum):
    not_classified = "not_classified"
    information = "information"
    warning = "warning"
    average = "average"
    high = "high"
    disaster = "disaster"


class AlertRequest(BaseModel):
    severity: Severity


SOUND_PATTERNS = {
    Severity.not_classified: {
        "pattern": [
            (500, 250, 150),
        ],
        "repeat": 5,
    },

    Severity.information: {
        "pattern": [
            (700, 200, 100),
            (850, 200, 250),
        ],
        "repeat": 4,
    },

    Severity.warning: {
        "pattern": [
            (900, 300, 80),
            (1200, 300, 300),
        ],
        "repeat": 4,
    },

    Severity.average: {
        "pattern": [
            (1100, 250, 80),
            (1400, 250, 80),
            (1100, 250, 300),
        ],
        "repeat": 4,
    },

    Severity.high: {
        "pattern": [
            (1500, 180, 70),
            (1500, 180, 70),
            (1000, 400, 300),
        ],
        "repeat": 4,
    },

    Severity.disaster: {
        "pattern": [
            (1800, 180, 60),
            (1200, 180, 60),
            (1800, 180, 60),
            (1200, 180, 250),
        ],
        "repeat": 5,
    },
}


def play_alert(severity: Severity):
    sound = SOUND_PATTERNS[severity]

    for _ in range(sound["repeat"]):
        for frequency, duration, pause in sound["pattern"]:
            winsound.Beep(frequency, duration)
            sleep(pause / 1000)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/alert")
def alert(
    request: AlertRequest,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        play_alert,
        request.severity
    )

    return {
        "status": "accepted",
        "severity": request.severity
    }