---
name: tdd-implementation
description: Apply Test-Driven Development methodology for implementing features with high quality. Use when implementing new features, fixing bugs, or refactoring code with test coverage requirements.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Test-Driven Development (TDD)

**Version**: 2.0  
**Origin**: Overwatch Agent Network - Feature-Centric TDD

## When to Use

- Implementing new features
- Fixing bugs (write test that reproduces bug first)
- Refactoring existing code
- When test coverage requirements exist
- Building reliable, maintainable software

## Core Philosophy

> "Tests are the evaluation metric."
> If you can't test it, you can't verify it works.

## The TDD Cycle

```
        ┌──────────────┐
        │     RED      │
        │ Write Failing│
        │    Test      │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │    GREEN     │
        │ Make It Pass │
        │   Minimal    │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │   REFACTOR   │
        │   Improve    │
        │  Structure   │
        └──────┬───────┘
               │
               └────────► Repeat
```

## Feature-Centric TDD Algorithm

```python
def implement_feature(feature_spec):
    # 1. Red Phase (The Validator)
    test_case = create_failing_test(feature_spec)
    assert run_test(test_case) == FAIL  # MUST fail first
    
    # 2. Green Phase (The Generator)
    code = generate_minimal_code(feature_spec)
    assert run_test(test_case) == PASS  # Just enough to pass
    
    # 3. Refactor Phase (The Optimizer)
    code = optimize_structure(code)
    assert run_test(test_case) == PASS  # Must still pass
```

## Coverage Targets

| Metric | Target | Minimum |
|--------|--------|---------|
| Statements | 90% | 80% |
| Branches | 85% | 75% |
| Functions | 95% | 90% |
| Lines | 90% | 80% |

## Step-by-Step Process

### Phase 1: RED - Write Failing Test

**Purpose**: Define expected behavior before implementation

```typescript
// test/user.service.test.ts
import { UserService } from '../src/user.service';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  describe('createUser', () => {
    it('should create a user with valid email', async () => {
      const result = await service.createUser({
        email: 'test@example.com',
        name: 'Test User'
      });

      expect(result).toMatchObject({
        id: expect.any(String),
        email: 'test@example.com',
        name: 'Test User',
        createdAt: expect.any(Date)
      });
    });

    it('should throw error for invalid email', async () => {
      await expect(
        service.createUser({ email: 'invalid', name: 'Test' })
      ).rejects.toThrow('Invalid email format');
    });

    it('should throw error for duplicate email', async () => {
      await service.createUser({ email: 'test@example.com', name: 'User 1' });
      
      await expect(
        service.createUser({ email: 'test@example.com', name: 'User 2' })
      ).rejects.toThrow('Email already exists');
    });
  });
});
```

Run and verify failure:

```bash
# Run the test - MUST fail
npm test -- user.service.test.ts

# Expected output:
# FAIL  test/user.service.test.ts
#   ● UserService › createUser › should create a user with valid email
#     Cannot find module '../src/user.service'
```

### Phase 2: GREEN - Make It Pass

**Purpose**: Write minimum code to pass the test

```typescript
// src/user.service.ts
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

export class UserService {
  private users: Map<string, User> = new Map();

  async createUser(dto: CreateUserDto): Promise<User> {
    // Validate email format
    if (!dto.email.includes('@') || !dto.email.includes('.')) {
      throw new Error('Invalid email format');
    }

    // Check for duplicate
    for (const user of this.users.values()) {
      if (user.email === dto.email) {
        throw new Error('Email already exists');
      }
    }

    const user: User = {
      id: crypto.randomUUID(),
      email: dto.email,
      name: dto.name,
      createdAt: new Date()
    };

    this.users.set(user.id, user);
    return user;
  }
}
```

Run and verify success:

```bash
# Run the test - MUST pass now
npm test -- user.service.test.ts

# Expected output:
# PASS  test/user.service.test.ts
#   UserService
#     createUser
#       ✓ should create a user with valid email (5 ms)
#       ✓ should throw error for invalid email (2 ms)
#       ✓ should throw error for duplicate email (1 ms)
```

### Phase 3: REFACTOR - Improve Structure

**Purpose**: Clean up code while keeping tests green

```typescript
// src/user.service.ts - Refactored
import { z } from 'zod';

const EmailSchema = z.string().email('Invalid email format');

const CreateUserSchema = z.object({
  email: EmailSchema,
  name: z.string().min(1, 'Name is required')
});

interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

type CreateUserDto = z.infer<typeof CreateUserSchema>;

export class UserService {
  private users: Map<string, User> = new Map();

  async createUser(dto: CreateUserDto): Promise<User> {
    // Validate with schema
    const validated = CreateUserSchema.parse(dto);

    // Check for duplicate
    if (this.findByEmail(validated.email)) {
      throw new Error('Email already exists');
    }

    const user = this.buildUser(validated);
    this.users.set(user.id, user);
    return user;
  }

  private findByEmail(email: string): User | undefined {
    return Array.from(this.users.values())
      .find(u => u.email === email);
  }

  private buildUser(dto: CreateUserDto): User {
    return {
      id: crypto.randomUUID(),
      email: dto.email,
      name: dto.name,
      createdAt: new Date()
    };
  }
}
```

