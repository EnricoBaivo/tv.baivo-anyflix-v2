import re
from typing import Dict, Iterator, List, Optional


class JsUnpacker:
    """JavaScript unpacker for packed/obfuscated code."""

    _PACKED_REGEX = re.compile(
        r"eval[(]function[(]p,a,c,k,e,[r|d]?", re.IGNORECASE | re.MULTILINE
    )

    _PACKED_EXTRACT_REGEX = re.compile(
        r"[}][(]'(.*)', *(\d+), *(\d+), *'(.*?)'[.]split[(]'[|]'[)]",
        re.IGNORECASE | re.MULTILINE,
    )

    _UNPACK_REPLACE_REGEX = re.compile(r"\b\w+\b", re.IGNORECASE | re.MULTILINE)

    @staticmethod
    def detect(script_block: str) -> bool:
        """
        Detect if a script block contains packed JavaScript.

        Args:
            script_block: The JavaScript code to check

        Returns:
            True if packed JavaScript is detected
        """
        return bool(JsUnpacker._PACKED_REGEX.search(script_block))

    @staticmethod
    def detect_multiple(script_blocks: List[str]) -> List[str]:
        """
        Filter script blocks to only return those containing packed JavaScript.

        Args:
            script_blocks: List of JavaScript code blocks

        Returns:
            List of script blocks that contain packed JavaScript
        """
        return [block for block in script_blocks if JsUnpacker.detect(block)]

    @staticmethod
    def unpack(script_block: str) -> List[str]:
        """
        Unpack a script block containing packed JavaScript.

        Args:
            script_block: The packed JavaScript code

        Returns:
            List of unpacked JavaScript strings
        """
        if JsUnpacker.detect(script_block):
            return list(JsUnpacker._unpacking(script_block))
        return []

    @staticmethod
    def unpack_and_combine(script_block: str) -> Optional[str]:
        """
        Unpack a script block and combine results into a single string.

        Args:
            script_block: The packed JavaScript code

        Returns:
            Combined unpacked JavaScript string, or None if no packed code found
        """
        unpacked = JsUnpacker.unpack(script_block)
        return " ".join(unpacked) if unpacked else None

    @staticmethod
    def _unpacking(script_block: str) -> Iterator[str]:
        """
        Internal method to perform the unpacking.

        Args:
            script_block: The packed JavaScript code

        Yields:
            Unpacked JavaScript strings
        """
        matches = JsUnpacker._PACKED_EXTRACT_REGEX.finditer(script_block)

        for match in matches:
            payload = match.group(1)
            radix_str = match.group(2)
            count_str = match.group(3)
            symtab_str = match.group(4)

            if not all([payload, radix_str, count_str, symtab_str]):
                continue

            symtab = symtab_str.split("|")
            radix = int(radix_str) if radix_str.isdigit() else 10
            count = int(count_str) if count_str.isdigit() else 0
            unbaser = Unbaser(radix)

            if len(symtab) == count:

                def replace_func(match_obj):
                    word = match_obj.group(0)
                    try:
                        index = unbaser.unbase(word)
                        if 0 <= index < len(symtab):
                            unbased = symtab[index]
                            return unbased if unbased else word
                    except (ValueError, IndexError):
                        pass
                    return word

                unpacked_payload = JsUnpacker._UNPACK_REPLACE_REGEX.sub(
                    replace_func, payload
                )
                yield unpacked_payload


class Unbaser:
    """Helper class for converting from different number bases."""

    _ALPHABET: Dict[int, str] = {
        52: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP",
        54: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR",
        62: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        95: " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
    }

    def __init__(self, base: int):
        """
        Initialize unbaser with specified base.

        Args:
            base: The number base to convert from
        """
        self.base = base

    def unbase(self, value: str) -> int:
        """
        Convert a string from the specified base to decimal.

        Args:
            value: The string value to convert

        Returns:
            The decimal integer value
        """
        if 2 <= self.base <= 36:
            try:
                return int(value, self.base)
            except ValueError:
                return 0
        else:
            # Use custom alphabet for bases > 36
            alphabet = self._ALPHABET.get(self.base)
            if not alphabet:
                return 0

            # Create character to index mapping
            char_to_index = {char: idx for idx, char in enumerate(alphabet)}

            return_val = 0
            # Process characters in reverse order (least significant first)
            for i, char in enumerate(reversed(value)):
                char_index = char_to_index.get(char, 0)
                return_val += (self.base**i) * char_index

            return return_val
