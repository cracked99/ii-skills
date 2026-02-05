---
name: slate-methodology
description: Apply the S.L.A.T.E. development methodology for structured, specification-first software engineering. Use when implementing complex features, establishing rigorous development workflows, ensuring high code quality, practicing TDD, managing context efficiently, or when engineering excellence and maintainability are critical. Triggers include requests for clean architecture implementation, test-driven development, specification-first design, or systematic feature development.
license: MIT
---

# S.L.A.T.E. Development Methodology

**Version 2025.1** - Systematic, Specification-First Engineering

## Overview

S.L.A.T.E. is a development methodology emphasizing specification-first design, efficient context management, test-driven development, and engineering excellence. It provides two execution tracks (Standard and Fast-Track) for different complexity levels.

**Core Philosophy**: The Prompt is a Downstream Artifact of the Specification. If it's not in the spec, it shouldn't be in the code.

## The Five Principles

### S - Specification-First
**Define BEFORE you implement.**

Write clear, testable specifications before writing any code:
- **Contracts**: Define interfaces and data models first
- **Requirements**: Document functional and non-functional requirements
- **Acceptance Criteria**: Specify "done" conditions upfront
- **API Contract**: Define request/response shapes explicitly

**Anti-Pattern**: Writing spec.md after implementation defeats the purpose.

**Example**:
```typescript
// ✅ Specification-First: Interface defined before implementation
interface CreateUserUseCase {
  execute(request: CreateUserRequest): Promise<CreateUserResponse>;
}

// Then implement
class CreateUserService implements CreateUserUseCase {
  execute(request: CreateUserRequest): Promise<CreateUserResponse> {
    // Implementation follows spec
  }
}

// ❌ Wrong: Implementing first, figuring out interface later
class CreateUserService {
  async doSomething(data: any) { /* ... */ }
}
```

---

### L - Loaded Context
**Load lazily, search strategically.**

Context window is a scarce resource. Use it efficiently:
- **Search First**: Use grep/find before reading files
- **Targeted Reads**: Read only relevant sections
- **Progressive Disclosure**: Load details only when needed
- **Pattern Discovery**: Find existing patterns before creating new ones

**Workflow**:
```bash
# ❌ Wasteful - Loading entire file
Read src/services/OrderService.ts

# ✅ Efficient - Search first
grep -n "class.*Service" src/services/OrderService.ts
# → Found pattern at line 15
Read src/services/OrderService.ts --lines 15-50
```

**Anti-Pattern**: Reading entire files when a grep would suffice.

---

### A - Augmented Intelligence
**Tools are function calls, not magic.**

Use tools strategically and verify state:
- **Verify Before Acting**: Check file exists before editing
- **Parallel Execution**: Combine independent tool calls
- **State Awareness**: Understand current state before changes
- **Tool Selection**: Use the right tool for the job

**Example**:
```typescript
// ✅ Parallel independent operations
[
  invoke(Read, "src/domain/User.ts"),
  invoke(Read, "src/domain/Order.ts"),
  invoke(Bash, "npm test -- User.test.ts")
]

// ❌ Sequential when parallel is possible
invoke(Read, "src/domain/User.ts");
wait();
invoke(Read, "src/domain/Order.ts");  // Could have been parallel
```

---

### T - Test-Driven
**Tests are the evaluation metric.**

Follow RED-GREEN-REFACTOR cycle:
1. **RED**: Write failing test first
2. **GREEN**: Minimal implementation to pass
3. **REFACTOR**: Improve code quality while keeping tests green

**Every task must have**:
- Clear test requirements
- Test written before implementation
- All tests passing before completion

**Example TDD Cycle**:
```typescript
// 1. RED - Write failing test
describe('Email', () => {
  it('should validate format', () => {
    expect(() => Email.create('invalid')).toThrow();
  });
});
// Run → FAILS ❌

// 2. GREEN - Minimal implementation
class Email {
  static create(value: string): Email {
    if (!value.includes('@')) throw new Error('Invalid');
    return new Email(value);
  }
}
// Run → PASSES ✅

// 3. REFACTOR - Improve
class Email {
  static create(value: string): Email {
    if (!this.isValid(value)) {
      throw new Error('Invalid email format');
    }
    return new Email(value);
  }
  private static isValid(value: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }
}
// Run → STILL PASSES ✅
```

