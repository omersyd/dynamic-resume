"""
Template Preservation Verifier

Lightweight validation that generated LaTeX is structurally sound
and uses the same document class as the sample template.
"""

import re
from typing import List, Tuple


class TemplateVerifier:
    """Verifies basic structural consistency between generated and sample LaTeX."""

    @staticmethod
    def extract_documentclass(latex_code: str) -> str:
        """Extract the \\documentclass declaration."""
        pattern = r"\\documentclass(?:\[.*?\])?\{([^}]+)\}"
        match = re.search(pattern, latex_code)
        return match.group(1) if match else ""

    def verify_template_preservation(
        self, sample_latex: str, generated_latex: str
    ) -> Tuple[bool, List[str]]:
        """
        Verify that the generated LaTeX preserves essential template structure.

        Only checks hard requirements:
        - Document class matches the sample
        - \\begin{document} and \\end{document} are present

        Args:
            sample_latex: The original template
            generated_latex: The generated resume

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check document class
        sample_class = self.extract_documentclass(sample_latex)
        generated_class = self.extract_documentclass(generated_latex)

        if sample_class and generated_class and sample_class != generated_class:
            issues.append(
                f"Document class mismatch: expected '{sample_class}', got '{generated_class}'"
            )

        # Check document boundaries
        if "\\begin{document}" not in generated_latex:
            issues.append("Missing \\begin{document}")

        if "\\end{document}" not in generated_latex:
            issues.append("Missing \\end{document}")

        is_valid = len(issues) == 0
        return is_valid, issues
