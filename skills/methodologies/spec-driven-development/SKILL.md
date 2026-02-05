---
name: spec-driven-development
description: Apply Spec-Driven Development (SDD) methodology for requirements-first software development. Use when defining requirements, creating technical specifications, or ensuring traceability from requirements to implementation.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Spec-Driven Development (SDD)

**Version**: 2.0  
**Origin**: Overwatch Agent Network - Prompt Programming Framework

## When to Use

- Starting new projects or major features
- When requirements traceability is critical
- Building complex systems with multiple stakeholders
- Ensuring alignment between requirements and implementation
- Regulated environments requiring documentation

## Core Philosophy

> "The Specification is the Source of Truth."

All code is a downstream artifact of the specification. Changes flow from spec → plan → tasks → code, never the reverse.

## SDD Phases

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Requirements    →  Gather stakeholder needs       │
│  Phase 1: Specification   →  Define WHAT & WHY              │
│  Phase 2: Planning        →  Define HOW & WITH WHAT         │
│  Phase 3: Task Breakdown  →  Create testable work units     │
│  Phase 4: Implementation  →  TDD cycle with validation      │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### Phase 0: Requirements Gathering

Create a requirements document (`pm-docs/requirements.md`):

```markdown
# Requirements: [Project/Feature Name]

## Stakeholders
- Product Owner: [Name]
- Technical Lead: [Name]
- End Users: [Description]

## Business Context
[Why this feature/project exists]

## User Stories
1. As a [user type], I want [capability] so that [benefit]
2. As a [user type], I want [capability] so that [benefit]

## Functional Requirements
- FR-001: [Requirement description]
- FR-002: [Requirement description]

## Non-Functional Requirements
- NFR-001: Performance - Response time < 200ms
- NFR-002: Security - Authentication required
- NFR-003: Availability - 99.9% uptime

## Constraints
- Must integrate with existing auth system
- Must support mobile devices
- Budget: [if applicable]

## Out of Scope
- [What is explicitly NOT included]
```

### Phase 1: Specification

Create a specification document (`spec.md`):

```markdown
# Specification: [Feature Name]

## Overview
[High-level description]

## Functional Specification

### FS-001: [Function Name]
**Requirement**: FR-001
**Description**: [What it does]
**Inputs**: 
  - `param1`: Type - Description
  - `param2`: Type - Description
**Outputs**:
  - `result`: Type - Description
**Preconditions**:
  - User must be authenticated
**Postconditions**:
  - Data is persisted
**Error Handling**:
  - InvalidInput → 400 Bad Request
  - NotFound → 404 Not Found

### FS-002: [Function Name]
...

## Data Specification

### Entity: User
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | string | unique, not null | User email |
| name | string | not null | Display name |

## Interface Specification

### API Endpoints
| Method | Path | Request | Response | Description |
|--------|------|---------|----------|-------------|
| GET | /api/users/:id | - | User | Get user by ID |
| POST | /api/users | CreateUserDto | User | Create user |

### Type Definitions
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

interface CreateUserDto {
  email: string;
  name: string;
}
```

## Acceptance Criteria
- [ ] AC-001: User can view their profile
- [ ] AC-002: Profile displays name and email
- [ ] AC-003: 404 returned for non-existent users
```

### Phase 2: Technical Planning

Create a plan document (`plan.md`):

```markdown
# Technical Plan: [Feature Name]

## Architecture Approach
[Describe the architectural approach]

## Technology Stack
- Runtime: Node.js 20
- Framework: Express/Fastify
- Database: PostgreSQL
- ORM: Prisma

## Component Design

### Component: UserService
**Responsibility**: User domain logic
**Dependencies**: 
  - DatabaseAdapter
  - CacheAdapter
**Interface**:
```typescript
interface UserService {
  getById(id: string): Promise<User | null>;
  create(dto: CreateUserDto): Promise<User>;
}
```

## File Structure
```
src/
├── domain/
│   └── user/
│       ├── user.entity.ts
│       ├── user.service.ts
│       └── user.repository.ts
├── api/
│   └── user/
│       ├── user.controller.ts
│       └── user.dto.ts
└── infrastructure/
    └── database/
        └── prisma.adapter.ts
```

## Dependencies to Add
| Package | Version | Purpose |
|---------|---------|---------|
| prisma | ^5.0.0 | ORM |
| zod | ^3.0.0 | Validation |

## Migration Plan
1. Add database migration
2. Deploy schema changes
3. Deploy application changes

## Risk Assessment
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking change | Low | High | Feature flag |
```

### Phase 3: Task Breakdown

Create a tasks document (`tasks.md`):

```markdown
# Tasks: [Feature Name]