---

### E - Engineering Excellence
**Consistency over novelty.**

Follow established patterns and maintain quality:
- **Follow Project Patterns**: Mimic existing code style
- **Run Quality Checks**: Lint and typecheck after changes
- **Code Review Standards**: Clean, readable, maintainable
- **No Shortcuts**: Proper error handling, no TODO without issues

**Mandatory Quality Gates**:
```bash
npm run test       # Must pass with 0 failures
npm run lint       # Must pass with 0 errors
npm run typecheck  # Must pass with 0 errors
```

**Anti-Pattern**: Introducing new patterns when project has established ones.

---

## Execution Tracks

### Decision Framework

**Use Standard Track when**:
- Complex business logic involved
- Multiple components affected
- Requirements are unclear or evolving
- High risk of bugs or errors
- Team collaboration needed

**Use Fast-Track when**:
- Simple, well-understood change
- Single file or component
- Clear, obvious implementation
- Low complexity (bug fix, UI tweak)
- Quick iteration needed

### Standard Track (Complex Features)

**6-Phase Process for Complex Work**

#### Phase 0: Constitution
**Load project context efficiently**

Actions:
```bash
# Find project documentation
cat CLAUDE.md || cat PROJECT.md || cat .cursorrules

# Discover patterns
grep -r "class.*Service" src/ | head -5
find . -name "*.test.ts" | head -3 | xargs head -20

# Check dependencies
cat package.json | jq '.dependencies'
cat tsconfig.json  # or equivalent config
```

Output: Understanding of project conventions, patterns, testing setup.

#### Phase 1: Specification
**Define requirements in `spec.md`**

Template:
```markdown
# Specification: [Feature Name]

## Overview
[What and why in 2-3 sentences]

## Functional Requirements
1. [REQ-001] [Specific requirement]
2. [REQ-002] [Specific requirement]

## Non-Functional Requirements
- Performance: [Metric]
- Security: [Requirement]

## API Contract
\`\`\`typescript
interface Request { }
interface Response { }
\`\`\`

## Data Models
\`\`\`typescript
class Entity { }
\`\`\`

## Business Rules
1. [Rule with conditions]

## Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]

## Out of Scope
- [Explicitly excluded]
```

#### Phase 2: Planning
**Define technical approach in `plan.md`**

Template:
```markdown
# Implementation Plan: [Feature Name]

## Architecture Decision
Pattern: [Chosen architecture]
Rationale: [Why]

## Component Breakdown
1. [Component] - [Responsibility]

## File Structure
\`\`\`
src/
├── domain/
└── application/
\`\`\`

## Dependencies
- [Library] - [Purpose]

## Test Strategy
- Unit: [What to test]
- Integration: [What to test]
- E2E: [What to test]

## Implementation Order
1. [Step 1]
2. [Step 2]
```

#### Phase 3: Analysis
**Determine affected files and dependencies**

Actions:
- Search for existing related code
- Map import/dependency chains
- Identify test files to update
- Check for naming/pattern conflicts

#### Phase 4: Task Breakdown
**Create atomic, testable tasks**

Task Template:
```markdown
## Task [N]: [Action] [Target]

**Test Requirements**:
- [ ] Unit test: [Scenario]
- [ ] Integration test: [Scenario]

**Acceptance Criteria**:
- [ ] [Specific criterion]

**Dependencies**: Tasks [X, Y]
**Complexity**: [Low/Medium/High]
```

#### Phase 5: Implementation
**TDD loop for each task**

Process:
1. **RED**: Write failing test
2. **GREEN**: Minimal implementation
3. **REFACTOR**: Improve code
4. **VERIFY**: Run lint, typecheck
5. **COMMIT**: Git commit with message
6. **NEXT**: Move to next task

---

### Fast-Track (Simple Changes)

**3-Phase Process for Simple Work**

