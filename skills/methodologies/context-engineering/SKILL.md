---
name: context-engineering
description: Manage LLM context efficiently for optimal performance. Use when working with large codebases, managing token budgets, or optimizing information retrieval for AI agents.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Context Engineering

**Version**: 2.0  
**Origin**: Overwatch Agent Network - Loaded Context Principle

## When to Use

- Working with large codebases
- Optimizing LLM token usage
- Building AI agent systems
- Managing information retrieval
- Reducing context window overflow

## Core Philosophy

> "Context is a System Resource."
> Load ONLY what's needed. Search before reading.

## Token Budget Thresholds

| Range | State | Strategy |
|-------|-------|----------|
| 0-50% | Normal | Full context loading acceptable |
| 50-80% | Warning | Progressive disclosure, avoid full file reads |
| 80-90% | Critical | Active management, use notes.md, clear old tool results |
| 90%+ | Emergency | Compact context or escalate |

## The Lazy Loading Principle

```
┌─────────────────────────────────────────────────────────────┐
│                  LAZY LOADING HIERARCHY                      │
├─────────────────────────────────────────────────────────────┤
│  1. SEARCH → Know what exists (grep, find, glob)            │
│  2. PREVIEW → Understand structure (head, tail, wc)         │
│  3. TARGET → Load specific sections (sed, awk)              │
│  4. FULL READ → Only when absolutely necessary              │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### Step 1: Search Before Reading

Always search for patterns before loading full files:

```bash
# Find relevant files
find . -name "*.ts" -type f | head -20

# Search for specific patterns
grep -rn "function\|class\|interface" src/ --include="*.ts" | head -50

# Find files containing a term
grep -rl "UserService" src/

# Search with context
grep -B2 -A5 "export class UserService" src/
```

### Step 2: Preview Structure

Understand file structure without loading everything:

```bash
# Check file sizes
wc -l src/**/*.ts 2>/dev/null | sort -n | tail -20

# Preview file structure
head -n 50 src/services/user.service.ts

# See end of file
tail -n 20 src/services/user.service.ts

# Get function/class names only
grep -n "export\|class\|function\|interface" src/services/user.service.ts
```

### Step 3: Target Specific Sections

Load only the code you need:

```bash
# Read specific line range
sed -n '45,80p' src/services/user.service.ts

# Read function definition
sed -n '/export class UserService/,/^}$/p' src/services/user.service.ts

# Extract specific function
awk '/function createUser/,/^  }/' src/services/user.service.ts
```

### Step 4: Context Compression Techniques

When context is filling up:

```markdown
## notes.md - Context Summary

### Key Decisions Made
- Using Prisma for ORM (see src/lib/prisma.ts)
- JWT auth with 1hr expiry
- Rate limiting: 100 req/min per IP

### File Summaries
- **src/services/user.service.ts** (245 lines)
  - createUser(dto): Creates user, validates email
  - getById(id): Returns user or null
  - updateProfile(id, dto): Updates name/avatar

### Current Task
Implementing password reset flow

### Dependencies
- @prisma/client: 5.x
- jsonwebtoken: 9.x
```

## Context-Aware Commands

### File Discovery

```bash
# Project structure overview
tree -L 3 -I 'node_modules|.git|dist' .

# Find large files (potential context hogs)
find . -name "*.ts" -exec wc -l {} \; | sort -n | tail -10

# Find recently modified files
find . -name "*.ts" -mtime -1 -type f

# Find files with specific content
grep -rl "password\|auth\|token" src/
```

### Pattern Extraction

```bash
# Extract all exports
grep -h "^export" src/**/*.ts | sort | uniq

# Extract all imports from a file
grep "^import" src/services/user.service.ts

# Extract type definitions
grep -A10 "^interface\|^type" src/types/*.ts

# Extract function signatures
grep -E "^\s*(async\s+)?(function|const\s+\w+\s*=.*=>)" src/services/*.ts
```

### Dependency Analysis

```bash
# Find what imports a module
grep -rl "from.*user.service" src/

# Find external dependencies
grep -h "from '" src/**/*.ts | grep -v "^\./\|^\.\./\|^@/" | sort | uniq

