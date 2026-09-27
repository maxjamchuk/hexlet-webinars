import os
import pwd
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
DATA_FILE = Path("/app/data/message.txt")


@app.get("/identity")
def identity():
    uid = os.getuid()
    return {"uid": uid, "user": pwd.getpwuid(uid).pw_name}


@app.post("/write")
def write_message():
    try:
        DATA_FILE.write_text("Hello, Docker!\n", encoding="utf-8")
    except PermissionError:
        return JSONResponse(
            {"error": "permission denied", "path": str(DATA_FILE)}, status_code=500
        )
    return {"status": "written", "path": str(DATA_FILE)}
