import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Banka Core API", version="0.1.0")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE = DATA_DIR / "banka.sqlite3"


class TransferRequest(BaseModel):
    account_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    reference: str = Field(min_length=1, max_length=120)


class InstantPaymentRequest(BaseModel):
    sender_account_id: str = Field(min_length=1)
    recipient_alias: str = Field(min_length=3, max_length=80)
    amount: float = Field(gt=0)
    reference: str = Field(min_length=1, max_length=120)


class PocketRequest(BaseModel):
    account_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=60)
    target_amount: float = Field(gt=0)


class CardControlRequest(BaseModel):
    action: str = Field(pattern="^(freeze|unfreeze|replace)$")


@app.on_event("startup")
def initialise_database():
    with closing(sqlite3.connect(DATABASE)) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS transfers (id INTEGER PRIMARY KEY, account_id TEXT, amount REAL, reference TEXT)")
        connection.execute("CREATE TABLE IF NOT EXISTS feature_events (id INTEGER PRIMARY KEY, event_type TEXT, payload TEXT)")
        connection.commit()


@app.get("/health")
def health():
    return {"service": "banka-api", "status": "ok"}


@app.get("/v1/accounts/{account_id}")
def account(account_id: str):
    return {"account_id": account_id, "currency": "ZAR", "available_balance": 24680.0, "status": "active"}


@app.post("/v1/transfers", status_code=201)
def create_transfer(payload: TransferRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO transfers(account_id, amount, reference) VALUES (?, ?, ?)", (payload.account_id, payload.amount, payload.reference))
        connection.commit()
        return {"transfer_id": cursor.lastrowid, "status": "accepted", **payload.model_dump()}


@app.post("/v1/payments/instant", status_code=201)
def instant_payment(payload: InstantPaymentRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO feature_events(event_type, payload) VALUES (?, ?)", ("instant_payment", str(payload.model_dump())))
        connection.commit()
        return {"payment_id": cursor.lastrowid, "status": "submitted", "rail": "instant", **payload.model_dump()}


@app.post("/v1/pockets", status_code=201)
def create_pocket(payload: PocketRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO feature_events(event_type, payload) VALUES (?, ?)", ("savings_pocket", str(payload.model_dump())))
        connection.commit()
        return {"pocket_id": cursor.lastrowid, "balance": 0, "status": "active", **payload.model_dump()}


@app.get("/v1/pockets/{account_id}")
def pockets(account_id: str):
    return {"account_id": account_id, "pockets": [{"name": "Rainy day", "balance": 3200.0, "target_amount": 10000.0}, {"name": "Travel", "balance": 1850.0, "target_amount": 8000.0}]}


@app.post("/v1/cards/{card_id}/control")
def card_control(card_id: str, payload: CardControlRequest):
    return {"card_id": card_id, "action": payload.action, "status": "confirmed" if payload.action != "replace" else "replacement_requested"}