# Find circular dependency candidates
for f in src/services/*.ts; do
  echo "=== $f imports ==="
  grep "from '\.\." $f
done
```

## Context Management Strategies

### Strategy 1: Progressive Disclosure

Load information in layers:

```
Layer 1: File names and structure
         ↓
Layer 2: Function/class signatures
         ↓
Layer 3: Specific implementation details
         ↓
Layer 4: Full file content (rare)
```

### Strategy 2: Working Notes

Maintain a rolling summary:

```bash
# Create/update working notes
cat >> .context/notes.md << 'EOF'

## Session: 2024-01-15

### Explored Files
- src/auth/jwt.service.ts - JWT handling, uses RS256
- src/auth/password.service.ts - bcrypt hashing, 12 rounds

### Key Patterns Found
- All services extend BaseService
- Error handling uses custom AppError class
- Validation uses Zod schemas

### Next Steps
- Implement password reset endpoint
- Add rate limiting to auth routes
EOF
```

### Strategy 3: Context Pruning

Remove outdated information:

```bash
# Clear old test outputs from context
# (Mental model - these would be in agent memory)

# Archive detailed info to files
cat > .context/user-service-analysis.md << 'EOF'
# UserService Analysis

## Methods
- createUser: lines 45-78
- getById: lines 80-92
- updateProfile: lines 94-120

## Dependencies
- PrismaClient
- EmailService
- CacheService
EOF

# Reference file instead of keeping in context
echo "See .context/user-service-analysis.md for UserService details"
```

### Strategy 4: Semantic Chunking

Group related information:

```markdown
## Auth Module Summary

### Files
- src/auth/auth.module.ts (entry point)
- src/auth/auth.controller.ts (routes)
- src/auth/auth.service.ts (logic)
- src/auth/guards/*.ts (middleware)

### Key Endpoints
- POST /auth/login → JWT token
- POST /auth/register → User + JWT
- POST /auth/refresh → New JWT
- POST /auth/logout → Invalidate token

### Shared Types
- AuthPayload { userId, email, role }
- LoginDto { email, password }
- RegisterDto extends LoginDto { name }
```

## Token Estimation

Rough token estimates for planning:

| Content | ~Tokens |
|---------|---------|
| 1 line of code | 10-20 |
| 100 lines of code | 1,000-2,000 |
| Package.json | 200-500 |
| README.md (typical) | 500-2,000 |
| Full TypeScript file | 500-5,000 |

### Budget Calculation

```
Available context: 128,000 tokens (Claude 3.5)
System prompt: ~2,000 tokens
Conversation history: ~10,000 tokens (accumulated)
Tool results: ~5,000 tokens (accumulated)
---
Available for new content: ~111,000 tokens

At 80% warning threshold: 88,800 tokens used
At 90% critical threshold: 99,900 tokens used
```

## Anti-Patterns

- ❌ Reading entire files before searching
- ❌ Loading node_modules or build outputs
- ❌ Keeping full file contents in context when summaries suffice
- ❌ Not pruning old tool results
- ❌ Loading generated files (*.d.ts, dist/*)
- ❌ Repeatedly loading the same file

## Best Practices Checklist

### Before Loading Content
- [ ] Searched for the pattern first?
- [ ] Checked file size?
- [ ] Can I use a summary instead?
- [ ] Is this information already in context?

### During Session
- [ ] Maintaining working notes?
- [ ] Pruning outdated information?
- [ ] Using targeted reads (line ranges)?
- [ ] Tracking token budget?

### For Large Files
- [ ] Extract only relevant sections?
- [ ] Create summary in notes.md?
- [ ] Use grep/sed for targeted extraction?
- [ ] Consider splitting analysis across turns?

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Context overflow | Prune old results, use summaries |
| Can't find information | Use multiple search patterns |
| Losing track of decisions | Maintain notes.md |
| Repeated file loads | Reference previous analysis |
| Slow responses | Reduce context size |