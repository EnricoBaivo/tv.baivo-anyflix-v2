"""Base64 utilities similar to JavaScript Uint8Array extensions."""

import base64
from typing import List


class Base64Utils:
    """Base64 encoding/decoding utilities."""

    @staticmethod
    def from_base64(b64_str: str) -> bytes:
        """Decode base64 string to bytes.

        Args:
            b64_str: Base64 encoded string

        Returns:
            Decoded bytes
        """
        try:
            return base64.b64decode(b64_str)
        except Exception:
            # Custom implementation for compatibility
            m = [-1] * 128
            # Base64 character mapping
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
            for i, char in enumerate(chars):
                m[ord(char)] = i
            m[ord("-")] = 62
            m[ord("_")] = 63

            data = []
            val = 0
            bits = -8

            for char in b64_str:
                char_code = ord(char)
                if char_code >= len(m):
                    continue
                n = m[char_code]
                if n == -1:
                    break
                val = (val << 6) + n
                bits += 6
                while bits >= 0:
                    data.append((val >> bits) & 0xFF)
                    bits -= 8

            return bytes(data)

    @staticmethod
    def to_base64(data: bytes) -> str:
        """Encode bytes to base64 string.

        Args:
            data: Bytes to encode

        Returns:
            Base64 encoded string
        """
        return base64.b64encode(data).decode("ascii")

    @staticmethod
    def decode_utf8(data: bytes) -> str:
        """Decode UTF-8 bytes to string.

        Args:
            data: UTF-8 encoded bytes

        Returns:
            Decoded string
        """
        return data.decode("utf-8", errors="ignore")

    @staticmethod
    def encode_utf8(text: str) -> bytes:
        """Encode string to UTF-8 bytes.

        Args:
            text: String to encode

        Returns:
            UTF-8 encoded bytes
        """
        return text.encode("utf-8")

    @staticmethod
    def reverse_bytes(data: bytes) -> bytes:
        """Reverse byte order.

        Args:
            data: Bytes to reverse

        Returns:
            Reversed bytes
        """
        return data[::-1]
