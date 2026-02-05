# S.L.A.T.E. Methodology - Practical Examples

## Table of Contents
1. [Complete Feature Example](#complete-feature-example)
2. [Fast-Track Example](#fast-track-example)
3. [Context Loading Patterns](#context-loading-patterns)
4. [TDD Examples](#tdd-examples)
5. [Common Scenarios](#common-scenarios)

## Complete Feature Example

### Scenario: Add User Authentication to Existing App

#### Phase 0: Constitution
```bash
# Search for project conventions
cat CLAUDE.md
# → Found: "Use Hexagonal Architecture, TypeScript, Jest for testing"

# Check existing patterns
grep -r "class.*Service" src/
# → Found pattern: Services use dependency injection

# Check test setup
cat jest.config.js
# → Found: Tests in __tests__ folders, use .test.ts suffix

# Check linting
cat .eslintrc.json
# → Found: ESLint with TypeScript, Prettier integration
```

**Constitution Summary**:
- Architecture: Hexagonal
- Language: TypeScript
- Testing: Jest, >90% coverage required
- Style: ESLint + Prettier, functional components
- DI: Constructor injection pattern

---

#### Phase 1: Specification (`spec.md`)

```markdown
# Specification: User Authentication

## Overview
Implement JWT-based authentication allowing users to register, login, and access protected resources.

## Functional Requirements
1. [REQ-001] Users can register with email and password
2. [REQ-002] Users can login with valid credentials
3. [REQ-003] System returns JWT token on successful authentication
4. [REQ-004] Protected endpoints require valid JWT token
5. [REQ-005] Tokens expire after 24 hours

## Non-Functional Requirements
- Performance: Authentication check < 50ms
- Security: Passwords hashed with bcrypt (cost factor 10)
- Reliability: Token validation must be stateless

## API Contract

### Registration
\`\`\`typescript
POST /api/auth/register
Request:
{
  email: string;
  password: string;
  name: string;
}

Response (201):
{
  userId: string;
  token: string;
  expiresAt: string; // ISO 8601
}

Errors:
400 - Invalid email format
400 - Password too weak
409 - Email already registered
```

### Login
```typescript
POST /api/auth/login
Request:
{
  email: string;
  password: string;
}

Response (200):
{
  userId: string;
  token: string;
  expiresAt: string;
}

Errors:
400 - Missing credentials
401 - Invalid credentials
```

## Data Models

```typescript
// Domain Entity
class User {
  id: UserId;
  email: Email;
  passwordHash: PasswordHash;
  name: string;
  createdAt: Date;
}

// Value Objects
class Email {
  value: string; // validated format
}

class PasswordHash {
  hash: string;
  verify(plaintext: string): Promise<boolean>;
}

// Authentication Token
interface AuthToken {
  userId: string;
  issuedAt: Date;
  expiresAt: Date;
}
```

## Business Rules
1. Email must be valid RFC 5322 format
2. Email must be unique across all users
3. Password must be:
   - At least 8 characters
   - Contain uppercase and lowercase
   - Contain at least one number
4. Token expiry is exactly 24 hours from issuance
5. Password verification limited to 3 attempts per minute per user

## Acceptance Criteria
- [ ] User can register with valid email/password/name
- [ ] System rejects registration with existing email
- [ ] System rejects weak passwords
- [ ] User can login with correct credentials
- [ ] User cannot login with wrong password
- [ ] Protected endpoint rejects request without token
- [ ] Protected endpoint rejects expired token
- [ ] Protected endpoint accepts valid token

## Out of Scope
- Email verification
- Password reset flow
- OAuth/social login
- Multi-factor authentication
- Refresh tokens
```

---

#### Phase 2: Planning (`plan.md`)

```markdown
# Implementation Plan: User Authentication

## Architecture Decision
**Pattern**: Hexagonal Architecture (aligns with existing codebase)
**Rationale**: 
- Isolate authentication logic from framework
- Enable testing without HTTP layer
- Allow swapping JWT library if needed

## Component Breakdown

### 1. Domain Layer (Pure Business Logic)
**Files to create**:
- `src/domain/entities/User.ts` - User entity
- `src/domain/value-objects/Email.ts` - Email validation
- `src/domain/value-objects/PasswordHash.ts` - Password hashing
- `src/domain/value-objects/UserId.ts` - User identifier

**Responsibilities**:
- Email format validation
- Password strength validation
- Password hashing/verification
- User creation logic

### 2. Application Layer (Use Cases)
**Files to create**:
- `src/application/ports/inbound/RegisterUserUseCase.ts`
- `src/application/ports/inbound/LoginUserUseCase.ts`
- `src/application/ports/outbound/UserRepository.ts`
- `src/application/ports/outbound/TokenGenerator.ts`
- `src/application/services/RegisterUserService.ts`
- `src/application/services/LoginUserService.ts`

**Responsibilities**:
- Orchestrate domain logic
- Enforce business rules
- Coordinate with repositories and services

### 3. Infrastructure Layer (Adapters)
**Files to create**:
- `src/infrastructure/adapters/inbound/AuthController.ts`
- `src/infrastructure/adapters/inbound/AuthMiddleware.ts`
- `src/infrastructure/adapters/outbound/PostgresUserRepository.ts`
- `src/infrastructure/adapters/outbound/JwtTokenGenerator.ts`

**Files to modify**:
- `src/infrastructure/config/routes.ts` - Add auth routes
- `src/infrastructure/config/di-container.ts` - Register dependencies

**Responsibilities**:
- HTTP request/response handling
- JWT token generation/validation
- Database persistence
- Dependency injection setup

## Dependencies

**New**:
- `bcrypt@^5.1.0` - Password hashing
- `jsonwebtoken@^9.0.0` - JWT generation/validation
- `validator@^13.9.0` - Email validation

**Existing** (no changes):
- `express@^4.18.0`
- `pg@^8.11.0`
- `inversify@^6.0.0`

## Database Schema

\`\`\`sql
-- Migration: 20240205_create_users_table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();
\`\`\`

## Test Strategy

### Unit Tests (Domain Layer)
- Email validation logic
- Password strength validation
- Password hashing/verification
- User entity creation

**Coverage Target**: 100%

### Integration Tests (Application Layer)
- RegisterUserService with in-memory repository
- LoginUserService with fake token generator
- Error handling flows

**Coverage Target**: >95%

### E2E Tests (Infrastructure Layer)
- POST /api/auth/register with real HTTP
- POST /api/auth/login with real HTTP
- Protected endpoint with middleware

**Coverage Target**: >90%

## Implementation Order

1. **Value Objects** (No dependencies)
   - Email
   - PasswordHash
   - UserId

2. **Domain Entity** (Depends on VOs)
   - User

3. **Port Interfaces** (Define contracts)
   - All inbound and outbound ports

4. **Application Services** (Business logic)
   - RegisterUserService
   - LoginUserService

5. **Outbound Adapters** (Infrastructure)
   - PostgresUserRepository
   - JwtTokenGenerator

6. **Inbound Adapters** (HTTP layer)
   - AuthController
   - AuthMiddleware

7. **Integration** (Wire it all up)
   - DI container configuration
   - Route registration

8. **Testing** (Throughout)
   - Unit tests alongside each component
   - Integration tests after services
   - E2E tests at the end

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| JWT secret exposure | High | Store in environment variable, never commit |
| Password hash timing attack | Medium | Use constant-time comparison |
| Rate limiting bypass | Medium | Implement IP-based rate limiter |
| Token replay attack | Low | Tokens are stateless, use short expiry |

## Rollout Plan

1. Feature flag: `AUTH_ENABLED=false` initially
2. Deploy with flag off
3. Run smoke tests in production
4. Enable for internal users first
5. Monitor error rates
6. Enable for all users
```

---

#### Phase 3: Analysis

**Search Results**:
```bash
# Check for existing auth code
grep -r "auth" src/
# → No results, clean slate

# Check for existing User model
grep -r "class User" src/
# → No results, safe to create

# Find similar services for pattern matching
grep -r "class.*Service.*implements" src/application/services/
# → Found: CreateOrderService pattern to follow

# Check DI container pattern
cat src/infrastructure/config/di-container.ts
# → Found: Using inversify, register pattern established
```

**Files to Create** (15 new files):
- 4 domain files
- 6 application files
- 4 infrastructure files
- 1 migration file

**Files to Modify** (2 existing files):
- `src/infrastructure/config/routes.ts`
- `src/infrastructure/config/di-container.ts`

**Dependencies**:
- Order: Value Objects → Entity → Ports → Services → Adapters

---

#### Phase 4: Task Breakdown

```markdown
## Task 1: Create Email Value Object
**Test Requirements**:
- [ ] Unit: Valid email accepted
- [ ] Unit: Invalid email rejected
- [ ] Unit: Email equality works

**Acceptance**:
- [ ] Email class with validation
- [ ] All tests pass

**Dependencies**: None
**Complexity**: Low

---

## Task 2: Create PasswordHash Value Object
**Test Requirements**:
- [ ] Unit: Password hashing works
- [ ] Unit: Password verification works
- [ ] Unit: Wrong password rejected

**Acceptance**:
- [ ] PasswordHash class with bcrypt
- [ ] All tests pass

**Dependencies**: None
**Complexity**: Low

---

## Task 3: Create UserId Value Object
**Test Requirements**:
- [ ] Unit: UUID generation works
- [ ] Unit: UUID validation works
- [ ] Unit: Equality comparison works

**Acceptance**:
- [ ] UserId class
- [ ] All tests pass

**Dependencies**: None
**Complexity**: Low

---

## Task 4: Create User Entity
**Test Requirements**:
- [ ] Unit: User creation with valid data
- [ ] Unit: User creation rejects invalid email
- [ ] Unit: User creation rejects weak password

**Acceptance**:
- [ ] User class with factory method
- [ ] Validation using VOs
- [ ] All tests pass

**Dependencies**: Tasks 1, 2, 3
**Complexity**: Medium

---

## Task 5: Define Port Interfaces
**Test Requirements**:
- N/A (interfaces only)

**Acceptance**:
- [ ] RegisterUserUseCase interface
- [ ] LoginUserUseCase interface
- [ ] UserRepository interface
- [ ] TokenGenerator interface
- [ ] No implementation, just types

**Dependencies**: Task 4
**Complexity**: Low

---

## Task 6: Implement RegisterUserService
**Test Requirements**:
- [ ] Integration: Successful registration
- [ ] Integration: Duplicate email rejected
- [ ] Integration: Weak password rejected

**Acceptance**:
- [ ] Service implements RegisterUserUseCase
- [ ] Uses UserRepository and TokenGenerator ports
- [ ] All tests pass with fake adapters

**Dependencies**: Tasks 4, 5
**Complexity**: High

---

## Task 7: Implement LoginUserService
**Test Requirements**:
- [ ] Integration: Successful login
- [ ] Integration: Wrong password rejected
- [ ] Integration: Non-existent user rejected

**Acceptance**:
- [ ] Service implements LoginUserUseCase
- [ ] All tests pass with fake adapters

**Dependencies**: Tasks 4, 5
**Complexity**: High

---

## Task 8: Implement PostgresUserRepository
**Test Requirements**:
- [ ] Integration: Save user to database
- [ ] Integration: Find user by email
- [ ] Integration: Duplicate email throws error

**Acceptance**:
- [ ] Repository implements UserRepository
- [ ] Uses pg connection pool
- [ ] All tests pass with test database

**Dependencies**: Tasks 4, 5
**Complexity**: Medium

---

## Task 9: Implement JwtTokenGenerator
**Test Requirements**:
- [ ] Unit: Token generation works
- [ ] Unit: Token validation works
- [ ] Unit: Expired token rejected

**Acceptance**:
- [ ] Generator implements TokenGenerator
- [ ] Uses jsonwebtoken library
- [ ] All tests pass

**Dependencies**: Task 5
**Complexity**: Medium

---

## Task 10: Implement AuthController
**Test Requirements**:
- [ ] E2E: POST /register returns 201
- [ ] E2E: POST /register returns 409 for duplicate
- [ ] E2E: POST /login returns 200
- [ ] E2E: POST /login returns 401 for wrong password

**Acceptance**:
- [ ] Controller with register and login endpoints
- [ ] Proper error handling
- [ ] All E2E tests pass

**Dependencies**: Tasks 6, 7
**Complexity**: Medium

---

## Task 11: Implement AuthMiddleware
**Test Requirements**:
- [ ] E2E: Protected route rejects no token
- [ ] E2E: Protected route rejects invalid token
- [ ] E2E: Protected route accepts valid token

**Acceptance**:
- [ ] Middleware validates JWT
- [ ] Attaches user to request
- [ ] All tests pass

**Dependencies**: Task 9
**Complexity**: Medium

---

## Task 12: Configure Dependency Injection
**Test Requirements**:
- [ ] E2E: Full auth flow works end-to-end

**Acceptance**:
- [ ] All services registered in container
- [ ] Routes configured
- [ ] Full system integration works

**Dependencies**: Tasks 8, 9, 10, 11
**Complexity**: Low
```

---

#### Phase 5: Implementation (Example for Task 1)

**TDD Cycle**:

**1. RED - Write Test**
```typescript
// src/domain/value-objects/__tests__/Email.test.ts
import { Email } from '../Email';

describe('Email', () => {
  describe('create', () => {
    it('should accept valid email format', () => {
      expect(() => Email.create('user@example.com')).not.toThrow();
    });

    it('should reject invalid email format', () => {
      expect(() => Email.create('invalid-email')).toThrow('Invalid email format');
    });

    it('should reject empty email', () => {
      expect(() => Email.create('')).toThrow('Email cannot be empty');
    });
  });

  describe('equals', () => {
    it('should return true for same email', () => {
      const email1 = Email.create('user@example.com');
      const email2 = Email.create('user@example.com');
      expect(email1.equals(email2)).toBe(true);
    });

    it('should return false for different emails', () => {
      const email1 = Email.create('user1@example.com');
      const email2 = Email.create('user2@example.com');
      expect(email1.equals(email2)).toBe(false);
    });
  });

  describe('getValue', () => {
    it('should return email string', () => {
      const email = Email.create('user@example.com');
      expect(email.getValue()).toBe('user@example.com');
    });
  });
});
```

Run: `npm test` → **FAILS** (Email class doesn't exist)

**2. GREEN - Minimal Implementation**
```typescript
// src/domain/value-objects/Email.ts
import validator from 'validator';

export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    if (!email || email.trim().length === 0) {
      throw new Error('Email cannot be empty');
    }

    if (!validator.isEmail(email)) {
      throw new Error('Invalid email format');
    }

    return new Email(email.toLowerCase());
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }

  getValue(): string {
    return this.value;
  }
}
```

Run: `npm test` → **PASSES** ✅

**3. REFACTOR - Improve**
```typescript
// src/domain/value-objects/Email.ts (refactored)
import validator from 'validator';

export class Email {
  private constructor(private readonly value: string) {}

  static create(email: string): Email {
    Email.validate(email);
    return new Email(email.toLowerCase().trim());
  }

  private static validate(email: string): void {
    if (!email || email.trim().length === 0) {
      throw new Error('Email cannot be empty');
    }

    if (!validator.isEmail(email)) {
      throw new Error('Invalid email format');
    }
  }

  equals(other: Email): boolean {
    if (!(other instanceof Email)) {
      return false;
    }
    return this.value === other.value;
  }

  getValue(): string {
    return this.value;
  }

  toString(): string {
    return this.value;
  }
}
```

Run: `npm test` → **PASSES** ✅

**4. Quality Checks**
```bash
npm run lint       # → PASSES ✅
npm run typecheck  # → PASSES ✅
```

**5. Commit**
```bash
git add src/domain/value-objects/Email.ts
git add src/domain/value-objects/__tests__/Email.test.ts
git commit -m "feat: add Email value object with validation

- Validates email format using validator library
- Case-insensitive comparison
- 100% test coverage"
```

✅ **Task 1 Complete** → Move to Task 2

---

## Fast-Track Example

### Scenario: Add className Prop to Existing Button Component

#### Phase 1: Context Document

```markdown
# Task: Add className prop to Button component

## Goal
Allow consumers to pass custom CSS classes to Button component for styling flexibility.

## Requirements
- Button accepts optional `className` prop
- Custom className is merged with existing button classes
- Existing button styling is preserved
- TypeScript types updated

## Acceptance Criteria
- [ ] Button renders with custom className
- [ ] Existing button classes still applied
- [ ] TypeScript compilation succeeds
- [ ] Tests pass

## Files to Modify
- `src/components/Button.tsx`
- `src/components/__tests__/Button.test.tsx`
```

#### Phase 2: Implementation

**1. Write Test**
```typescript
// src/components/__tests__/Button.test.tsx
it('should render with custom className', () => {
  render(<Button className="custom-class">Click me</Button>);
  const button = screen.getByRole('button');
  expect(button).toHaveClass('btn');  // existing class
  expect(button).toHaveClass('custom-class');  // new class
});
```

**2. Implement**
```typescript
// src/components/Button.tsx
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  className?: string;  // ← Added
  children: React.ReactNode;
}

export function Button({ 
  variant = 'primary', 
  className,  // ← Added
  children, 
  ...props 
}: ButtonProps) {
  return (
    <button
      className={cn(
        'btn',
        variant === 'primary' ? 'btn-primary' : 'btn-secondary',
        className  // ← Added - merges custom classes
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

#### Phase 3: Validation

```bash
npm test           # ✅ All tests pass
npm run lint       # ✅ No linting errors
npm run typecheck  # ✅ No type errors
npm run dev        # ✅ Component renders correctly
```

**Total time**: ~5 minutes
**Lines changed**: 5
**Tests added**: 1

---

## Context Loading Patterns

### Pattern 1: Constitution Discovery
```bash
# Find project documentation
find . -maxdepth 2 -name "*.md" | grep -iE "(claude|project|readme|contributing)"

# Check for cursor rules
cat .cursorrules 2>/dev/null || echo "No .cursorrules found"

# Find package manager
ls package.json 2>/dev/null && echo "Node.js project" ||
ls requirements.txt 2>/dev/null && echo "Python project" ||
ls go.mod 2>/dev/null && echo "Go project"
```

### Pattern 2: Pattern Discovery
```bash
# Find service pattern
find src -name "*Service.ts" | head -3 | xargs grep -l "class"

# Find repository pattern  
find src -name "*Repository.ts" | head -1 | xargs cat

# Find test pattern
find src -name "*.test.ts" -o -name "*.spec.ts" | head -1 | xargs head -20
```

### Pattern 3: Dependency Analysis
```bash
# Check what's already installed
cat package.json | jq '.dependencies'

# Find usage of a library
grep -r "from 'react'" src/ | wc -l
```

---

## TDD Examples

### Example 1: Value Object
```typescript
// Test
describe('Money', () => {
  it('should add two amounts in same currency', () => {
    const m1 = Money.create(10, 'USD');
    const m2 = Money.create(20, 'USD');
    expect(m1.add(m2)).toEqual(Money.create(30, 'USD'));
  });

  it('should throw when adding different currencies', () => {
    const m1 = Money.create(10, 'USD');
    const m2 = Money.create(20, 'EUR');
    expect(() => m1.add(m2)).toThrow('Cannot add different currencies');
  });
});

// Implementation
class Money {
  constructor(
    private amount: number,
    private currency: string
  ) {}

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }
}
```

### Example 2: Service
```typescript
// Test
describe('CreateOrderService', () => {
  let service: CreateOrderService;
  let mockRepository: jest.Mocked<OrderRepository>;

  beforeEach(() => {
    mockRepository = {
      save: jest.fn(),
      findById: jest.fn(),
    };
    service = new CreateOrderService(mockRepository);
  });

  it('should create order and save to repository', async () => {
    const request = {
      customerId: 'customer-1',
      items: [{ productId: 'p1', quantity: 2, price: 10 }],
    };

    await service.execute(request);

    expect(mockRepository.save).toHaveBeenCalledWith(
      expect.objectContaining({
        customerId: 'customer-1',
      })
    );
  });
});

// Implementation
class CreateOrderService {
  constructor(private repository: OrderRepository) {}

  async execute(request: CreateOrderRequest): Promise<void> {
    const order = Order.create(request.customerId, request.items);
    await this.repository.save(order);
  }
}
```

---

## Common Scenarios

### Scenario: Bug Fix
```markdown
# Context: Fix validation bug

## Goal
Fix bug where phone number validation accepts invalid formats

## Current Behavior
Phone number "123" is accepted (invalid)

## Expected Behavior
Phone number must be exactly 10 digits

## Root Cause
Regex pattern missing length check

## Fix
Update regex from /^\d+$/ to /^\d{10}$/

## Test
- [ ] Valid 10-digit number accepted
- [ ] 9-digit number rejected
- [ ] 11-digit number rejected
```

### Scenario: Refactoring
```markdown
# Context: Extract duplicate validation logic

## Goal
DRY up validation code duplicated across 3 files

## Approach
Create shared ValidationService

## Files Affected
- src/validators/ValidationService.ts (new)
- src/services/UserService.ts (modify)
- src/services/OrderService.ts (modify)
- src/services/ProductService.ts (modify)

## Tests
- [ ] All existing tests still pass
- [ ] New ValidationService has unit tests
```

### Scenario: New Feature (Small)
Use Fast-Track:
```markdown
# Task: Add sorting to product list

## Requirements
- Sort by price (ascending/descending)
- Sort by name (A-Z, Z-A)
- Default sort by name ascending

## Implementation
Add `sortBy` and `sortOrder` query params

## Tests
- [ ] Default sort works
- [ ] All sort combinations work
```

### Scenario: New Feature (Large)
Use Standard Track with full spec.md and plan.md