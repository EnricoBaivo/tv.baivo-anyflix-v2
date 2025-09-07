"""String utilities similar to JavaScript String extensions."""

import re


class StringUtils:
    """String manipulation utilities."""

    @staticmethod
    def reverse(text: str) -> str:
        """Reverse string.

        Args:
            text: String to reverse

        Returns:
            Reversed string
        """
        return text[::-1]

    @staticmethod
    def swapcase(text: str) -> str:
        """Swap case of ASCII letters.

        Args:
            text: String to process

        Returns:
            String with swapped case
        """
        result = []
        for char in text:
            if char.isalpha() and char.isascii():
                # XOR with 32 to swap case for ASCII letters
                result.append(chr(ord(char) ^ 32))
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def decode_html_entities(text: str) -> str:
        """Decode common HTML entities.

        Args:
            text: Text with HTML entities

        Returns:
            Decoded text
        """
        entities = {
            "&lt;": "<",
            "&gt;": ">",
            "&amp;": "&",
            "&quot;": '"',
            "&#039;": "'",
            "&nbsp;": " ",
        }

        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)

        return text

    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename by removing invalid characters.

        Args:
            filename: Filename to clean

        Returns:
            Cleaned filename
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Remove trailing dots and spaces
        filename = filename.strip(". ")
        return filename
