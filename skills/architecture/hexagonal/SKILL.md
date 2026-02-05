---
name: hexagonal-architecture
description: Apply hexagonal (ports and adapters) architecture pattern for building testable, maintainable systems. Use when designing applications that need to be independent of frameworks, databases, UI, or external agencies. Triggers include requests for clean architecture, DDD implementation, microservices design, testing-focused architecture, or when separating business logic from infrastructure concerns.
license: MIT
---

# Hexagonal Architecture (Ports and Adapters)

## Overview

Hexagonal Architecture (also known as Ports and Adapters) is an architectural pattern that creates loosely coupled application components that can be connected to their software environment through ports and adapters. This allows components to be tested in isolation and makes the application technology-agnostic.

## Core Architecture Layers

### 1. Domain Layer (Inner Hexagon)
The heart of the application containing pure business logic:
- **Entities**: Core business objects with identity (Order, Customer, Product)
- **Value Objects**: Immutable objects representing concepts (Money, Email, Address)
- **Domain Services**: Business logic that doesn't belong to a single entity
- **Domain Events**: Notifications of state changes
- **No dependencies**: Must not depend on any external frameworks or libraries

### 2. Application Layer (Use Cases)
Orchestrates the domain layer and defines interfaces for the outside world:
- **Inbound Ports**: Interfaces for use cases (CreateOrderUseCase, GetOrderUseCase)
- **Outbound Ports**: Interfaces for external dependencies (OrderRepository, PaymentGateway)
- **Application Services**: Implement use cases by orchestrating domain objects
- **DTOs**: Data transfer objects for input/output

### 3. Infrastructure Layer (Outer Hexagon)
Concrete implementations of ports and framework-specific code:
- **Inbound Adapters**: REST controllers, GraphQL resolvers, CLI handlers, message consumers
- **Outbound Adapters**: Database repositories, API clients, email services, file systems
- **Configuration**: Dependency injection, framework setup

## Quick Start Workflow

### Step 1: Identify Your Domain
Extract pure business logic:
```typescript
// ✅ Domain Entity - No dependencies
class Order {
  confirm(): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be confirmed');
    }
    this.status = OrderStatus.CONFIRMED;
  }
  
  calculateTotal(): Money {
    return this.items.reduce(
      (total, item) => total.add(item.subtotal()),
      Money.zero('USD')
    );
  }
}
```

### Step 2: Define Inbound Ports (Use Cases)
Create interfaces for how the outside world interacts with your application:
```typescript
// application/ports/inbound/CreateOrderUseCase.ts
export interface CreateOrderUseCase {
  execute(request: CreateOrderRequest): Promise<CreateOrderResponse>;
}
```

### Step 3: Define Outbound Ports
Create interfaces for external dependencies:
```typescript
// application/ports/outbound/OrderRepository.ts
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}

export interface PaymentGateway {
  processPayment(amount: Money, method: PaymentMethod): Promise<PaymentResult>;
}
```

### Step 4: Implement Application Service
Orchestrate domain logic using ports:
```typescript
export class CreateOrderService implements CreateOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private paymentGateway: PaymentGateway
  ) {}
  
  async execute(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    // Create domain object
    const order = Order.create(request.customerId, request.items);
    
    // Use outbound ports
    await this.paymentGateway.processPayment(order.calculateTotal());
    order.confirm();
    await this.orderRepository.save(order);
    
    return this.toResponse(order);
  }
}
```

### Step 5: Implement Adapters
Create concrete implementations:
```typescript
// Inbound Adapter - REST Controller
export class OrderController {
  constructor(private createOrderUseCase: CreateOrderUseCase) {}
  
  async createOrder(req: Request, res: Response) {
    const response = await this.createOrderUseCase.execute(req.body);
    res.status(201).json(response);
  }
}

// Outbound Adapter - Database Repository
export class PostgresOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    // Postgres-specific implementation
  }
}
```

### Step 6: Wire Dependencies
Use dependency injection:
```typescript
// Infrastructure configuration
const orderRepository = new PostgresOrderRepository(dbPool);
const paymentGateway = new StripePaymentGateway(apiKey);
const createOrderService = new CreateOrderService(orderRepository, paymentGateway);
const orderController = new OrderController(createOrderService);
```

## Project Structure

**Recommended folder organization:**

```
src/
├── domain/              # Pure business logic (no dependencies)
│   ├── entities/
│   ├── value-objects/
│   ├── services/
│   └── events/
├── application/         # Use cases and port definitions
│   ├── ports/
│   │   ├── inbound/    # Use case interfaces
│   │   └── outbound/   # Repository/service interfaces
│   └── services/       # Use case implementations
└── infrastructure/      # Adapters and framework code
    ├── adapters/
    │   ├── inbound/    # Controllers, CLI, GraphQL
    │   └── outbound/   # DB repos, API clients
    └── config/         # DI, framework setup
```

