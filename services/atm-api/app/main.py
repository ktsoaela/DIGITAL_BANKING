import sqlite3
from contextlib import closing
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Digital Banking ATM API", version="0.1.0")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE = DATA_DIR / "atm.sqlite3"


class WithdrawalRequest(BaseModel):
    card_token: str = Field(min_length=8)
    amount: int = Field(gt=0, multiple_of=10)
    terminal_id: str = Field(min_length=1, max_length=40)


class CardlessCashRequest(BaseModel):
    voucher_code: str = Field(min_length=6, max_length=40)
    amount: int = Field(gt=0, multiple_of=10)
    terminal_id: str = Field(min_length=1, max_length=40)


class CashDepositRequest(BaseModel):
    account_id: str = Field(min_length=1)
    amount: int = Field(gt=0, multiple_of=10)
    terminal_id: str = Field(min_length=1, max_length=40)


@app.on_event("startup")
def initialise_database():
    with closing(sqlite3.connect(DATABASE)) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS withdrawals (id INTEGER PRIMARY KEY, card_token TEXT, amount INTEGER, terminal_id TEXT)")
        connection.execute("CREATE TABLE IF NOT EXISTS atm_events (id INTEGER PRIMARY KEY, event_type TEXT, payload TEXT)")
        connection.commit()


@app.get("/health")
def health():
    return {"service": "digital-banking-api", "status": "ok"}


@app.get("/v1/terminals/{terminal_id}")
def terminal(terminal_id: str):
    return {"terminal_id": terminal_id, "status": "available", "cash_units": ["ZAR 50", "ZAR 100", "ZAR 200"]}


@app.post("/v1/withdrawals", status_code=201)
def withdraw(payload: WithdrawalRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO withdrawals(card_token, amount, terminal_id) VALUES (?, ?, ?)", (payload.card_token, payload.amount, payload.terminal_id))
        connection.commit()
        return {"withdrawal_id": cursor.lastrowid, "status": "authorised", "amount": payload.amount, "terminal_id": payload.terminal_id}


@app.post("/v1/cardless-withdrawals", status_code=201)
def cardless_withdrawal(payload: CardlessCashRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO atm_events(event_type, payload) VALUES (?, ?)", ("cardless_withdrawal", str(payload.model_dump())))
        connection.commit()
        return {"withdrawal_id": cursor.lastrowid, "status": "voucher_verified", "amount": payload.amount, "terminal_id": payload.terminal_id}


@app.post("/v1/deposits", status_code=201)
def cash_deposit(payload: CashDepositRequest):
    with closing(sqlite3.connect(DATABASE)) as connection:
        cursor = connection.execute("INSERT INTO atm_events(event_type, payload) VALUES (?, ?)", ("cash_deposit", str(payload.model_dump())))
        connection.commit()
        return {"deposit_id": cursor.lastrowid, "status": "counted", "receipt_available": True, **payload.model_dump()}