Verify tests still pass:

```bash
# Run tests after refactor - MUST still pass
npm test -- user.service.test.ts

# Check coverage
npm test -- --coverage user.service.test.ts
```

## Test Types Hierarchy

```
                    ┌─────────────────┐
                    │    E2E Tests    │  Slow, Expensive
                    │   (Few tests)   │  Full system
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │ Integration     │  Medium speed
                    │ Tests           │  Real dependencies
                    └────────┬────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │         Unit Tests                   │  Fast, Cheap
          │         (Many tests)                 │  Isolated
          └──────────────────────────────────────┘
```

### Unit Test Example

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = {
      findByEmail: jest.fn(),
      save: jest.fn()
    };
    service = new UserService(mockRepository);
  });

  it('creates user when email is unique', async () => {
    mockRepository.findByEmail.mockResolvedValue(null);
    mockRepository.save.mockImplementation(async (u) => u);

    const result = await service.createUser({
      email: 'test@example.com',
      name: 'Test'
    });

    expect(mockRepository.findByEmail).toHaveBeenCalledWith('test@example.com');
    expect(mockRepository.save).toHaveBeenCalled();
    expect(result.email).toBe('test@example.com');
  });
});
```

### Integration Test Example

```typescript
describe('UserService Integration', () => {
  let service: UserService;
  let db: Database;

  beforeAll(async () => {
    db = await Database.connect(TEST_DATABASE_URL);
  });

  beforeEach(async () => {
    await db.query('DELETE FROM users');
    service = new UserService(new UserRepository(db));
  });

  afterAll(async () => {
    await db.disconnect();
  });

  it('persists user to database', async () => {
    const user = await service.createUser({
      email: 'test@example.com',
      name: 'Test'
    });

    const found = await db.query('SELECT * FROM users WHERE id = $1', [user.id]);
    expect(found.rows[0].email).toBe('test@example.com');
  });
});
```

### E2E Test Example

```typescript
describe('User API E2E', () => {
  let app: Express;

  beforeAll(async () => {
    app = await createApp();
  });

  it('POST /api/users creates user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      email: 'test@example.com'
    });
  });

  it('GET /api/users/:id returns user', async () => {
    // Create user first
    const created = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' });

    // Then fetch
    const response = await request(app)
      .get(`/api/users/${created.body.id}`)
      .expect(200);

    expect(response.body.email).toBe('test@example.com');
  });
});
```

## Bug Fix TDD

When fixing bugs, write the reproducing test first:

```bash
# 1. Reproduce bug with test
cat > test/bug-123.test.ts << 'EOF'
describe('Bug #123: User creation fails with + in email', () => {
  it('should accept email with + symbol', async () => {
    const result = await service.createUser({
      email: 'user+tag@example.com',
      name: 'Test'
    });
    expect(result.email).toBe('user+tag@example.com');
  });
});
EOF

# 2. Run test - should fail (proving bug exists)
npm test -- bug-123.test.ts

# 3. Fix the bug
# ... edit code ...

# 4. Run test - should pass (proving bug is fixed)
npm test -- bug-123.test.ts

# 5. Run all tests - should still pass (no regression)
npm test
```

## Test Quality Checklist

### Before Committing
- [ ] All tests pass locally
- [ ] Coverage meets targets
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests are fast (unit tests < 100ms each)
- [ ] Tests are isolated (no shared state)

### Test Naming Convention
```typescript
// Pattern: should_ExpectedBehavior_When_Condition
it('should return user when id exists', () => {});
it('should throw NotFoundError when id does not exist', () => {});
it('should create user when email is valid', () => {});
```

## Anti-Patterns

- ❌ Writing tests after implementation
- ❌ Testing implementation details, not behavior
- ❌ Skipping the RED phase
- ❌ Not refactoring after GREEN
- ❌ Flaky tests that sometimes pass/fail
- ❌ Tests that depend on execution order
- ❌ Mocking everything (test nothing real)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Test passes without implementation | Test is not specific enough |
| Test is flaky | Add proper async handling, avoid time-based tests |
| Can't test code | Refactor for testability (dependency injection) |
| Tests are slow | Move to unit tests, use mocks appropriately |
| Coverage low | Add edge case tests, test error paths |