#### Phase 1: Context Document
Create `context.md`:
```markdown
# Task: [Short Description]

## Goal
[One sentence goal]

## Requirements
- [Bullet point]
- [Bullet point]

## Acceptance Criteria
- [ ] [Criterion]

## Files to Modify
- [File path]
```

#### Phase 2: Direct Implementation
- Write test first (even on fast-track!)
- Implement feature
- Verify tests pass

#### Phase 3: Validation
```bash
npm run test
npm run lint
npm run typecheck
```

All must pass ✅

---

## Quality Gates

### Before Implementation Checklist
Ask yourself:
- ✓ Do I have clear test requirements?
- ✓ Is the interface/contract defined?
- ✓ Are acceptance criteria specific and testable?
- ✓ Do I understand the "done" state?

If any answer is **NO** → Back to specification phase.

### After Implementation Checklist
**Mandatory (Must ALL pass)**:
```bash
npm run test        # or: pytest, go test, etc.
npm run lint        # or: ruff, golangci-lint, etc.  
npm run typecheck   # or: mypy, tsc --noEmit, etc.
```

**Additional Quality Metrics**:
- ✓ Test coverage > 90% for new code
- ✓ No skipped/pending tests
- ✓ No TODO comments without issue links
- ✓ Documentation updated (if public API changed)

### Definition of Done
A task is **DONE** when:
1. ✅ All tests pass (including new tests for the feature)
2. ✅ Linter passes with 0 errors
3. ✅ Type checker passes with 0 errors
4. ✅ Code review completed (if applicable)
5. ✅ All acceptance criteria met
6. ✅ Specification updated (if requirements changed during implementation)

---

## Quick Reference

### The Golden Rule
**The Prompt is a Downstream Artifact of the Specification.**

If it's not in the spec (input), it shouldn't be in the code (output).

### Standard Track Phases
0. **Constitution** → Load context
1. **Specify** → Write spec.md
2. **Plan** → Write plan.md
3. **Analyze** → Determine scope
4. **Task** → Break into tasks
5. **Implement** → TDD loop

### Fast-Track Phases
1. **Context** → Write context.md
2. **Implement** → Write test + code
3. **Validate** → Run checks

### TDD Cycle
1. **RED** → Failing test
2. **GREEN** → Minimal implementation
3. **REFACTOR** → Improve code

### Quality Commands
```bash
npm run test       # All tests must pass
npm run lint       # 0 errors required
npm run typecheck  # 0 errors required
```

---

## Reference Documentation

For detailed workflows, examples, and patterns:

**Detailed workflow guide**: See [references/detailed-workflow.md](references/detailed-workflow.md)
- Complete walkthrough of Standard Track (all 6 phases)
- Fast-Track implementation guide
- Phase-by-phase templates
- Decision framework for track selection
- Quality gate checklists

**Practical examples**: See [references/examples.md](references/examples.md)
- Full feature example (User Authentication)
- Fast-track example (Add className prop)
- Context loading patterns
- TDD examples with code
- Common scenarios (bug fix, refactoring, new features)

Load these references when you need:
- Step-by-step phase templates
- Real-world implementation examples
- Context loading strategies
- TDD cycle demonstrations
- Quality gate definitions

---

## Common Anti-Patterns to Avoid

### ❌ Specification After Implementation
Writing spec.md after code is already written defeats the purpose.

### ❌ Skipping Tests for "Speed"
Tests ARE the evaluation metric. No tests = incomplete work.

### ❌ Loading Entire Files Unnecessarily
Use grep/search first, then targeted reads.

### ❌ Inventing New Patterns
Follow existing project patterns. Consistency > Novelty.

### ❌ Premature Optimization
Make it work, make it right, THEN make it fast (if needed).

### ❌ Skipping Quality Gates
Lint and typecheck are non-negotiable, not optional.

---

## Benefits

✅ **Predictability**: Specification-first prevents scope creep
✅ **Quality**: TDD ensures testability and correctness
✅ **Efficiency**: Context management reduces token waste
✅ **Maintainability**: Consistent patterns ease future work
✅ **Confidence**: Quality gates catch issues early
