---
name: hexagonal-architecture
description: Design systems using Hexagonal Architecture (Ports & Adapters) pattern. Use when building modular applications, designing clean boundaries between core logic and external services, or implementing dependency inversion for testability and flexibility.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Hexagonal Architecture (Ports & Adapters)

**Origin**: Overwatch Agent Network - ADR-006

## When to Use

- Designing systems with clean separation of concerns
- Building applications that need to swap external services
- Creating testable architectures with mockable dependencies
- Implementing dependency inversion principle at scale
- Multi-adapter systems (CLI, HTTP, WebSocket, etc.)

## Core Concept

```
┌─────────────────────────────────────────────────────────────────┐
│                         ADAPTERS (Outside)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ CLI Adapter │  │ HTTP Adapter│  │ WS Adapter  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
├─────────────────────────────────────────────────────────────────┤
│                          PORTS (Interface)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ InputPort   │  │ EventPort   │  │ CommandPort │              │
├─────────────────────────────────────────────────────────────────┤
│                     CORE DOMAIN (Inside)                         │
│         Business Logic • Entities • Use Cases • Rules            │
├─────────────────────────────────────────────────────────────────┤
│                          PORTS (Interface)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ StoragePort │  │ MessagingPort│ │ ExternalPort│              │
├─────────────────────────────────────────────────────────────────┤
│                         ADAPTERS (Outside)                       │
│  │ PostgreSQL  │  │ RabbitMQ    │  │ Stripe API  │              │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### Ports (Interfaces)

Ports define the contract between core domain and outside world:

```typescript
// Inbound Port - How outside world interacts with core
interface UserServicePort {
  createUser(data: CreateUserDTO): Promise<User>;
  getUser(id: string): Promise<User | null>;
  updateUser(id: string, data: UpdateUserDTO): Promise<User>;
  deleteUser(id: string): Promise<void>;
}

// Outbound Port - What core needs from outside world
interface UserRepositoryPort {
  save(user: User): Promise<User>;
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  delete(id: string): Promise<void>;
}

interface NotificationPort {
  sendWelcomeEmail(user: User): Promise<void>;
  sendPasswordReset(user: User, token: string): Promise<void>;
}
```

### Adapters (Implementations)

Adapters implement ports for specific technologies:

```typescript
// Inbound Adapter - HTTP
class UserHttpAdapter {
  constructor(private userService: UserServicePort) {}

  async handleCreateUser(req: Request, res: Response) {
    const user = await this.userService.createUser(req.body);
    res.status(201).json(user);
  }
}

// Outbound Adapter - Database
class PostgresUserRepository implements UserRepositoryPort {
  constructor(private db: Database) {}

  async save(user: User): Promise<User> {
    const result = await this.db.query(
      'INSERT INTO users (id, name, email) VALUES ($1, $2, $3) RETURNING *',
      [user.id, user.name, user.email]
    );
    return this.mapToUser(result.rows[0]);
  }
}

// Outbound Adapter - Email Service
class SendGridNotificationAdapter implements NotificationPort {
  constructor(private sendgrid: SendGridClient) {}

  async sendWelcomeEmail(user: User): Promise<void> {
    await this.sendgrid.send({
      to: user.email,
      template: 'welcome',
      data: { name: user.name }
    });
  }
}
```

### Core Domain

Core domain contains business logic with no external dependencies:

```typescript
// Core Entity
class User {
  constructor(
    public readonly id: string,
    public name: string,
    public email: string,
    private passwordHash: string
  ) {}

  verifyPassword(password: string): boolean {
    return bcrypt.compareSync(password, this.passwordHash);
  }

  updateEmail(newEmail: string): void {
    if (!this.isValidEmail(newEmail)) {
      throw new InvalidEmailError(newEmail);
    }
    this.email = newEmail;
  }
}

// Use Case (Application Service)
class CreateUserUseCase implements UserServicePort {
  constructor(
    private userRepo: UserRepositoryPort,
    private notifications: NotificationPort
  ) {}

