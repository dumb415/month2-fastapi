import os                          # os: standard library; gives access to environment variables
from dotenv import load_dotenv     # load_dotenv: reads .env and copies each line into os.environ
from fastapi import FastAPI        # FastAPI: the app class, like instantiating your server object

load_dotenv()  # must run BEFORE os.getenv() calls; no .env means it silently does nothing

app = FastAPI(title="Month 2 API")  # `app` is the name uvicorn looks for in "main:app"; title shows in /docs

APP_ENV = os.getenv("APP_ENV", "development")  # getenv(name, default): returns the default if the var is missing, like a safe map.get()


@app.get("/")  # decorator: registers the function below as the handler for GET requests to "/"
async def root() -> dict:  # async def: lets FastAPI serve other requests while this one waits; "-> dict" is a return type hint
    return {  # a returned dict is auto-converted to JSON, so no manual serialization
        "status": "ok",
        "env": APP_ENV,
        # Best practice: report whether a key is SET, never the key itself
        "openai_key_configured": os.getenv("OPENAI_API_KEY") not in (None, "", "your-key-here"),
    }