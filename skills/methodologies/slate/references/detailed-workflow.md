# S.L.A.T.E. Methodology - Detailed Workflow Guide

## Table of Contents
1. [Standard Track Workflow](#standard-track-workflow)
2. [Fast-Track Workflow](#fast-track-workflow)
3. [Phase Templates](#phase-templates)
4. [Decision Framework](#decision-framework)
5. [Quality Gates](#quality-gates)

## Standard Track Workflow

For complex tasks requiring comprehensive planning and specification.

### Phase 0: Constitution (Context Loading)
**Objective**: Load project context efficiently before any work begins.

**Actions**:
1. **Search for project constitution**:
   ```bash
   # Look for standard project documentation
   find . -name "CLAUDE.md" -o -name "PROJECT.md" -o -name ".cursorrules"
   ```

2. **Load style guides and patterns**:
   - Grep for coding conventions
   - Check for linting/formatting configs
   - Review existing test patterns
   - Identify architectural patterns in use

3. **Understand dependencies**:
   ```bash
   # Check package managers
   cat package.json   # Node.js
   cat requirements.txt  # Python
   cat go.mod  # Go
   ```

4. **Identify test infrastructure**:
   ```bash
   # Find test configuration
   find . -name "*.test.*" -o -name "*.spec.*" | head -5
   cat jest.config.js  # or vitest.config.ts, pytest.ini, etc.
   ```

**Deliverable**: Mental model of project structure, conventions, and existing patterns.

**Skip Condition**: Simple projects with obvious structure or explicit user guidance.

---

### Phase 1: Specification (Define Requirements)
**Objective**: Create clear, testable requirements BEFORE writing code.

**Create `spec.md` with**:

```markdown
# Feature Specification: [Feature Name]

## Overview
Brief description of what this feature does and why it's needed.

## Functional Requirements
1. [REQ-001] User can do X
2. [REQ-002] System validates Y
3. [REQ-003] Error Z is handled gracefully

## Non-Functional Requirements
- Performance: Response time < 200ms
- Security: Input validation, SQL injection prevention
- Reliability: 99.9% uptime

## API Contract / Interface
\`\`\`typescript
interface CreateUserRequest {
  email: string;
  password: string;
  name: string;
}

interface CreateUserResponse {
  userId: string;
  createdAt: Date;
}
\`\`\`

## Data Models
\`\`\`typescript
class User {
  id: UserId;
  email: Email;
  passwordHash: string;
  name: string;
  createdAt: Date;
}
\`\`\`

## Business Rules
1. Email must be unique
2. Password must be at least 8 characters
3. Name cannot be empty

## Acceptance Criteria
- [ ] User can register with valid email/password
- [ ] System rejects duplicate emails
- [ ] System rejects weak passwords
- [ ] User receives confirmation email

## Out of Scope
- Social login (OAuth)
- Email verification flow
- Password reset
```

**Best Practices**:
- Use "must", "should", "may" (RFC 2119 keywords)
- Define all data types explicitly
- Include validation rules
- Specify error conditions
- List what's explicitly NOT included

**Deliverable**: `spec.md` file with comprehensive requirements.

---

### Phase 2: Planning (Technical Design)
**Objective**: Plan HOW to implement the specification.

**Create `plan.md` with**:

```markdown
# Implementation Plan: [Feature Name]

## Architecture Decision
**Pattern**: Hexagonal Architecture (Ports & Adapters)
**Rationale**: Need testability and database independence

## Component Breakdown
1. **Domain Layer**
   - `User` entity
   - `Email` value object
   - `Password` value object
   - `UserCreatedEvent` domain event

2. **Application Layer**
   - `CreateUserUseCase` port
   - `CreateUserService` implementation
   - `UserRepository` port

3. **Infrastructure Layer**
   - `UserController` (REST adapter)
   - `PostgresUserRepository` (DB adapter)
   - `SendGridEmailService` (email adapter)

## File Structure
\`\`\`
src/
├── domain/
│   ├── entities/User.ts
│   ├── value-objects/Email.ts
│   └── value-objects/Password.ts
├── application/
│   ├── ports/inbound/CreateUserUseCase.ts
│   ├── ports/outbound/UserRepository.ts
│   └── services/CreateUserService.ts
└── infrastructure/
    ├── adapters/inbound/UserController.ts
    └── adapters/outbound/PostgresUserRepository.ts
\`\`\`

## Dependencies
- `bcrypt` - Password hashing
- `validator` - Email validation
- `pg` - PostgreSQL client

## Database Schema
\`\`\`sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
\`\`\`

## Test Strategy
1. **Unit Tests** - Domain logic (Email validation, Password strength)
2. **Integration Tests** - Application services with in-memory repo
3. **E2E Tests** - Full HTTP request through controller

## Risk Assessment
- **High**: Database connection failures → Implement connection pooling
- **Medium**: Email service downtime → Queue emails for retry
- **Low**: Password hashing performance → Acceptable trade-off for security

## Implementation Order
1. Value objects (Email, Password)
2. User entity
3. Ports (interfaces)
4. Application service
5. Repository adapter
6. Controller adapter
7. Integration tests
8. E2E tests
```

**Deliverable**: `plan.md` file with technical approach.

---

### Phase 3: Analysis (Scope Determination)
**Objective**: Determine exact files to modify and their dependencies.

**Actions**:
1. **Search for existing related code**:
   ```bash
   # Find similar implementations
   grep -r "class.*User" src/
   grep -r "interface.*Repository" src/
   ```

2. **Map dependencies**:
   ```bash
   # Find import chains
   grep -r "from.*User" src/
   ```

3. **Identify affected tests**:
   ```bash
   find . -name "*User*.test.ts"
   ```

4. **Check for conflicts**:
   - Naming conflicts (existing User class?)
   - Pattern conflicts (different repo pattern already used?)
   - Dependency conflicts (incompatible versions?)

**Deliverable**: List of files to create/modify and their relationships.

---

### Phase 4: Task Breakdown (Atomic Units)
**Objective**: Break implementation into small, testable tasks.

**Task Template**:
```markdown
## Task [#]

**Title**: [Action Verb] + [Target]

**Test Requirement**:
- [ ] Unit test: [scenario]
- [ ] Integration test: [scenario]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Dependencies**: Tasks [#, #]

**Estimated Complexity**: [Low/Medium/High]
```

**Example Task List**:
```markdown
## Task 1: Create Email Value Object

**Test Requirement**:
- [ ] Unit test: Valid email formats accepted
- [ ] Unit test: Invalid email formats rejected
- [ ] Unit test: Email comparison works correctly

**Acceptance Criteria**:
- [ ] Email class created with private constructor
- [ ] Static factory method validates format
- [ ] Equals method for comparison
- [ ] toString returns email string

**Dependencies**: None

**Estimated Complexity**: Low

---

## Task 2: Create Password Value Object

**Test Requirement**:
- [ ] Unit test: Password must be >= 8 chars
- [ ] Unit test: Password hashing works
- [ ] Unit test: Password verification works

**Acceptance Criteria**:
- [ ] Password class with hash method
- [ ] Validation for minimum length
- [ ] Compare method for authentication

**Dependencies**: None

**Estimated Complexity**: Low

---

## Task 3: Create User Entity

**Test Requirement**:
- [ ] Unit test: User creation with valid data
- [ ] Unit test: User creation fails with invalid email
- [ ] Unit test: User creation fails with weak password

**Acceptance Criteria**:
- [ ] User class with all properties
- [ ] Factory method for creation
- [ ] Validation using Email and Password VOs

**Dependencies**: Task 1, Task 2

**Estimated Complexity**: Medium
```

**Deliverable**: Ordered list of atomic, testable tasks.

---

### Phase 5: Implementation (TDD Loop)
**Objective**: Implement each task using Test-Driven Development.

**TDD Cycle for Each Task**:

#### 1. RED - Write Failing Test
```typescript
// Email.test.ts
describe('Email', () => {
  it('should accept valid email format', () => {
    expect(() => Email.create('user@example.com')).not.toThrow();
  });
  
  it('should reject invalid email format', () => {
    expect(() => Email.create('invalid-email')).toThrow('Invalid email format');
  });
});
```
Run test → Verify it fails (RED)

#### 2. GREEN - Minimal Implementation
```typescript
// Email.ts
export class Email {
  private constructor(private readonly value: string) {}
  
  static create(email: string): Email {
    if (!this.isValid(email)) {
      throw new Error('Invalid email format');
    }
    return new Email(email);
  }
  
  private static isValid(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  toString(): string {
    return this.value;
  }
}
```
Run test → Verify it passes (GREEN)

#### 3. REFACTOR - Improve Code Quality
```typescript
// Email.ts (refactored)
export class Email {
  private static readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  private constructor(private readonly value: string) {}
  
  static create(email: string): Email {
    if (!this.isValid(email)) {
      throw new Error('Invalid email format');
    }
    return new Email(email);
  }
  
  private static isValid(email: string): boolean {
    return Email.EMAIL_REGEX.test(email);
  }
  
  equals(other: Email): boolean {
    return this.value === other.value;
  }
  
  toString(): string {
    return this.value;
  }
}
```
Run test → Verify still passes → Commit

**Implementation Checklist per Task**:
- [ ] Write test (RED)
- [ ] Minimal implementation (GREEN)
- [ ] Refactor code (REFACTOR)
- [ ] Run all tests
- [ ] Run linter
- [ ] Run type checker
- [ ] Git commit
- [ ] Move to next task

**Deliverable**: Working, tested code for the feature.

---

## Fast-Track Workflow

For simple, well-understood tasks that don't require extensive planning.

### Phase 1: Context Document
**Objective**: Quickly capture requirements without formal spec.

**Create `context.md`**:
```markdown
# Task: [Short Description]

## Goal
What needs to be done in 1-2 sentences

## Requirements
- Bullet point 1
- Bullet point 2
- Bullet point 3

## Acceptance Criteria
- [ ] Works for case A
- [ ] Works for case B
- [ ] Tests pass

## Files to Modify
- `src/components/Button.tsx`
- `src/components/Button.test.tsx`
```

**Deliverable**: `context.md` with minimal requirements.

---

### Phase 2: Direct Implementation
**Objective**: Implement solution with test coverage.

**Process**:
1. Write test first (even on fast-track)
2. Implement feature
3. Verify tests pass
4. Quick refactor if needed

**Example**:
```typescript
// Button.test.tsx
it('should render with custom className', () => {
  render(<Button className="custom" />);
  expect(screen.getByRole('button')).toHaveClass('custom');
});

// Button.tsx
export function Button({ className, ...props }) {
  return <button className={cn('btn', className)} {...props} />;
}
```

---

### Phase 3: Validation
**Objective**: Ensure quality before considering done.

**Checklist**:
- [ ] All tests pass
- [ ] No linting errors (`npm run lint`)
- [ ] No type errors (`npm run typecheck`)
- [ ] Feature works in dev environment
- [ ] No console errors

---

## Phase Templates

### Spec Template
```markdown
# Specification: [Feature Name]

## Overview
[What and why]

## Requirements
1. [REQ-001] [Description]

## Interface
\`\`\`typescript
[Type definitions]
\`\`\`

## Acceptance Criteria
- [ ] [Criterion]
```

### Plan Template
```markdown
# Implementation Plan: [Feature Name]

## Approach
[High-level strategy]

## Components
1. [Component] - [Purpose]

## Files
\`\`\`
[Structure]
\`\`\`

## Tests
[Strategy]
```

### Context Template (Fast-Track)
```markdown
# Task: [Name]

## Goal
[One sentence]

## Requirements
- [Bullet points]

## Acceptance
- [ ] [Criteria]
```

## Decision Framework

### When to Use Standard Track
- Complex business logic
- Multiple components affected
- Unclear requirements
- High risk of errors
- Team collaboration needed

### When to Use Fast-Track
- Simple bug fix
- Well-understood change
- Single file modification
- Low complexity
- Clear requirements

### Red Flags Requiring Standard Track
🚩 "Add a feature to..." (vague)
🚩 Multiple system interactions
🚩 No existing tests
🚩 Unfamiliar codebase
🚩 Security implications

### Green Lights for Fast-Track
✅ "Change button color"
✅ "Fix typo in validation message"
✅ "Add className prop"
✅ Well-defined scope
✅ Obvious implementation

## Quality Gates

### Before Implementation
Questions to ask:
- ✓ Do I have a clear test requirement?
- ✓ Is the interface defined?
- ✓ Are acceptance criteria specific?
- ✓ Do I understand the "done" state?

If any answer is "no" → Back to specification phase

### After Implementation
Mandatory checks:
```bash
# All must pass
npm run test        # or: pytest, go test
npm run lint        # or: ruff, golangci-lint
npm run typecheck   # or: mypy, go build
```

Additional verification:
- ✓ Coverage > 90% for new code
- ✓ No skipped tests
- ✓ No TODO comments without issue links
- ✓ Documentation updated (if public API)

### Definition of Done
A task is done when:
1. All tests pass (including new tests)
2. Linter passes with 0 errors
3. Type checker passes with 0 errors
4. Code review completed (if applicable)
5. Acceptance criteria met
6. Specification updated (if requirements changed)

---

## Anti-Patterns to Avoid

### ❌ Specification After Implementation
Writing spec.md after code is already written defeats the purpose.

### ❌ Skipping Tests for "Speed"
Tests ARE the evaluation metric. No tests = incomplete work.

### ❌ Loading Entire Files Unnecessarily
Use grep/search first, then targeted reads.

### ❌ Inventing New Patterns
Follow existing project patterns. Consistency > Novelty.

### ❌ Premature Optimization
Make it work, make it right, then make it fast (if needed).

---

## Success Metrics

Track these for continuous improvement:
- Test coverage percentage
- Lint error count (should be 0)
- Type error count (should be 0)
- Time from spec to green tests
- Defect rate in production

Remember: **The Prompt is a Downstream Artifact of the Specification**
If it's not in the spec, it shouldn't be in the code.