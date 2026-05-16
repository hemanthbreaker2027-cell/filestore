import aiohttp
import time
import hashlib
import os
import base64
import secrets
import json
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from urllib.parse import urlparse
from config import JWT_SECRET, SECURE_SECRET_KEY, SHORTLINK_API, WEBSITE_URL, WHITELISTED_DOMAIN
from database.database import db


class SecurityService:

    @staticmethod
    def get_client_ip(request):
        # Robust IP detection for Render/Cloudflare
        xf = request.headers.get("X-Forwarded-For", "")
        cf = request.headers.get("CF-Connecting-IP", "")

        # Get primary client IP (leftmost in X-Forwarded-For)
        return cf or (xf.split(',')[0].strip() if xf else request.remote)

    @staticmethod
    def get_identifier(request):
        ip = SecurityService.get_client_ip(request)
        ua = request.headers.get("User-Agent", "")
        return hashlib.sha256(f"{ip or 'unknown'}{ua}".encode()).hexdigest()

    @staticmethod
    async def get_secure_shortlink(user_id: int, payload: str):
        from helper_func import get_shortlink

        now = int(time.time())
        token_data = {
            "user_id": user_id,
            "payload": payload,
            "issuedAt": now,
            "expiresAt": now + 600  # 10 min
        }

        token = SecureRedirect.encrypt(token_data)

        # Store hash for one-time use
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await db.store_secure_token(token_hash, token_data["expiresAt"])

        padded_id = f"__________{user_id}__________"
        target_url = f"{WEBSITE_URL}/r2/{padded_id}/{token}"

        if WHITELISTED_DOMAIN and SHORTLINK_API:
            return await get_shortlink(WHITELISTED_DOMAIN, SHORTLINK_API, target_url)

        return target_url

    @staticmethod
    def encode_link(link: str):
        return base64.urlsafe_b64encode(link.encode()).decode().rstrip("=")

    @staticmethod
    def decode_link(encoded: str):
        padding = "=" * (4 - len(encoded) % 4)
        return base64.urlsafe_b64decode(encoded + padding).decode()

    @staticmethod
    def get_protection_url(user_id: int, short_link: str):
        token_data = {
            "user_id": user_id,
            "target": short_link,
            "issuedAt": int(time.time()),
            "expiresAt": int(time.time()) + 1800  # 30 min
        }

        encoded = SecureRedirect.encrypt(token_data)

        base = WEBSITE_URL if WEBSITE_URL.startswith("http") else f"https://{WEBSITE_URL}"
        return f"{base}/protect?url={encoded}"

    @staticmethod
    def is_domain_whitelisted(url: str):
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            if domain.startswith("www."):
                domain = domain[4:]

            # Support Telegram links as whitelisted for the direct-to-bot redirection
            if domain == "t.me" or domain == "telegram.me":
                return True

            return domain == WHITELISTED_DOMAIN
        except:
            return False

    @staticmethod
    def extract_slug(url: str):
        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            # Usually the last part of the path is the slug
            return path.split("/")[-1] if path else ""
        except:
            return ""


class SecureRedirect:

    @staticmethod
    def generate_protected_token(data: dict, expiry: int = 300):
        # Now accepts a dict instead of just code
        payload = {
            **data,
            "exp": int(time.time()) + expiry,
            "iat": int(time.time())
        }
        return jwt.encode(payload, SECURE_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_protected_token(token: str):
        try:
            payload = jwt.decode(token, SECURE_SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            print("[JWT ERROR] Token Expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"[JWT ERROR] Invalid Token: {e}")
            return None

    @staticmethod
    def _get_key():
        return hashlib.sha256(JWT_SECRET.encode()).digest()

    @staticmethod
    def encrypt(data: dict):
        key = SecureRedirect._get_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        if "expiresAt" not in data:
            data["expiresAt"] = int(time.time()) + 600

        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        raw = nonce + ciphertext
        final_payload = base64.urlsafe_b64encode(raw).decode().rstrip("=")

        marker = "OTK"
        noise = "1111122blongurl" + secrets.token_hex(50)

        return f"{noise}{marker}{final_payload}{marker}{noise}"

    @staticmethod
    def decrypt(token: str):
        try:
            marker = "OTK"

            if not token or marker not in token:
                return None

            parts = token.split(marker)

            if len(parts) < 3:
                return None

            final_payload_b64 = parts[1].strip()

            # Robust Base64 Padding handling
            missing_padding = len(final_payload_b64) % 4
            if missing_padding:
                final_payload_b64 += "=" * (4 - missing_padding)

            try:
                data = base64.urlsafe_b64decode(final_payload_b64)
            except Exception as b64e:
                print(f"[B64 DECODE ERROR] {b64e}")
                return None

            if len(data) < 13: # Nonce(12) + at least 1 byte ciphertext
                return None

            key = SecureRedirect._get_key()
            nonce = data[:12]
            ciphertext = data[12:]

            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)

            result = json.loads(decrypted.decode())

            # Expiry check
            if time.time() > result.get("expiresAt", 0):
                return None

            return result

        except Exception as e:
            # Graceful error handling to prevent server crash
            print(f"[DECRYPT CRITICAL ERROR] {e}")
            return None
