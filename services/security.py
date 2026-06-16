import time
import hashlib
import os
import base64
import secrets
import json
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from urllib.parse import urlparse
from config import JWT_SECRET, SHORTLINK_URL, SHORTLINK_API, WEBSITE_URL, WHITELISTED_DOMAINS, SECURE_SECRET_KEY
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
    async def get_secure_jwt(user_id: int, payload: str):
        now = int(time.time())
        token_data = {
            "user_id": user_id,
            "payload": payload,
            "iat": now,
            "exp": now + 600  # 10 min
        }
        return jwt.encode(token_data, SECURE_SECRET_KEY, algorithm="HS256")

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
