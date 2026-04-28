
import aiohttp
import jwt
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
MIN_SCORE = 0.5

class SecurityService:
    @staticmethod
    async def verify_recaptcha(token: str, ip: str, session: aiohttp.ClientSession):
        async with session.post('https://www.google.com/recaptcha/api/siteverify', data={
            'secret': RECAPTCHA_SECRET,
            'response': token,
            'remoteip': ip
        }) as resp:
            result = await resp.json()

        if result.get('success') and result.get('score', 0) >= MIN_SCORE:
            return True, result.get('score')
        return False, result.get('score', 0)

    @staticmethod
    def generate_session_token(payload: str, session_id: str, ip: str):
        return jwt.encode({
            'payload': payload,
            'session_id': session_id,
            'ip': ip,
            'iat': int(time.time()),
            'exp': int(time.time()) + 600 # 10 mins
        }, JWT_SECRET, algorithm='HS256')

    @staticmethod
    def verify_session_token(token: str):
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except:
            return None

    @staticmethod
    def get_identifier(request):
        ip = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For', request.remote)
        ua = request.headers.get('User-Agent', '')
        return hashlib.sha256(f"{ip}{ua}".encode()).hexdigest()

    @staticmethod
    async def get_secure_shortlink(user_id: int, payload: str):
        from helper_func import get_shortlink
        # For the new flow, we use the /r2/ system
        token = SecureRedirect.encrypt({
            "destination": f"https://t.me/placeholder?start=yu3elk{payload}7", # Will be fixed in route
            "payload": payload,
            "expiresAt": int(time.time()) + 600 # 10 mins
        })

        target_url = f"{WEBSITE_URL}/r2/{user_id}/{token}"

        if SHORTLINK_URL and SHORTLINK_API:
            return await get_shortlink(SHORTLINK_URL, SHORTLINK_API, target_url)
        return target_url

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
