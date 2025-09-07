import os
import re


class Deobfuscator:
    @staticmethod
    def deobfuscate_js_password(input_string: str) -> str:
        """
        Deobfuscate JavaScript password by evaluating bracket expressions.

        Args:
            input_string: The obfuscated JavaScript string

        Returns:
            Deobfuscated string
        """
        idx = 0
        brackets = ["[", "("]
        evaluated_string = []

        while idx < len(input_string):
            chr_char = input_string[idx]

            if chr_char not in brackets:
                idx += 1
                continue

            closing_index = Deobfuscator._get_matching_bracket_index(idx, input_string)

            if chr_char == "[":
                digit = Deobfuscator._calculate_digit(
                    input_string[idx : closing_index + 1]
                )
                evaluated_string.append(digit)
            else:  # chr_char == '('
                evaluated_string.append(".")

                if (
                    closing_index + 1 < len(input_string)
                    and input_string[closing_index + 1] == "["
                ):
                    skipping_index = Deobfuscator._get_matching_bracket_index(
                        closing_index + 1, input_string
                    )
                    idx = skipping_index + 1
                    continue

            idx = closing_index + 1

        return "".join(evaluated_string)

    @staticmethod
    def _get_matching_bracket_index(opening_index: int, input_string: str) -> int:
        """
        Find the index of the matching closing bracket.

        Args:
            opening_index: Index of the opening bracket
            input_string: The input string

        Returns:
            Index of matching closing bracket, or -1 if not found
        """
        opening_bracket = input_string[opening_index]
        closing_bracket = "]" if opening_bracket == "[" else ")"
        counter = 0

        for idx in range(opening_index, len(input_string)):
            if input_string[idx] == opening_bracket:
                counter += 1
            if input_string[idx] == closing_bracket:
                counter -= 1

            if counter == 0:
                return idx  # found matching bracket
            if counter < 0:
                return -1  # unbalanced brackets

        return -1  # matching bracket not found

    @staticmethod
    def _calculate_digit(input_sub_string: str) -> str:
        """
        Calculate digit from JavaScript bracket expression.

        Args:
            input_sub_string: The bracket expression substring

        Returns:
            Calculated digit as string, or '-' for illegal digit
        """
        # Count occurrences of "!+[]" pattern
        digit = len(re.findall(r"\!\+\[\]", input_sub_string))

        if digit == 0:
            # Check for "+[]" pattern (represents 0)
            if len(re.findall(r"\+\[\]", input_sub_string)) == 1:
                return "0"
        elif 1 <= digit <= 9:
            return str(digit)

        return "-"  # Illegal digit


def load_file(file_path: str) -> str:
    """Load file content."""
    with open(file_path, "r") as f:
        return f.read()


if __name__ == "__main__":

    input_string = load_file("voe_scripts.txt")
    deobfuscated_script = Deobfuscator.deobfuscate_js_password(input_string)
    print(deobfuscated_script)
