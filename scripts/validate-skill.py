#!/usr/bin/env python3
"""
Skill Validator for II-Skills Repository

Validates SKILL.md files for proper structure, frontmatter, and content.

Usage:
    python validate-skill.py <skill-path>
    python validate-skill.py skills/my-skill/
    python validate-skill.py --all  # Validate all skills
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import List, Tuple, Optional


class SkillValidator:
    """Validates skill folders and SKILL.md files."""

    # Validation constants
    MAX_LINES = 500
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 1024
    NAME_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

    VALID_FRONTMATTER_KEYS = {
        'name',
        'description',
        'allowed-tools',
        'disable-model-invocation',
        'user-invocable',
        'context',
        'agent',
        'hooks',
        'model',
        'argument-hint',
        'license',
        'metadata',
        'compatibility',
    }

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self._validate_folder_structure()
        self._validate_skill_md()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_folder_structure(self):
        """Check folder structure requirements."""
        # Check skill folder exists
        if not self.skill_path.exists():
            self.errors.append(f"Skill folder does not exist: {self.skill_path}")
            return

        if not self.skill_path.is_dir():
            self.errors.append(f"Path is not a directory: {self.skill_path}")
            return

        # Check SKILL.md exists
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            self.errors.append(f"SKILL.md not found in {self.skill_path}")
            return

        # Check folder name format
        folder_name = self.skill_path.name
        if not self.NAME_PATTERN.match(folder_name):
            self.errors.append(
                f"Folder name '{folder_name}' invalid. "
                "Use lowercase letters, numbers, and hyphens only."
            )

    def _validate_skill_md(self):
        """Validate SKILL.md content and frontmatter."""
        skill_md = self.skill_path / "SKILL.md"
        if not skill_md.exists():
            return

        content = skill_md.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Check line count
        if len(lines) > self.MAX_LINES:
            self.warnings.append(
                f"SKILL.md has {len(lines)} lines (recommended max: {self.MAX_LINES})"
            )

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content)
        if frontmatter is None:
            self.errors.append("Invalid or missing YAML frontmatter")
            return

        self._validate_frontmatter(frontmatter)
        self._validate_content(content)

    def _parse_frontmatter(self, content: str) -> Optional[dict]:
        """Extract and parse YAML frontmatter."""
        if not content.startswith('---'):
            return None

        parts = content.split('---', 2)
        if len(parts) < 3:
            return None

        try:
            return yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return None

    def _validate_frontmatter(self, frontmatter: dict):
        """Validate frontmatter fields."""
        if frontmatter is None:
            return

        # Check for unknown keys
        for key in frontmatter:
            if key not in self.VALID_FRONTMATTER_KEYS:
                self.warnings.append(f"Unknown frontmatter key: '{key}'")

        # Validate 'name' field
        name = frontmatter.get('name')
        if name:
            if len(name) > self.MAX_NAME_LENGTH:
                self.errors.append(
                    f"Name '{name}' exceeds max length ({self.MAX_NAME_LENGTH} chars)"
                )

            if not self.NAME_PATTERN.match(name):
                self.errors.append(
                    f"Name '{name}' invalid. Use lowercase, numbers, hyphens only."
                )

            # Check name matches folder
            folder_name = self.skill_path.name
            if name != folder_name:
                self.warnings.append(
                    f"Name '{name}' doesn't match folder '{folder_name}'"
                )
        else:
            self.warnings.append("No 'name' field in frontmatter (will use folder name)")

        # Validate 'description' field
        description = frontmatter.get('description')
        if description:
            if len(description) > self.MAX_DESCRIPTION_LENGTH:
                self.errors.append(
                    f"Description exceeds max length ({self.MAX_DESCRIPTION_LENGTH} chars)"
                )

            # Check for "Use when" pattern
            if 'use when' not in description.lower():
                self.warnings.append(
                    "Description should include 'Use when...' trigger conditions"
                )

            # Check for first person
            if description.lower().startswith(('i ', 'i\'', 'we ')):
                self.warnings.append(
                    "Description should be in third person (avoid 'I' or 'We')"
                )
        else:
            self.errors.append("Missing required 'description' field")

        # Validate boolean fields
        for field in ['disable-model-invocation', 'user-invocable']:
            value = frontmatter.get(field)
            if value is not None and not isinstance(value, bool):
                self.errors.append(f"'{field}' must be a boolean (true/false)")

    def _validate_content(self, content: str):
        """Validate markdown content structure."""
        # Check for recommended sections
        recommended_sections = [
            ('When to Use', 'when to use'),
            ('Quick Start', 'quick start'),
            ('Examples', 'example'),
        ]

        content_lower = content.lower()
        for section_name, pattern in recommended_sections:
            if pattern not in content_lower:
                self.warnings.append(f"Missing recommended section: '{section_name}'")

        # Check for deeply nested references
        ref_pattern = re.compile(r'\[.*?\]\((?:\.\.\/){2,}.*?\)')
        if ref_pattern.search(content):
            self.warnings.append("Deeply nested file references detected (avoid ../..)")


def validate_skill(skill_path: str) -> bool:
    """Validate a single skill and print results."""
    print(f"\n{'='*60}")
    print(f"Validating: {skill_path}")
    print('='*60)

    validator = SkillValidator(skill_path)
    is_valid, errors, warnings = validator.validate()

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"   • {error}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")

    if is_valid:
        print("\n✅ Skill is valid!")
    else:
        print("\n❌ Skill has errors that must be fixed.")

    return is_valid


def validate_all_skills(skills_dir: str = "skills") -> bool:
    """Validate all skills in the skills directory."""
    skills_path = Path(skills_dir)

    if not skills_path.exists():
        print(f"Skills directory not found: {skills_dir}")
        return False

    all_valid = True
    skill_count = 0
    error_count = 0

    for skill_folder in sorted(skills_path.iterdir()):
        if skill_folder.is_dir() and not skill_folder.name.startswith('.'):
            skill_count += 1
            if not validate_skill(str(skill_folder)):
                error_count += 1
                all_valid = False

    print(f"\n{'='*60}")
    print(f"SUMMARY: {skill_count - error_count}/{skill_count} skills valid")
    print('='*60)

    return all_valid


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    if arg == '--all':
        success = validate_all_skills()
    elif arg == '--help' or arg == '-h':
        print(__doc__)
        sys.exit(0)
    else:
        success = validate_skill(arg)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()