import os                                      # stdlib module for env vars, like System.getenv() in Java
from dotenv import load_dotenv                 # reads .env file into the process environment
from fastapi import FastAPI, HTTPException     # HTTPException = throw-able HTTP error, like a custom Java exception carrying a status code
from fastapi.middleware.cors import CORSMiddleware  # from Day 4: lets Next.js on :3000 call this API
from pydantic import BaseModel                 # base class for validated request/response shapes (Day 3)
from supabase import create_client, Client     # create_client() = factory, like DriverManager.getConnection(); Client = its type

load_dotenv()  # MUST run before os.getenv(), or your keys come back None

# ---------- Config (fail fast: crash at startup, not on the first request) ----------
SUPABASE_URL = os.getenv("SUPABASE_URL")       # returns None if the variable is missing (no exception)
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:       # `not x` is True for None or "" (like !x in C++ for pointers/strings)
    raise RuntimeError("SUPABASE_URL / SUPABASE_KEY missing from .env")  # raise = throw

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  # `: Client` is a type hint (documentation only, not enforced at runtime)
TABLE = "items"                                # one constant, so a table rename touches one line, not four

# ---------- App ----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],   # exact origin, never "*" in real projects
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------
class ItemCreate(BaseModel):                   # shape of the incoming POST body
    name: str                                  # required; wrong type or missing -> automatic 422

class ItemResponse(BaseModel):                 # shape of what we send back; mirrors the table columns
    id: int
    name: str
    created_at: str

# ---------- Routes ----------
# Plain `def`, NOT `async def`: the supabase client is synchronous (blocking).
# FastAPI runs plain `def` routes in a thread pool, so a slow DB call won't freeze the event loop.
# Rule: blocking library -> `def`; awaitable library (httpx.AsyncClient) -> `async def`.

@app.get("/items", response_model=list[ItemResponse])  # response_model filters/validates output; list[X] = like List<X> in Java
def list_items():
    res = supabase.table(TABLE).select("*").order("id").execute()  # .table() picks the table, .select("*") = SELECT *, .order("id") = ORDER BY id
    return res.data                                    # .data = list of dicts, one per row (like a ResultSet already converted to maps)

@app.post("/items", response_model=ItemResponse, status_code=201)  # 201 Created is the correct code for a successful insert
def create_item(body: ItemCreate):                     # FastAPI parses the JSON body into an ItemCreate for you
    res = supabase.table(TABLE).insert({"name": body.name}).execute()  # .insert(dict) = INSERT INTO items (name) VALUES (...)
    if not res.data:                                   # insert should return the new row; empty means it didn't happen
        raise HTTPException(status_code=500, detail="Insert failed")
    return res.data[0]                                 # data is a list, so [0] is the one row we inserted (id/created_at filled by the DB)

@app.delete("/items/{item_id}")                        # {item_id} = path parameter, passed to the function below
def delete_item(item_id: int):                         # `: int` makes FastAPI convert and validate the path value ("abc" -> 422)
    res = supabase.table(TABLE).delete().eq("id", item_id).execute()  # .eq("id", x) = WHERE id = x. FORGET .eq() AND YOU DELETE EVERY ROW.
    if not res.data:                                   # delete returns the removed rows; empty list = nothing matched
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")  # f"..." = string interpolation, like "..." + id in Java
    return {"deleted": item_id}