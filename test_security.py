import asyncio
import os
import json
import base64
import time
from services.security import SecurityService, SecureRedirect
from config import JWT_SECRET

def test_encryption_decryption():
    print("Testing Encryption/Decryption...")
    test_data = {
        "user_id": 12345,
        "target": "https://arolinks.com/GXC8A",
        "payload": "base64_payload_string",
        "issuedAt": int(time.time()),
        "expiresAt": int(time.time()) + 1800
    }

    encrypted = SecureRedirect.encrypt(test_data)
    print(f"Encrypted Token: {encrypted[:50]}...")

    decrypted = SecureRedirect.decrypt(encrypted)
    print(f"Decrypted Data: {decrypted}")

    assert decrypted is not None
    assert decrypted["user_id"] == test_data["user_id"]
    assert decrypted["target"] == test_data["target"]
    assert decrypted["payload"] == test_data["payload"]
    print("Encryption/Decryption Test Passed!\n")

def test_protection_url_generation():
    print("Testing Protection URL Generation...")
    user_id = 8646416973
    short_link = "https://arolinks.com/GXC8A"
    payload = "dGVzdF9wYXlsb2Fk"

    url = SecurityService.get_protection_url(user_id, short_link, payload)
    print(f"Generated Protection URL: {url}")

    assert "/protect?data=" in url

    # Extract token and decrypt it
    token = url.split("data=")[1]
    decrypted = SecureRedirect.decrypt(token)
    print(f"Decrypted from URL: {decrypted}")

    assert decrypted["user_id"] == user_id
    assert decrypted["target"] == short_link
    assert decrypted["payload"] == payload
    print("Protection URL Generation Test Passed!\n")

if __name__ == "__main__":
    test_encryption_decryption()
    test_protection_url_generation()
