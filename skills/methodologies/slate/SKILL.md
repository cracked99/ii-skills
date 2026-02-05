---
name: slate-methodology
description: Apply the S.L.A.T.E. development methodology for structured software engineering. Use when planning complex features, establishing development workflows, or ensuring engineering excellence.
allowed-tools:
  - Bash
  - Read
  - str_replace_based_edit_tool
---

# S.L.A.T.E. Development Methodology

**Version**: 2025.1  
**Origin**: Overwatch Agent Network - Prompt Programming Framework

## When to Use

- Starting a complex feature or project
- Establishing structured development workflows
- Ensuring specification-first development
- When engineering excellence is required
- Multi-phase development tasks

## The S.L.A.T.E. Principles

| Letter | Principle | Description |
|--------|-----------|-------------|
| **S** | **Specification-First** | Define contracts, interfaces, types BEFORE implementation. No code generation without defined requirements |
| **L** | **Loaded Context** | Lazy loading - use grep/search BEFORE read. Load ONLY what's needed. Context is a system resource |
| **A** | **Augmented Intelligence** | Tools are function calls. Verify state before acting. Combine tool calls when independent |
| **T** | **Test-Driven** | Tests are the evaluation metric. RED-GREEN-REFACTOR cycle per feature |
| **E** | **Engineering Excellence** | Follow project's style signature. Consistency > Novelty. Run lint/typecheck after changes |

## Execution Tracks

### Standard Track (Complex Tasks)

For complex features requiring full specification:

```
Phase 0: Constitution → Load project standards, patterns, conventions
Phase 1: Specify     → Create/update spec.md with requirements
Phase 2: Plan        → Create/update plan.md with technical approach
Phase 3: Analyze     → Determine scope, affected files, dependencies
Phase 4: Task        → Break into atomic, testable tasks
Phase 5: Implement   → TDD Loop (Red-Green-Refactor)
```

### Fast-Track (Simple Tasks)

For simpler, well-defined changes:

```
Phase 1: Context   → Create context.md with bullet-point requirements
Phase 2: Implement → Direct implementation with testing
Phase 3: Validate  → Run tests, lint, typecheck
```

## Step-by-Step Process

### Phase 0: Constitution

Load and understand project standards:

```bash
# Check for project conventions
cat README.md 2>/dev/null || echo "No README found"
cat CONTRIBUTING.md 2>/dev/null || echo "No CONTRIBUTING found"
cat .editorconfig 2>/dev/null || echo "No editorconfig found"

# Check existing patterns
ls -la src/ 2>/dev/null || ls -la app/ 2>/dev/null
```

### Phase 1: Specification

Create a specification document:

```markdown
# Feature: [Feature Name]

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Acceptance Criteria
- [ ] Given X, When Y, Then Z

## Interfaces
- Input: TypeA
- Output: TypeB

## Constraints
- Must complete in < 100ms
- Must handle edge case X
```

### Phase 2: Planning

Define technical approach:

```markdown
# Technical Plan

## Approach
Description of the implementation strategy

## Files to Modify
- `src/file1.ts` - Add function X
- `src/file2.ts` - Update interface Y

## Dependencies
- library-x: ^1.0.0

## Risks
- Risk 1: Mitigation strategy
```

### Phase 3: Analysis

Use lazy loading to understand scope:

```bash
# Search before reading
grep -rn "function\|class\|interface" src/ --include="*.ts" | head -50

# Check file sizes before loading
wc -l src/**/*.ts 2>/dev/null | sort -n

# Preview relevant sections
head -n 50 src/relevant-file.ts
```

### Phase 4: Task Breakdown

Create atomic, testable tasks:

```markdown
## Tasks

1. [ ] Create interface for FeatureX
   - Test: Interface exports correctly
   - Files: src/types/featureX.ts

2. [ ] Implement core logic
   - Test: Unit tests pass
   - Files: src/services/featureX.ts

3. [ ] Add API endpoint
   - Test: Integration test passes
   - Files: src/api/featureX.ts
```

### Phase 5: Implementation (TDD)

```python
def implement_feature(feature_spec):
    # 1. Red Phase (The Validator)
    test_case = create_failing_test(feature_spec)
    assert run_test(test_case) == FAIL

    # 2. Green Phase (The Generator)
    code = generate_minimal_code(feature_spec)
    assert run_test(test_case) == PASS

    # 3. Refactor Phase (The Optimizer)
    code = optimize_structure(code)
    assert run_test(test_case) == PASS
```

## The Golden Rule

> "The Prompt is a Downstream Artifact of the Specification."
> If it's not in the Spec (Input), it shouldn't be in the Code (Output).

## Quality Gates

### Before Implementation (Input Validation)
- [ ] Does the task have a Test Requirement?
- [ ] Is the Interface defined?
- [ ] Are acceptance criteria clear?

### After Implementation (Output Validation)
- [ ] Do all tests pass?
- [ ] Is coverage > 90%?
- [ ] Are there 0 linting errors?
- [ ] Has typecheck passed?

## Anti-Patterns to Avoid

- ❌ Starting implementation without specification
- ❌ Loading entire files without searching first
- ❌ Skipping test writing
- ❌ Ignoring project conventions
- ❌ Not running lint/typecheck after changes

## Examples

### Example: Adding a New API Endpoint

**Phase 1 - Spec:**
```markdown
# Feature: User Profile API

## Requirements
- GET /api/users/:id returns user profile
- 404 if user not found
- Rate limited to 100 req/min

## Interface
Input: userId: string
Output: { id, name, email, createdAt }
```

**Phase 5 - TDD:**
```typescript
// RED: Write failing test first
describe('GET /api/users/:id', () => {
  it('returns user profile', async () => {
    const res = await request(app).get('/api/users/123');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('name');
  });
});

// GREEN: Implement minimal code
app.get('/api/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

// REFACTOR: Improve structure
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Scope creep | Return to specification, add new requirements formally |
| Test failures | Check RED phase was properly failing |
| Context overload | Use lazy loading (L principle) |
| Inconsistent style | Check constitution phase, follow project patterns |