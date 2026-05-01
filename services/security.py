
import aiohttp
import time
import hashlib
import os
import base64
import secrets
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import JWT_SECRET, SHORTLINK_URL, SHORTLINK_API, WEBSITE_URL
from database.database import db

# Configuration for reCAPTCHA
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY", "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe")
MIN_SCORE = 0.1 # Lowered threshold to prevent blocking valid users

class SecurityService:
    @staticmethod
    async def verify_recaptcha(token: str, ip: str, session: aiohttp.ClientSession):
        try:
            # We omit remoteip here as it often causes issues in proxy environments like Render/Heroku
            async with session.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': RECAPTCHA_SECRET,
                'response': token
            }) as resp:
                result = await resp.json()

            # Log the full result for debugging
            print(f"[RECAPTCHA DEBUG] Result: {result}")

            if result.get('success'):
                score = result.get('score', 0.5)

                # If using Google's public test keys, always allow to prevent blocking
                if RECAPTCHA_SECRET == "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe":
                    return True, score

                if score >= MIN_SCORE:
                    return True, score
                return False, score

            # If success is false, check for error codes
            error_codes = result.get('error-codes', [])
            print(f"[RECAPTCHA ERROR] Success false. Codes: {error_codes}")

            # Special case for test keys or common dev errors
            if "invalid-input-secret" in error_codes:
                return False, -1 # Indicates config error

            return False, 0

        except Exception as e:
            print(f"[RECAPTCHA EXCEPTION] {e}")
            return False, 0


    @staticmethod
    def get_identifier(request):
        ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        ua = request.headers.get('User-Agent', '')
        return hashlib.sha256(f"{ip}{ua}".encode()).hexdigest()

    @staticmethod
    async def get_secure_shortlink(user_id: int, payload: str):
        from helper_func import get_shortlink
        # For the new flow, we use the /r2/ system
        now = int(time.time())
        token_data = {
            "payload": payload,
            "issuedAt": now,
            "expiresAt": now + 600 # 10 mins
        }
        token = SecureRedirect.encrypt(token_data)

        # Store hash for one-time use and expiry check
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await db.store_secure_token(token_hash, token_data["expiresAt"])

        target_url = f"{WEBSITE_URL}/r2/{user_id}/{token}"

        if SHORTLINK_URL and SHORTLINK_API:
            return await get_shortlink(SHORTLINK_URL, SHORTLINK_API, target_url)
        return target_url

    @staticmethod
    def encode_link(link: str):
        return base64.urlsafe_b64encode(link.encode()).decode().rstrip("=")

    @staticmethod
    def decode_link(encoded: str):
        padding = '=' * (4 - len(encoded) % 4)
        return base64.urlsafe_b64decode(encoded + padding).decode()

    @staticmethod
    def get_protection_url(short_link: str):
        encoded = SecurityService.encode_link(short_link)
        # Ensure WEBSITE_URL has protocol
        base = WEBSITE_URL if WEBSITE_URL.startswith("http") else f"https://{WEBSITE_URL}"
        return f"{base}/protect?url={encoded}"

class SecureRedirect:
    @staticmethod
    def _get_key():
        # Derive a 32-byte key from JWT_SECRET
        return hashlib.sha256(JWT_SECRET.encode()).digest()

    @staticmethod
    def encrypt(data: dict):
        key = SecureRedirect._get_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)

        # Ensure expiresAt is present
        if 'expiresAt' not in data:
            data['expiresAt'] = int(time.time()) + 600

        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Combine nonce + ciphertext
        raw = nonce + ciphertext
        final_payload = base64.urlsafe_b64encode(raw).decode().rstrip("=")

        # Obfuscation: Add character noise
        marker = "OTK"
        return f"{secrets.token_hex(500)}{marker}{final_payload}{marker}{secrets.token_hex(500)}"

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
            # Add back padding
            missing_padding = len(final_payload_b64) % 4
            if missing_padding:
                final_payload_b64 += '=' * (4 - missing_padding)

            data = base64.urlsafe_b64decode(final_payload_b64)

            key = SecureRedirect._get_key()
            nonce = data[:12]
            ciphertext = data[12:]

            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext, None)

            result = json.loads(decrypted.decode())

            # Check expiry
            if time.time() > result.get('expiresAt', 0):
                return None

            return result
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
