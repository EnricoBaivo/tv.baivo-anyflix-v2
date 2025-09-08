import base64
import hashlib
import secrets
from typing import Tuple

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class CryptoAES:
    @staticmethod
    def encrypt_aes_crypto_js(plain_text: str, passphrase: str) -> str:
        """
        Encrypt text using AES in CBC mode compatible with CryptoJS.

        Args:
            plain_text: The text to encrypt
            passphrase: The passphrase to derive key from

        Returns:
            Base64 encoded encrypted string with salt
        """
        try:
            salt = CryptoAES._gen_random_with_non_zero(8)
            key, iv = CryptoAES._derive_key_and_iv(passphrase.strip(), salt)

            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Add PKCS7 padding
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plain_text.strip().encode("utf-8"))
            padded_data += padder.finalize()

            # Encrypt
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()

            # Combine with salt and "Salted__" prefix
            salted_prefix = b"Salted__"
            encrypted_bytes_with_salt = salted_prefix + salt + encrypted_bytes

            return base64.b64encode(encrypted_bytes_with_salt).decode("utf-8")
        except Exception as error:
            raise error

    @staticmethod
    def decrypt_aes_crypto_js(encrypted: str, passphrase: str) -> str:
        """
        Decrypt text encrypted with AES in CBC mode compatible with CryptoJS.

        Args:
            encrypted: Base64 encoded encrypted string
            passphrase: The passphrase to derive key from

        Returns:
            Decrypted plain text
        """
        try:
            encrypted_bytes_with_salt = base64.b64decode(encrypted.strip())

            # Extract encrypted bytes and salt
            encrypted_bytes = encrypted_bytes_with_salt[
                16:
            ]  # Skip "Salted__" (8) + salt (8)
            salt = encrypted_bytes_with_salt[8:16]  # Extract salt

            key, iv = CryptoAES._derive_key_and_iv(passphrase.strip(), salt)

            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()

            # Decrypt
            padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()

            # Remove PKCS7 padding
            unpadder = padding.PKCS7(128).unpadder()
            plain_data = unpadder.update(padded_data) + unpadder.finalize()

            return plain_data.decode("utf-8")
        except Exception as error:
            raise error

    @staticmethod
    def _derive_key_and_iv(passphrase: str, salt: bytes) -> Tuple[bytes, bytes]:
        """
        Derive key and IV from passphrase and salt using MD5 (compatible with CryptoJS).

        Args:
            passphrase: The passphrase string
            salt: Salt bytes

        Returns:
            Tuple of (key, iv) bytes
        """
        password = passphrase.encode("utf-8")
        concatenated_hashes = b""
        current_hash = b""

        while len(concatenated_hashes) < 48:  # Need 32 bytes for key + 16 bytes for IV
            if current_hash:
                pre_hash = current_hash + password + salt
            else:
                pre_hash = password + salt

            current_hash = hashlib.md5(pre_hash).digest()
            concatenated_hashes += current_hash

        key_bytes = concatenated_hashes[:32]  # First 32 bytes for key
        iv_bytes = concatenated_hashes[32:48]  # Next 16 bytes for IV

        return key_bytes, iv_bytes

    @staticmethod
    def _gen_random_with_non_zero(seed_length: int) -> bytes:
        """
        Generate random bytes with non-zero values.

        Args:
            seed_length: Length of random bytes to generate

        Returns:
            Random bytes with no zero values
        """
        result = bytearray()
        for _ in range(seed_length):
            # Generate random value between 1 and 245 (inclusive)
            result.append(secrets.randbelow(245) + 1)
        return bytes(result)
