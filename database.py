import os                                   # standard library: read environment variables
from dotenv import load_dotenv              # reads .env and puts its values into os.environ
from supabase import create_client, Client  # create_client = factory function; Client = type for hints

load_dotenv()                               # call once, BEFORE reading any env var

SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")  # None if missing (os.environ[...] would raise)
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")  # `str | None` = "string or nothing"

if not SUPABASE_URL or not SUPABASE_KEY:    # `not x` is True for None AND empty string
    raise RuntimeError(                     # crash at startup with a clear message
        "Missing SUPABASE_URL or SUPABASE_KEY. Check your .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # one shared client; no network call yet
