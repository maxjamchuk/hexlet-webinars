import os

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
API_URL = os.environ["API_URL"]


@app.get("/proxy")
def proxy():
    try:
        response = httpx.get(API_URL, timeout=2.0)
        response.raise_for_status()
    except httpx.RequestError:
        return JSONResponse({"error": "upstream unavailable"}, status_code=502)
    except httpx.HTTPStatusError:
        return JSONResponse({"error": "upstream returned an error"}, status_code=502)
    return {"upstream": response.json()}
