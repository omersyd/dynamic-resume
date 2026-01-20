import re
from typing import List, Tuple


class LatexValidator:
    @staticmethod
    def validate(latex_code: str) -> Tuple[bool, List[str]]:
        """
        Validates LaTeX code for common syntax errors.
        Returns: (is_valid, list_of_errors)
        """
        errors = []

        # 1. Check for basic brace balance
        open_braces = latex_code.count('{')
        close_braces = latex_code.count('}')
        if open_braces != close_braces:
            errors.append(f"Mismatched braces: Found {open_braces} open '{{' and {close_braces} close '}}'.")

        # 2. Check for environment balance (basic)
        begin_tags = re.findall(r'\\begin\{([^}]+)\}', latex_code)
        end_tags = re.findall(r'\\end\{([^}]+)\}', latex_code)

        # This is a naive check (counts) - a real parser would track nesting
        if len(begin_tags) != len(end_tags):
            errors.append(f"Mismatched environments: Found {len(begin_tags)} \\begin vs {len(end_tags)} \\end tags.")
        else:
            # Check if set types match (order independent naive check)
            from collections import Counter
            if Counter(begin_tags) != Counter(end_tags):
                errors.append(
                    f"Environment types do not match. Started: {set(begin_tags) - set(end_tags)}. "
                    f"Ended: {set(end_tags) - set(begin_tags)}"
                )

        # 3. Check for specific common hallucinations
        if "```" in latex_code:
            errors.append("Markdown code blocks (```) found in output. Please remove them.")

        return (len(errors) == 0, errors)
