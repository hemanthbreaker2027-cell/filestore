
import aiohttp
import jwt
import time
import hashlib
import os
import base64
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
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
    async def get_secure_shortlink(payload: str):
        from helper_func import get_shortlink
        # For the new flow, we redirect to /safe/{payload}
        safe_url = f"{WEBSITE_URL}/safe/{payload}"
        if SHORTLINK_URL and SHORTLINK_API:
            return await get_shortlink(SHORTLINK_URL, SHORTLINK_API, safe_url)
        return safe_url

class SecureRedirect:
    @staticmethod
    def _get_key():
        # Derive a 32-byte key from JWT_SECRET
        return hashlib.sha256(JWT_SECRET.encode()).digest()

    @staticmethod
    def encrypt(data: dict):
        key = SecureRedirect._get_key()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Add timestamp to data
        data_copy = data.copy()
        data_copy['ts'] = int(time.time() * 1000)

        content = str(data_copy).encode()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(content) + padder.finalize()

        encrypted = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV + Encrypted Data
        raw = iv + encrypted

        # Generate HMAC
        signature = hashlib.sha256(raw + key).digest()

        final_payload = base64.urlsafe_b64encode(raw + signature).decode()

        # Obfuscation: Add character noise
        # Note: Reduced to 3000 chars to avoid 414 Request-URI Too Large errors in production
        marker = "OTK"
        return f"{secrets.token_hex(1500)}{marker}{final_payload}{marker}{secrets.token_hex(1500)}"

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
            data = base64.urlsafe_b64decode(final_payload_b64)

            key = SecureRedirect._get_key()

            # signature is last 32 bytes
            signature = data[-32:]
            raw = data[:-32]

            # Verify HMAC
            expected_signature = hashlib.sha256(raw + key).digest()
            if not secrets.compare_digest(signature, expected_signature):
                return None

            iv = raw[:16]
            encrypted = raw[16:]

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

            # Convert back to dict (Note: eval is unsafe for untrusted input, but here it's our own encrypted data)
            # Using ast.literal_eval is safer.
            import ast
            result = ast.literal_eval(decrypted.decode())

            # Check expiry (5 minutes)
            if int(time.time() * 1000) - result.get('ts', 0) > 300000:
                return None

            return result
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
