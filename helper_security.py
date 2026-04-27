import base64
import hashlib
import hmac
import json
import os
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from config import SECURE_SECRET_KEY

class SecureRedirect:
    def __init__(self, secret_key: str):
        # Ensure key is 32 bytes for AES-256
        self.key = hashlib.sha256(secret_key.encode()).digest()
        self.backend = default_backend()

    def encrypt(self, data: dict, min_length: int = 100000) -> str:
        # Create a copy to avoid mutating original dict
        data_to_encrypt = data.copy()

        # Convert dict to JSON string
        # Add massive noise to reach the requested extreme length
        current_json = json.dumps(data_to_encrypt)
        if len(current_json) < min_length:
            noise_needed = min_length - len(current_json) - 10 # room for key and quotes
            data_to_encrypt['noise_padding'] = os.urandom(noise_needed // 2).hex()

        json_data = json.dumps(data_to_encrypt).encode()

        # Add padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_data) + padder.finalize()

        # Generate random IV
        iv = os.urandom(16)

        # AES-256-CBC Encryption
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        encrypted_payload = encryptor.update(padded_data) + encryptor.finalize()

        # Combine IV + Encrypted Payload
        combined = iv + encrypted_payload

        # Base64 encode (URL-safe)
        encoded_payload = base64.urlsafe_b64encode(combined).decode().strip('=')

        # Create HMAC signature
        signature = hmac.new(self.key, encoded_payload.encode(), hashlib.sha256).hexdigest()

        return f"{encoded_payload}.{signature}"

    def decrypt(self, token: str) -> dict:
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None

            encoded_payload, provided_signature = parts

            # Verify HMAC signature
            expected_signature = hmac.new(self.key, encoded_payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(provided_signature, expected_signature):
                return None

            # Base64 decode
            # Re-add padding if necessary for base64
            padding_needed = len(encoded_payload) % 4
            if padding_needed:
                encoded_payload += '=' * (4 - padding_needed)

            combined = base64.urlsafe_b64decode(encoded_payload.encode())

            # Extract IV and Encrypted Payload
            iv = combined[:16]
            encrypted_payload = combined[16:]

            # AES-256-CBC Decryption
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_payload) + decryptor.finalize()

            # Remove padding
            unpadder = padding.PKCS7(128).unpadder()
            json_data = unpadder.update(padded_data) + unpadder.finalize()

            return json.loads(json_data.decode())
        except Exception as e:
            print(f"Decryption error: {e}")
            return None

    def generate_random_noise(self, length=16) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode().strip('=')

# Initialize global secure redirect instance
secure_redirect = SecureRedirect(SECURE_SECRET_KEY)
