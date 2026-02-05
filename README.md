# II-Skills

<p align="center">
  <img src="assets/ii-skills-banner.svg" alt="II-Skills Banner" width="600">
</p>

<p align="center">
  <strong>A curated collection of Agent Skills for II-Agent and compatible AI assistants</strong>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#available-skills">Available Skills</a> •
  <a href="#creating-skills">Creating Skills</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## What are Skills?

**Skills** are modular, self-contained packages that extend AI agent capabilities by providing specialized knowledge, workflows, and tool integrations. Each skill is a folder containing a `SKILL.md` file with YAML frontmatter and markdown instructions.

```
skill-name/
├── SKILL.md           # Required: Main instructions + metadata
├── scripts/           # Optional: Executable scripts
├── references/        # Optional: Additional documentation
└── assets/            # Optional: Templates, images, data
```

## Installation

### Using II-Agent Web Interface

1. Go to [agent.ii.inc](https://agent.ii.inc)
2. Click "Add Skill" → "Connect from GitHub"
3. Paste the skill URL: `https://github.com/YOUR_ORG/ii-skills/tree/main/skills/SKILL_NAME`
4. Click "Connect Skill"

### Manual Installation

Clone this repository and copy skills to your local skills directory:

```bash
git clone https://github.com/YOUR_ORG/ii-skills.git
cp -r ii-skills/skills/SKILL_NAME ~/.claude/skills/
```

## Available Skills

### 📊 Document Processing

| Skill | Description |
|-------|-------------|
| [xlsx](skills/xlsx/) | Spreadsheet creation, editing, analysis with formulas and formatting |
| [docx](skills/docx/) | Word document manipulation with tracked changes and comments |
| [pdf](skills/pdf/) | PDF extraction, creation, merging, splitting, and form filling |
| [pptx](skills/pptx/) | Presentation creation and editing |

### 🎨 Design & Creative

| Skill | Description |
|-------|-------------|
| [frontend-design](skills/frontend-design/) | Production-grade UI/UX design avoiding "AI slop" aesthetics |
| [algorithmic-art](skills/algorithmic-art/) | p5.js art generation with seeded randomness |
| [canvas-design](skills/canvas-design/) | Canvas API design and visualization |
| [theme-factory](skills/theme-factory/) | Theme and color palette generation |

### 🛠️ Development

| Skill | Description |
|-------|-------------|
| [webapp-testing](skills/webapp-testing/) | Comprehensive web application testing |
| [mcp-builder](skills/mcp-builder/) | Model Context Protocol server creation |
| [web-artifacts-builder](skills/web-artifacts-builder/) | Multi-component web artifacts |
| [skill-creator](skills/skill-creator/) | Meta-skill for creating new skills |

### 📝 Documentation & Communication

| Skill | Description |
|-------|-------------|
| [brand-guidelines](skills/brand-guidelines/) | Brand asset and guideline management |
| [doc-coauthoring](skills/doc-coauthoring/) | Collaborative document editing |
| [internal-comms](skills/internal-comms/) | Internal communication templates |
| [slack-gif-creator](skills/slack-gif-creator/) | Slack-compatible GIF creation |

## Creating Skills

### Quick Start

1. Create a new folder in `skills/`:
   ```bash
   mkdir skills/my-skill
   ```

2. Create `SKILL.md` with frontmatter:
   ```markdown
   ---
   name: my-skill
   description: What this skill does. Use when <specific triggers>.
   ---

   # My Skill

   ## When to Use
   - Trigger condition 1
   - Trigger condition 2

   ## Instructions
   Step-by-step instructions...
   ```

3. Test your skill locally before submitting

### SKILL.md Format

```yaml
---
name: skill-name                    # Required: lowercase, hyphens only
description: What + When            # Required: max 1024 chars
allowed-tools: Bash(python *), Read # Optional: pre-approved tools
disable-model-invocation: false     # Optional: manual-only if true
user-invocable: true                # Optional: hidden from menu if false
---
```

### Best Practices

- ✅ Keep `SKILL.md` under 500 lines
- ✅ Use consistent terminology throughout
- ✅ Include error handling and edge cases
- ✅ Write descriptions in third person
- ✅ Move detailed docs to `references/` folder
- ❌ Don't include time-sensitive information
- ❌ Don't explain what the agent already knows
- ❌ Don't use deeply nested file references

See [templates/](templates/) for starter templates.

## Project Structure

```
ii-skills/
├── README.md                 # This file
├── LICENSE                   # Apache 2.0 License
├── CONTRIBUTING.md           # Contribution guidelines
├── skills/                   # All available skills
│   ├── xlsx/
│   │   └── SKILL.md
│   ├── docx/
│   │   └── SKILL.md
│   └── ...
├── templates/                # Skill templates
│   ├── basic/
│   └── advanced/
├── scripts/                  # Utility scripts
│   └── validate-skill.py
└── .github/
    └── workflows/
        └── validate.yml
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding a New Skill

1. Fork this repository
2. Create your skill in `skills/your-skill-name/`
3. Ensure `SKILL.md` has valid frontmatter
4. Test your skill thoroughly
5. Submit a pull request

### Improving Existing Skills

- Fix bugs or typos
- Add missing error handling
- Improve documentation
- Add examples

## Validation

Run the validation script to check your skill:

```bash
python scripts/validate-skill.py skills/my-skill/
```

## License

This project is licensed under the Apache 2.0 License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Original skill implementations
- [II-Agent](https://github.com/Intelligent-Internet/ii-agent) - Agent framework
- [Claude Code](https://code.claude.com) - Skills documentation

---

<p align="center">
  Made with ❤️ for the AI agent community
</p>