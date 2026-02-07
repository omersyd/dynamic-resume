"""
Template Parser

Splits a LaTeX resume template into preamble and body,
and extracts a command cheatsheet for the LLM to reference.
"""

import re
from typing import Dict, List


class TemplateParser:
    """Parses LaTeX templates into structural components."""

    @staticmethod
    def parse(sample_latex: str) -> Dict[str, str]:
        """
        Split a LaTeX template into preamble and body.

        Returns:
            {
                "preamble": everything up to and including \\begin{document},
                "body": content between \\begin{document} and \\end{document},
                "command_cheatsheet": human-readable summary of custom commands
            }
        """
        begin_marker = r"\begin{document}"
        end_marker = r"\end{document}"

        begin_idx = sample_latex.find(begin_marker)
        end_idx = sample_latex.find(end_marker)

        if begin_idx == -1 or end_idx == -1:
            # Fallback: treat entire thing as body, empty preamble
            return {
                "preamble": "",
                "body": sample_latex,
                "command_cheatsheet": ""
            }

        preamble = sample_latex[:begin_idx + len(begin_marker)]
        body = sample_latex[begin_idx + len(begin_marker):end_idx].strip()

        cheatsheet = TemplateParser.build_command_cheatsheet(preamble)

        return {
            "preamble": preamble,
            "body": body,
            "command_cheatsheet": cheatsheet
        }

    @staticmethod
    def reassemble(preamble: str, body: str) -> str:
        """Combine preamble + generated body + \\end{document} into complete LaTeX."""
        return f"{preamble}\n\n{body}\n\n\\end{{document}}"

    @staticmethod
    def extract_command_signatures(preamble: str) -> List[str]:
        """
        Extract custom command definitions from the preamble.

        Returns signatures like:
            \\resumeSubheading{arg1}{arg2}{arg3}{arg4}
            \\resumeItem{arg1}
        """
        signatures = []

        # Match \newcommand{\name}[N]{...} or \newcommand{\name}{...}
        pattern = r"\\(?:new|renew)command\{\\([^}]+)\}(?:\[(\d+)\])?"
        matches = re.findall(pattern, preamble)

        for name, arg_count_str in matches:
            if arg_count_str:
                arg_count = int(arg_count_str)
                args = "".join(f"{{arg{i+1}}}" for i in range(arg_count))
            else:
                args = ""
            signatures.append(f"\\{name}{args}")

        return signatures

    @staticmethod
    def build_command_cheatsheet(preamble: str) -> str:
        """
        Build a human-readable cheatsheet of available custom commands.
        """
        signatures = TemplateParser.extract_command_signatures(preamble)

        if not signatures:
            return "No custom commands found in the template preamble."

        lines = ["Available custom commands from the template:"]
        for sig in signatures:
            lines.append(f"  - {sig}")

        return "\n".join(lines)
