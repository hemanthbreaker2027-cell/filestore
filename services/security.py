
import jwt
import time
import re
from config import JWT_SECRET

class SecurityService:
    @staticmethod
    def get_client_ip(request):
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip: return cf_ip
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded: return forwarded.split(",")[0].strip()
        peername = request.transport.get_extra_info('peername')
        if peername: return peername[0]
        return "127.0.0.1"

class SecureRedirect:
    @staticmethod
    def generate_protected_token(data, expiry=300):
        payload = {"data": data, "exp": int(time.time() + expiry), "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @staticmethod
    def verify_protected_token(token):
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return decoded.get("data")
        except: return None