## Key Principles

### 1. Dependency Rule
Dependencies point inward. Outer layers depend on inner layers, never the reverse:
- Infrastructure → Application → Domain
- Domain has ZERO dependencies
- Application depends only on domain
- Infrastructure depends on everything

### 2. Ports as Contracts
Ports are interfaces defining contracts:
- **Inbound ports**: Define what the application DOES (use cases)
- **Outbound ports**: Define what the application NEEDS (dependencies)

### 3. Dependency Injection
Always inject adapters into application services:
```typescript
// ✅ Good - Dependencies injected
constructor(
  private orderRepository: OrderRepository,  // Port, not adapter
  private paymentGateway: PaymentGateway    // Port, not adapter
) {}

// ❌ Bad - Direct instantiation
constructor() {
  this.orderRepository = new PostgresOrderRepository();
}
```

### 4. Rich Domain Model
Put business logic in domain entities, not services:
```typescript
// ✅ Good - Logic in domain
class Order {
  applyDiscount(percentage: number): void {
    if (percentage < 0 || percentage > 100) {
      throw new Error('Invalid discount percentage');
    }
    this.discount = percentage;
  }
}

// ❌ Bad - Anemic domain
class Order {
  discount: number;
}
class OrderService {
  applyDiscount(order: Order, percentage: number) { /* logic here */ }
}
```

## Testing Strategy

### Unit Test Domain (Pure Logic)
```typescript
describe('Order', () => {
  it('should calculate total correctly', () => {
    const order = Order.create('customer-1', [
      { productId: '1', quantity: 2, price: Money.from(10, 'USD') }
    ]);
    expect(order.calculateTotal()).toEqual(Money.from(20, 'USD'));
  });
});
```

### Integration Test Application (With Test Doubles)
```typescript
describe('CreateOrderService', () => {
  it('should create order when payment succeeds', async () => {
    const fakeRepository = new InMemoryOrderRepository();
    const fakeGateway = new FakePaymentGateway();
    const service = new CreateOrderService(fakeRepository, fakeGateway);
    
    const response = await service.execute({ /* request */ });
    
    expect(response.orderId).toBeDefined();
  });
});
```

### E2E Test Infrastructure (Real Adapters)
```typescript
describe('Order API', () => {
  it('should create order via REST endpoint', async () => {
    const response = await request(app)
      .post('/api/orders')
      .send({ customerId: '1', items: [...] });
    
    expect(response.status).toBe(201);
  });
});
```

## Advanced Patterns

### Domain Events
Decouple domain logic from side effects:
```typescript
class Order {
  confirm(): void {
    this.status = OrderStatus.CONFIRMED;
    this.addEvent(new OrderConfirmedEvent(this.id));
  }
}
```

### Specification Pattern
Encapsulate business rules:
```typescript
class HighValueOrderSpec implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.total.greaterThan(Money.from(1000, 'USD'));
  }
}
```

### Anti-Corruption Layer
Protect domain from legacy systems:
```typescript
class LegacyOrderAdapter {
  toDomain(legacyOrder: LegacyOrder): Order {
    // Translate legacy format to domain model
  }
}
```

## Common Mistakes to Avoid

1. **Anemic Domain Model**: Entities with only getters/setters, all logic in services
2. **Infrastructure Leakage**: Database annotations on domain entities
3. **Wrong Direction Dependencies**: Domain depending on infrastructure
4. **Port Explosion**: Creating separate port for every method
5. **Over-Engineering**: Adding layers when simple CRUD suffices

## Reference Documentation

For detailed implementation patterns and examples:
- **Architecture patterns and code examples**: See [references/architecture-patterns.md](references/architecture-patterns.md)
- **Step-by-step implementation guide**: See [references/implementation-guide.md](references/implementation-guide.md)

Load these references when you need:
- Detailed port/adapter implementation patterns
- Language-specific examples (TypeScript, Python, Go)
- Project structure templates
- Migration strategies from existing codebases
- Testing strategies and examples
- Common patterns (Repository, Factory, Specification, Anti-Corruption Layer)

## Benefits

✅ **Testability**: Test business logic without database or framework
✅ **Technology Independence**: Swap databases, frameworks, UI without changing domain
✅ **Maintainability**: Clear separation makes changes easier
✅ **Team Productivity**: Teams can work on different layers independently
✅ **Flexibility**: Easy to add new interfaces (REST, GraphQL, CLI, etc.)
