from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Section:
    title: str
    content: Dict[str, List[str]]


@dataclass
class Role:
    name: str
    description: str
    core_principles: Section
    guidelines: Section

    def to_string(self) -> str:
        """Reconstructs a readable prompt string similar to the original format."""
        lines = [f"{self.name} = \"\"\""]
        lines.append(self.description.strip())
        lines.append("")
        lines.append("=== CORE PRINCIPLES ===")
        for subsection, points in self.core_principles.content.items():
            lines.append(
                f"{list(self.core_principles.content.keys()).index(subsection)+1}. {subsection}:"
            )
            for p in points:
                lines.append(f"   -> {p}")
            lines.append("")
        lines.append("=== CRITICAL BEHAVIOR GUIDELINES ===")
        for subsection, points in self.guidelines.content.items():
            lines.append(f">> {subsection}:")
            for p in points:
                lines.append(f"   - {p}")
        lines.append('"""')
        return "\n".join(lines)
