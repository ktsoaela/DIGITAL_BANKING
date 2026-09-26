import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Khoebo Trading API", version="0.1.0")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE = DATA_DIR / "trading.sqlite3"


class OrderRequest(BaseModel):
    account_id: str = Field(min_length=1)
    symbol: str = Field(min_length=1, max_length=12)
    side: str = Field(pattern="^(buy|sell)$")
    quantity: int = Field(gt=0)


class ForexConversionRequest(BaseModel):
    account_id: str = Field(min_length=1)
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)
    amount: float = Field(gt=0)


class BOPDeclarationRequest(BaseModel):
    account_id: str = Field(min_length=1)
    purpose_code: str = Field(min_length=2, max_length=30)
    source_country: str = Field(min_length=2, max_length=2)
    amount: float = Field(gt=0)


@app.on_event("startup")
def initialise_database():
    with closing(sqlite3.connect(DATABASE)) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, account_id TEXT, symbol TEXT, side TEXT, quantity INTEGER)")
        connection.execute("CREATE TABLE IF NOT EXISTS forex_events (id INTEGER PRIMARY KEY, event_type TEXT, payload TEXT)")
        connection.commit()


@app.get("/health")
def health():
    return {"service": "khoebo-api", "status": "ok"}


@app.get("/v1/markets")
def markets():
    return {"markets": [{"symbol": "KHOE", "name": "Khoebo Holdings", "currency": "ZAR", "last": 128.40}, {"symbol": "NOVA", "name": "Nova Energy", "currency": "ZAR", "last": 76.15}]}


@app.post("/v1/orders", status_code=201)
def create_order(payload: OrderRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO orders(account_id, symbol, side, quantity) VALUES (?, ?, ?, ?)", (payload.account_id, payload.symbol.upper(), payload.side, payload.quantity))
        connection.commit()
        return {"order_id": cursor.lastrowid, "status": "queued", **payload.model_dump()}


@app.get("/v1/forex/wallets/{account_id}")
def forex_wallets(account_id: str):
    return {"account_id": account_id, "wallets": [{"currency": "USD", "balance": 1250.0}, {"currency": "EUR", "balance": 480.0}, {"currency": "GBP", "balance": 300.0}]}


@app.post("/v1/forex/conversions", status_code=201)
def forex_conversion(payload: ForexConversionRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO forex_events(event_type, payload) VALUES (?, ?)", ("conversion", str(payload.model_dump())))
        connection.commit()
        return {"conversion_id": cursor.lastrowid, "status": "quoted", "indicative_rate": 18.42, **payload.model_dump()}


@app.post("/v1/forex/bop-declarations", status_code=201)
def bop_declaration(payload: BOPDeclarationRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO forex_events(event_type, payload) VALUES (?, ?)", ("bop_declaration", str(payload.model_dump())))
        connection.commit()
        return {"declaration_id": cursor.lastrowid, "status": "submitted_for_review", "next_step": "Upload supporting documents if requested"}
