import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from jose import JWTError, jwt
except ModuleNotFoundError:
    JWTError = ValueError
    jwt = None

try:
    from passlib.context import CryptContext
except ModuleNotFoundError:
    CryptContext = None

from app.core.config import get_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None


def hash_password(password: str) -> str:
    if password_context is None:
        return "sha256$" + hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    if password_context is None:
        return hmac.compare_digest(hash_password(plain_password), password_hash)
    return password_context.verify(plain_password, password_hash)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    claims: dict[str, Any] = {"sub": subject, "type": "access", "exp": expires_at}
    if extra_claims:
        claims.update(extra_claims)
    return _encode_claims(claims, settings.jwt_secret_key, settings.jwt_algorithm)


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    claims = {"sub": subject, "type": "refresh", "exp": expires_at}
    return _encode_claims(claims, settings.jwt_secret_key, settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = _decode_claims(token, settings.jwt_secret_key, settings.jwt_algorithm)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
    return payload


def _encode_claims(claims: dict[str, Any], secret: str, algorithm: str) -> str:
    if jwt is not None:
        return jwt.encode(claims, secret, algorithm=algorithm)
    serializable = {
        key: int(value.timestamp()) if isinstance(value, datetime) else value
        for key, value in claims.items()
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join(
        [_urlsafe_json(header), _urlsafe_json(serializable)]
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    return signing_input + "." + _urlsafe_b64(signature)


def _decode_claims(token: str, secret: str, algorithm: str) -> dict[str, Any]:
    if jwt is not None:
        return jwt.decode(token, secret, algorithms=[algorithm])
    header_part, payload_part, signature_part = token.split(".")
    signing_input = f"{header_part}.{payload_part}"
    expected = _urlsafe_b64(hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest())
    if not hmac.compare_digest(expected, signature_part):
        raise ValueError("Invalid token signature")
    payload = json.loads(_urlsafe_b64decode(payload_part))
    expires_at = payload.get("exp")
    if expires_at is not None and datetime.fromtimestamp(expires_at, timezone.utc) < datetime.now(timezone.utc):
        raise ValueError("Token expired")
    return payload


def _urlsafe_json(value: dict[str, Any]) -> str:
    return _urlsafe_b64(json.dumps(value, separators=(",", ":")).encode("utf-8"))


def _urlsafe_b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _urlsafe_b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
