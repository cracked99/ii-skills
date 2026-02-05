# Contributing to II-Skills

Thank you for your interest in contributing to II-Skills! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Creating a New Skill](#creating-a-new-skill)
- [Skill Requirements](#skill-requirements)
- [Testing Your Skill](#testing-your-skill)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Style Guide](#style-guide)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ii-skills.git
   cd ii-skills
   ```

2. **Create a branch for your work**
   ```bash
   git checkout -b add-my-skill
   ```

3. **Make your changes and test**

4. **Submit a pull request**

## Creating a New Skill

### Step 1: Choose a Name

- Use lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Be descriptive (e.g., `pdf-form-filler` not `helper`)
- Avoid generic names like `utils`, `tools`, `data`

### Step 2: Create the Folder Structure

```bash
mkdir -p skills/my-skill/{scripts,references,assets}
touch skills/my-skill/SKILL.md
```

### Step 3: Write SKILL.md

```markdown
---
name: my-skill
description: What this skill does. Use when the user asks for X or mentions Y.
---

# My Skill

## When to Use

- Trigger condition 1
- Trigger condition 2
- Trigger condition 3

## Quick Start

Minimal example to get started quickly.

## Step-by-Step Process

1. **Step One**: Description
2. **Step Two**: Description
3. **Step Three**: Description

## Examples

### Example 1: Basic Usage

Input: User request
Output: Expected result

### Example 2: Advanced Usage

Input: Complex request
Output: Detailed result

## Error Handling

- **Common Error 1**: How to resolve
- **Common Error 2**: How to resolve

## Dependencies

List any required tools, libraries, or APIs.
```

### Step 4: Add Supporting Files (Optional)

- `scripts/` - Executable scripts the agent can run
- `references/` - Detailed documentation loaded on demand
- `assets/` - Templates, images, data files

## Skill Requirements

### Required

- [ ] `SKILL.md` file exists in skill folder
- [ ] Valid YAML frontmatter with `---` delimiters
- [ ] `name` field matches folder name (lowercase, hyphens only)
- [ ] `description` field explains WHAT it does and WHEN to use it
- [ ] Description is written in third person
- [ ] SKILL.md is under 500 lines

### Recommended

- [ ] Includes "When to Use" section with trigger conditions
- [ ] Includes "Quick Start" section
- [ ] Includes "Examples" section
- [ ] Includes "Error Handling" section
- [ ] Uses consistent terminology throughout
- [ ] No time-sensitive information
- [ ] No deeply nested file references

### Quality Checklist

- [ ] Tested with II-Agent or compatible assistant
- [ ] Works for at least 3 different use cases
- [ ] Error cases are handled gracefully
- [ ] Documentation is clear and complete

## Testing Your Skill

### Local Testing

1. Copy your skill to your local skills directory:
   ```bash
   cp -r skills/my-skill ~/.claude/skills/
   ```

2. Test with II-Agent or Claude Code

3. Verify these scenarios:
   - Skill triggers when expected (description keywords)
   - Skill completes the task correctly
   - Error cases are handled

### Validation Script

Run the validation script before submitting:

```bash
python scripts/validate-skill.py skills/my-skill/
```

This checks:
- Valid YAML frontmatter
- Required fields present
- Name format correct
- File size limits

## Submitting a Pull Request

### Before Submitting

1. Run validation script
2. Test your skill thoroughly
3. Update README.md if adding a new skill
4. Ensure no sensitive data is included

### PR Template

```markdown
## Description

Brief description of the skill and what it does.

## Use Cases

- Use case 1
- Use case 2
- Use case 3

## Testing Done

- [ ] Tested with II-Agent
- [ ] Tested with Claude Code
- [ ] Validation script passes
- [ ] Works for listed use cases

## Checklist

- [ ] SKILL.md has valid frontmatter
- [ ] Description explains what and when
- [ ] Under 500 lines
- [ ] README.md updated (if new skill)
```

### Review Process

1. Maintainers will review your PR
2. Automated validation checks will run
3. You may be asked to make changes
4. Once approved, your skill will be merged

## Style Guide

### YAML Frontmatter

```yaml
---
name: skill-name                    # Required
description: What + When            # Required
allowed-tools: Tool1, Tool2         # Optional
disable-model-invocation: false     # Optional
user-invocable: true                # Optional
---
```

### Markdown Content

- Use ATX-style headers (`#`, `##`, `###`)
- Use fenced code blocks with language identifiers
- Use bullet lists for triggers and conditions
- Use numbered lists for step-by-step processes
- Keep lines under 100 characters when practical

### Description Format

```
<What the skill does in active voice>. Use when <specific triggers or contexts>.
```

Good:
```
Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Bad:
```
This skill helps with PDFs.
```

### Code Examples

- Use realistic, working examples
- Include expected output when helpful
- Handle common error cases
- Use comments sparingly and only when necessary

## Questions?

If you have questions about contributing, please:

1. Check existing issues and discussions
2. Open a new issue with the "question" label
3. Join our community discussions

Thank you for contributing to II-Skills! 🎉