  async createUser(data: CreateUserDTO): Promise<User> {
    const existing = await this.userRepo.findByEmail(data.email);
    if (existing) {
      throw new UserAlreadyExistsError(data.email);
    }

    const user = new User(
      generateId(),
      data.name,
      data.email,
      hashPassword(data.password)
    );

    await this.userRepo.save(user);
    await this.notifications.sendWelcomeEmail(user);

    return user;
  }
}
```

## Directory Structure

```
src/
├── core/                    # Domain Layer (no external deps)
│   ├── entities/
│   │   └── user.ts
│   ├── use-cases/
│   │   └── create-user.ts
│   ├── ports/
│   │   ├── inbound/
│   │   │   └── user-service.port.ts
│   │   └── outbound/
│   │       ├── user-repository.port.ts
│   │       └── notification.port.ts
│   └── errors/
│       └── domain-errors.ts
├── adapters/                # Infrastructure Layer
│   ├── inbound/
│   │   ├── http/
│   │   │   └── user.controller.ts
│   │   ├── cli/
│   │   │   └── user.command.ts
│   │   └── websocket/
│   │       └── user.handler.ts
│   └── outbound/
│       ├── database/
│       │   └── postgres-user.repository.ts
│       ├── messaging/
│       │   └── rabbitmq.adapter.ts
│       └── email/
│           └── sendgrid.adapter.ts
└── config/
    └── dependency-injection.ts
```

## Dependency Injection

Wire everything together at composition root:

```typescript
// config/dependency-injection.ts
function createContainer() {
  // Outbound Adapters
  const db = new PostgresConnection(config.database);
  const userRepo = new PostgresUserRepository(db);
  const notifications = new SendGridNotificationAdapter(config.sendgrid);

  // Core Use Cases
  const userService = new CreateUserUseCase(userRepo, notifications);

  // Inbound Adapters
  const httpAdapter = new UserHttpAdapter(userService);
  const cliAdapter = new UserCliAdapter(userService);

  return {
    httpAdapter,
    cliAdapter,
    userService
  };
}
```

## Testing Strategy

Hexagonal architecture enables easy testing:

```typescript
// Unit Test - Mock outbound ports
describe('CreateUserUseCase', () => {
  let userRepo: MockUserRepository;
  let notifications: MockNotificationPort;
  let useCase: CreateUserUseCase;

  beforeEach(() => {
    userRepo = new MockUserRepository();
    notifications = new MockNotificationPort();
    useCase = new CreateUserUseCase(userRepo, notifications);
  });

  it('creates user and sends welcome email', async () => {
    const user = await useCase.createUser({
      name: 'John',
      email: 'john@example.com',
      password: 'secret123'
    });

    expect(user.name).toBe('John');
    expect(userRepo.savedUsers).toHaveLength(1);
    expect(notifications.sentEmails).toHaveLength(1);
  });
});
```

## Key Ports for Agent Systems

| Port | Purpose | Adapters |
|------|---------|----------|
| `AgentPort` | Agent lifecycle | AgentManager, MockAgent |
| `MessagingPort` | Message send/receive | FileBus, BrokerBus, InMemoryBus |
| `WorkspacePort` | File CRUD | FileWorkspace, S3Workspace |
| `LLMPort` | LLM interactions | OpenRouter, Anthropic, MockLLM |
| `SandboxPort` | Sandbox management | E2BProvider, LocalProvider |
| `StoragePort` | Persistence | Postgres, SQLite, InMemory |

## Anti-Patterns

- ❌ Domain entities depending on adapters
- ❌ Business logic in adapters
- ❌ Leaking adapter types into core
- ❌ Direct database calls in use cases
- ❌ Skipping dependency injection

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Circular dependencies | Check port direction, separate concerns |
| Testing difficulty | Ensure all deps are injected via ports |
| Adapter bloat | Consider adapter-specific DTOs |
| Performance concerns | Cache at adapter level, not core |