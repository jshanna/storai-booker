"""Cryptography service for encrypting sensitive data."""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from base64 import urlsafe_b64encode
from loguru import logger

from app.core.config import settings


class CryptoService:
    """
    Service for encrypting and decrypting sensitive data.

    Uses Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256).
    """

    def __init__(self):
        """Initialize crypto service with encryption key."""
        # Derive encryption key from SECRET_KEY
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'storai_booker_salt',  # Fixed salt for deterministic key generation
            iterations=100000,
        )
        key = kdf.derive(settings.secret_key.encode())
        self._fernet = Fernet(urlsafe_b64encode(key))

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string.

        Args:
            plaintext: The string to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        try:
            encrypted = self._fernet.encrypt(plaintext.encode())
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    def decrypt(self, encrypted: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            encrypted: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string
        """
        try:
            decrypted = self._fernet.decrypt(encrypted.encode())
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key for storage.

        Args:
            api_key: The API key to encrypt

        Returns:
            Encrypted API key
        """
        if not api_key:
            return ""
        return self.encrypt(api_key)

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        Decrypt an API key from storage.

        Args:
            encrypted_key: The encrypted API key

        Returns:
            Decrypted API key
        """
        if not encrypted_key:
            return ""
        return self.decrypt(encrypted_key)


# Singleton instance
crypto_service = CryptoService()