## Task Tracking

### Task 1: Create User Entity
**Spec Reference**: DS-001 (User entity)
**Type**: Implementation
**Test Requirement**: 
  - Unit test for entity validation
**Files**:
  - CREATE: src/domain/user/user.entity.ts
  - CREATE: src/domain/user/user.entity.test.ts
**Acceptance**:
  - [ ] Entity exports User type
  - [ ] Validation rejects invalid email
  - [ ] Tests pass with >90% coverage

### Task 2: Implement UserRepository
**Spec Reference**: FS-001, FS-002
**Type**: Implementation
**Dependencies**: Task 1
**Test Requirement**:
  - Integration test with test database
**Files**:
  - CREATE: src/domain/user/user.repository.ts
  - CREATE: src/domain/user/user.repository.test.ts
**Acceptance**:
  - [ ] Repository implements interface
  - [ ] getById returns User or null
  - [ ] create persists user
  - [ ] Integration tests pass

### Task 3: Implement UserService
**Spec Reference**: FS-001, FS-002
**Type**: Implementation
**Dependencies**: Task 2
**Test Requirement**:
  - Unit test with mocked repository
**Files**:
  - CREATE: src/domain/user/user.service.ts
  - CREATE: src/domain/user/user.service.test.ts
**Acceptance**:
  - [ ] Service implements interface
  - [ ] Business logic validated
  - [ ] Unit tests pass

### Task 4: Create API Endpoint
**Spec Reference**: IS-001 (API Endpoints)
**Type**: Implementation
**Dependencies**: Task 3
**Test Requirement**:
  - E2E test for each endpoint
**Files**:
  - CREATE: src/api/user/user.controller.ts
  - CREATE: src/api/user/user.e2e.test.ts
**Acceptance**:
  - [ ] GET /api/users/:id works
  - [ ] POST /api/users works
  - [ ] E2E tests pass
```

### Phase 4: Implementation

Execute TDD loop for each task:

```bash
# 1. RED: Create failing test
cat > src/domain/user/user.entity.test.ts << 'EOF'
import { User, createUser } from './user.entity';

describe('User Entity', () => {
  it('creates valid user', () => {
    const user = createUser({ email: 'test@example.com', name: 'Test' });
    expect(user.id).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });

  it('rejects invalid email', () => {
    expect(() => createUser({ email: 'invalid', name: 'Test' }))
      .toThrow('Invalid email');
  });
});
EOF

# Run test - should fail
npm test -- user.entity.test.ts

# 2. GREEN: Implement minimal code
cat > src/domain/user/user.entity.ts << 'EOF'
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

export function createUser(dto: { email: string; name: string }): User {
  if (!dto.email.includes('@')) {
    throw new Error('Invalid email');
  }
  return {
    id: crypto.randomUUID(),
    email: dto.email,
    name: dto.name,
    createdAt: new Date(),
  };
}
EOF

# Run test - should pass
npm test -- user.entity.test.ts

# 3. REFACTOR: Improve structure
# ... make improvements while keeping tests green
```

## Validation Checklists

### Spec Validation (90% threshold)
- [ ] All requirements have unique IDs
- [ ] All functions have defined I/O
- [ ] All entities have schema
- [ ] All APIs have contracts
- [ ] Acceptance criteria are testable

### Plan Validation (85% threshold)
- [ ] Architecture approach documented
- [ ] Component responsibilities clear
- [ ] File structure defined
- [ ] Dependencies listed
- [ ] Risks assessed

### Tasks Validation (85% threshold)
- [ ] Each task references spec
- [ ] Each task has test requirement
- [ ] Dependencies explicit
- [ ] Acceptance criteria defined
- [ ] Files to modify listed

## Traceability Matrix

Maintain requirement → implementation mapping:

| Requirement | Specification | Task | Test | Status |
|-------------|---------------|------|------|--------|
| FR-001 | FS-001 | Task 1 | user.test.ts | ✅ |
| FR-002 | FS-002 | Task 2 | user.repo.test.ts | 🔄 |
| NFR-001 | PS-001 | Task 5 | perf.test.ts | ⏳ |

## Anti-Patterns

- ❌ Implementing before spec is approved
- ❌ Changing spec mid-implementation without formal process
- ❌ Skipping task breakdown for "simple" features
- ❌ Not maintaining traceability
- ❌ Writing tests after implementation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Unclear requirements | Return to Phase 0, clarify with stakeholders |
| Spec doesn't match needs | Formal change request process |
| Tasks too large | Break down further, max 4 hours per task |
| Tests hard to write | Review spec - if untestable, revise spec |