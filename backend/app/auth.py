import hashlib
import hmac
import os
import secrets
import sqlite3
from contextvars import ContextVar, Token
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from app.memory.database import get_connection, initialize_database


SESSION_COOKIE = "workmate_session"
SESSION_DAYS = 7
COOKIE_SECURE = os.getenv("WORKMATE_COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("WORKMATE_COOKIE_SAMESITE", "lax").lower()
_active_user_id: ContextVar[str] = ContextVar("active_user_id", default="")


class AuthRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)
    password: str = Field(..., min_length=8, max_length=128)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    ).hex()


def _create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    connection = get_connection()
    connection.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash, user_id, expires_at.isoformat()),
    )
    connection.commit()
    connection.close()
    return token


def _user_response(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "email": row["email"]}


def get_current_user(session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None):
    if not session_token:
        raise HTTPException(status_code=401, detail="Login required.")

    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
    connection = get_connection()
    row = connection.execute(
        """
        SELECT users.id, users.email
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.token_hash = ? AND sessions.expires_at > ?
        """,
        (token_hash, datetime.now(timezone.utc).isoformat()),
    ).fetchone()
    connection.close()

    if row is None:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    user = _user_response(row)
    _active_user_id.set(user["id"])
    return user


def current_user_id(user: dict) -> str:
    return str(user["id"])


def get_authenticated_user_id() -> str:
    return _active_user_id.get()


def set_authenticated_user_id(user_id: str) -> Token[str]:
    return _active_user_id.set(user_id)


def reset_authenticated_user_id(token: Token[str]) -> None:
    _active_user_id.reset(token)


def register_user(request: AuthRequest) -> tuple[dict, str]:
    initialize_database()
    email = _normalize_email(request.email)
    salt = secrets.token_bytes(16)
    user_id = str(uuid4())
    connection = get_connection()
    try:
        connection.execute(
            """
            INSERT INTO users (id, email, password_hash, password_salt)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, email, _hash_password(request.password, salt), salt.hex()),
        )
        # Preserve the existing local workspace when the first account is created.
        has_users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if has_users == 1:
            for table in ("conversations", "memories", "documents"):
                connection.execute(f"UPDATE {table} SET user_id = ? WHERE user_id IS NULL", (user_id,))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        connection.close()
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    connection.close()
    return {"id": user_id, "email": email}, _create_session(user_id)


def login_user(request: AuthRequest) -> tuple[dict, str]:
    email = _normalize_email(request.email)
    connection = get_connection()
    row = connection.execute(
        "SELECT id, email, password_hash, password_salt FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    connection.close()

    if row is None:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")

    expected = _hash_password(request.password, bytes.fromhex(row["password_salt"]))
    if not hmac.compare_digest(expected, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")

    return _user_response(row), _create_session(row["id"])


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )


def auth_router():
    router = APIRouter(prefix="/api/auth", tags=["Authentication"])

    @router.post("/register")
    def register(request: AuthRequest, response: Response):
        user, token = register_user(request)
        set_session_cookie(response, token)
        return {"user": user}

    @router.post("/login")
    def login(request: AuthRequest, response: Response):
        user, token = login_user(request)
        set_session_cookie(response, token)
        return {"user": user}

    @router.get("/me")
    def me(user: dict = Depends(get_current_user)):
        return {"user": user}

    @router.post("/logout")
    def logout(response: Response, session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None):
        if session_token:
            token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
            connection = get_connection()
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            connection.commit()
            connection.close()
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"message": "Logged out."}

    return router
