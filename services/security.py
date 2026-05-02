import aiohttp
import time
import hashlib
import os
import base64
import secrets
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from urllib.parse import urlparse
from config import JWT_SECRET, SHORTLINK_URL, SHORTLINK_API, WEBSITE_URL, WHITELISTED_DOMAINS
from database.database import db

# Configuration for reCAPTCHA
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY", "")
MIN_SCORE = 0.5  # STRICT SECURITY


class SecurityService:

    @staticmethod
    async def verify_recaptcha(token: str, ip: str, session: aiohttp.ClientSession):
        try:
            async with session.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": RECAPTCHA_SECRET,
                    "response": token
                }
            ) as resp:
                result = await resp.json()

            print(f"[RECAPTCHA DEBUG] Result: {result}")

            if result.get("success"):
                score = result.get("score", 0.5)

                # Allow Google test key
                if RECAPTCHA_SECRET == "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe":
                    return True, score

                if score >= MIN_SCORE:
                    return True, score

                return False, score

            error_codes = result.get("error-codes", [])
            print(f"[RECAPTCHA ERROR] {error_codes}")

            if "invalid-input-secret" in error_codes:
                return False, -1

            return False, 0

        except Exception as e:
            print(f"[RECAPTCHA EXCEPTION] {e}")
            return False, 0

    @staticmethod
    def get_identifier(request):
        ip = request.headers.get("CF-Connecting-IP") or request.headers.get(
            "X-Forwarded-For", request.remote
        )

        if ip and "," in ip:
            ip = ip.split(",")[0].strip()

        ua = request.headers.get("User-Agent", "")
        return hashlib.sha256(f"{ip}{ua}".encode()).hexdigest()

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

        if SHORTLINK_URL and SHORTLINK_API:
            return await get_shortlink(SHORTLINK_URL, SHORTLINK_API, target_url)

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

            return domain in WHITELISTED_DOMAINS
        except:
            return False


class SecureRedirect:

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

            if marker not in token:
                return None

            parts = token.split(marker)

            if len(parts) < 3:
                return None

            final_payload_b64 = parts[1]

            # Fix padding
            if len(final_payload_b64) % 4:
                final_payload_b64 += "=" * (4 - len(final_payload_b64) % 4)

            data = base64.urlsafe_b64decode(final_payload_b64)

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
            print(f"[DECRYPT ERROR] {e}")
            return None
