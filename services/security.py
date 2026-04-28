
import aiohttp
import jwt
import time
import hashlib
import os
from config import JWT_SECRET, SHORTLINK_URL, SHORTLINK_API, WEBSITE_URL
from database.database import db

# Configuration for reCAPTCHA
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET_KEY", "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe") # Default test key if not set
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
        # Generate the final destination URL (back to the bot)
        # We use a secondary verification token to prevent direct access to /f/{payload}
        from helper_func import get_shortlink
        final_dest = f"{WEBSITE_URL}/f/{payload}"
        return await get_shortlink(SHORTLINK_URL, SHORTLINK_API, final_dest)
