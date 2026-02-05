# Hexagonal Architecture Implementation Guide

## Table of Contents
1. [Project Structure](#project-structure)
2. [Step-by-Step Implementation](#step-by-step-implementation)
3. [Language-Specific Examples](#language-specific-examples)
4. [Migration Strategies](#migration-strategies)
5. [Common Pitfalls](#common-pitfalls)

## Project Structure

### TypeScript/Node.js Structure
```
src/
├── domain/
│   ├── entities/
│   │   ├── Order.ts
│   │   ├── Customer.ts
│   │   └── Product.ts
│   ├── value-objects/
│   │   ├── OrderId.ts
│   │   ├── Money.ts
│   │   └── Email.ts
│   ├── services/
│   │   └── PricingService.ts
│   ├── events/
│   │   └── OrderCreatedEvent.ts
│   └── exceptions/
│       └── DomainException.ts
├── application/
│   ├── ports/
│   │   ├── inbound/
│   │   │   ├── CreateOrderUseCase.ts
│   │   │   └── GetOrderUseCase.ts
│   │   └── outbound/
│   │       ├── OrderRepository.ts
│   │       ├── PaymentGateway.ts
│   │       └── NotificationService.ts
│   └── services/
│       ├── CreateOrderService.ts
│       └── GetOrderService.ts
├── infrastructure/
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── rest/
│   │   │   │   └── OrderController.ts
│   │   │   ├── cli/
│   │   │   │   └── OrderCLI.ts
│   │   │   └── graphql/
│   │   │       └── OrderResolver.ts
│   │   └── outbound/
│   │       ├── persistence/
│   │       │   ├── PostgresOrderRepository.ts
│   │       │   └── MongoOrderRepository.ts
│   │       ├── payment/
│   │       │   ├── StripePaymentGateway.ts
│   │       │   └── PayPalPaymentGateway.ts
│   │       └── notification/
│   │           └── SendGridNotificationService.ts
│   ├── config/
│   │   └── dependency-injection.ts
│   └── database/
│       ├── migrations/
│       └── entities/
└── tests/
    ├── unit/
    │   └── domain/
    ├── integration/
    │   └── application/
    └── e2e/
        └── infrastructure/
```

### Python Structure
```
src/
├── domain/
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── order.py
│   │   └── customer.py
│   ├── value_objects/
│   │   ├── __init__.py
│   │   ├── order_id.py
│   │   └── money.py
│   ├── services/
│   │   └── pricing_service.py
│   └── exceptions/
│       └── domain_exception.py
├── application/
│   ├── ports/
│   │   ├── inbound/
│   │   │   ├── __init__.py
│   │   │   └── create_order_handler.py
│   │   └── outbound/
│   │       ├── __init__.py
│   │       ├── order_repository.py
│   │       └── payment_gateway.py
│   └── services/
│       └── create_order_service.py
├── infrastructure/
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── rest/
│   │   │   │   └── order_controller.py
│   │   │   └── cli/
│   │   │       └── order_cli.py
│   │   └── outbound/
│   │       ├── persistence/
│   │       │   └── postgres_order_repository.py
│   │       └── payment/
│   │           └── stripe_payment_gateway.py
│   ├── config/
│   │   └── di_container.py
│   └── database/
│       └── models.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## Step-by-Step Implementation

### Step 1: Define Domain Entities
Start with pure business objects, no dependencies.

```typescript
// domain/entities/Order.ts
import { OrderId } from '../value-objects/OrderId';
import { Money } from '../value-objects/Money';
import { OrderStatus } from '../value-objects/OrderStatus';

export class Order {
  private constructor(
    private readonly id: OrderId,
    private readonly customerId: string,
    private readonly items: OrderItem[],
    private status: OrderStatus,
    private readonly createdAt: Date
  ) {}
  
  static create(customerId: string, items: OrderItem[]): Order {
    this.validateItems(items);
    
    return new Order(
      OrderId.generate(),
      customerId,
      items,
      OrderStatus.PENDING,
      new Date()
    );
  }
  
  confirm(): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be confirmed');
    }
    this.status = OrderStatus.CONFIRMED;
  }
  
  cancel(): void {
    if (this.status === OrderStatus.SHIPPED) {
      throw new Error('Cannot cancel shipped orders');
    }
    this.status = OrderStatus.CANCELLED;
  }
  
  calculateTotal(): Money {
    return this.items.reduce(
      (total, item) => total.add(item.subtotal()),
      Money.zero('USD')
    );
  }
  
  private static validateItems(items: OrderItem[]): void {
    if (items.length === 0) {
      throw new Error('Order must have at least one item');
    }
  }
  
  // Getters
  getId(): OrderId { return this.id; }
  getStatus(): OrderStatus { return this.status; }
  getItems(): OrderItem[] { return [...this.items]; }
}
```

### Step 2: Define Value Objects
Immutable objects representing domain concepts.

```typescript
// domain/value-objects/Money.ts
export class Money {
  private constructor(
    private readonly amount: number,
    private readonly currency: string
  ) {
    if (amount < 0) {
      throw new Error('Amount cannot be negative');
    }
  }
  
  static from(amount: number, currency: string): Money {
    return new Money(amount, currency);
  }
  
  static zero(currency: string): Money {
    return new Money(0, currency);
  }
  
  add(other: Money): Money {
    this.ensureSameCurrency(other);
    return new Money(this.amount + other.amount, this.currency);
  }
  
  multiply(factor: number): Money {
    return new Money(this.amount * factor, this.currency);
  }
  
  greaterThan(other: Money): boolean {
    this.ensureSameCurrency(other);
    return this.amount > other.amount;
  }
  
  equals(other: Money): boolean {
    return this.amount === other.amount && 
           this.currency === other.currency;
  }
  
  private ensureSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new Error('Cannot operate on different currencies');
    }
  }
  
  getAmount(): number { return this.amount; }
  getCurrency(): string { return this.currency; }
}
```

### Step 3: Define Inbound Ports (Use Cases)
Interfaces for application entry points.

```typescript
// application/ports/inbound/CreateOrderUseCase.ts
export interface CreateOrderRequest {
  customerId: string;
  items: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
  shippingAddress: {
    street: string;
    city: string;
    country: string;
    postalCode: string;
  };
}

export interface CreateOrderResponse {
  orderId: string;
  totalAmount: number;
  currency: string;
  status: string;
  createdAt: Date;
}

export interface CreateOrderUseCase {
  execute(request: CreateOrderRequest): Promise<CreateOrderResponse>;
}
```

### Step 4: Define Outbound Ports
Interfaces for external dependencies.

```typescript
// application/ports/outbound/OrderRepository.ts
import { Order } from '../../domain/entities/Order';
import { OrderId } from '../../domain/value-objects/OrderId';

export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomerId(customerId: string): Promise<Order[]>;
  update(order: Order): Promise<void>;
  delete(id: OrderId): Promise<void>;
}
```

```typescript
// application/ports/outbound/PaymentGateway.ts
import { Money } from '../../domain/value-objects/Money';

export interface PaymentMethod {
  type: 'credit_card' | 'paypal' | 'bank_transfer';
  token: string;
}

export interface PaymentResult {
  transactionId: string;
  status: 'succeeded' | 'failed' | 'pending';
  amount: Money;
  failureReason?: string;
}

export interface PaymentGateway {
  processPayment(
    amount: Money, 
    method: PaymentMethod
  ): Promise<PaymentResult>;
  
  refundPayment(transactionId: string): Promise<PaymentResult>;
}
```

### Step 5: Implement Application Services
Business logic orchestration using ports.

```typescript
// application/services/CreateOrderService.ts
import { CreateOrderUseCase, CreateOrderRequest, CreateOrderResponse } 
  from '../ports/inbound/CreateOrderUseCase';
import { OrderRepository } from '../ports/outbound/OrderRepository';
import { PaymentGateway } from '../ports/outbound/PaymentGateway';
import { NotificationService } from '../ports/outbound/NotificationService';
import { Order } from '../../domain/entities/Order';
import { OrderItem } from '../../domain/entities/OrderItem';
import { Money } from '../../domain/value-objects/Money';

export class CreateOrderService implements CreateOrderUseCase {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly paymentGateway: PaymentGateway,
    private readonly notificationService: NotificationService
  ) {}
  
  async execute(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    // 1. Create domain entity
    const items = request.items.map(item =>
      OrderItem.create(
        item.productId,
        item.quantity,
        Money.from(item.price, 'USD')
      )
    );
    
    const order = Order.create(request.customerId, items);
    
    // 2. Process payment
    const paymentResult = await this.paymentGateway.processPayment(
      order.calculateTotal(),
      { type: 'credit_card', token: 'tok_123' } // From request
    );
    
    if (paymentResult.status !== 'succeeded') {
      throw new Error(`Payment failed: ${paymentResult.failureReason}`);
    }
    
    // 3. Confirm order
    order.confirm();
    
    // 4. Save order
    await this.orderRepository.save(order);
    
    // 5. Send notification
    await this.notificationService.sendOrderConfirmation(
      request.customerId,
      order.getId().getValue()
    );
    
    // 6. Return response
    return this.toResponse(order);
  }
  
  private toResponse(order: Order): CreateOrderResponse {
    const total = order.calculateTotal();
    return {
      orderId: order.getId().getValue(),
      totalAmount: total.getAmount(),
      currency: total.getCurrency(),
      status: order.getStatus().toString(),
      createdAt: new Date()
    };
  }
}
```

### Step 6: Implement Outbound Adapters
Real implementations of outbound ports.

```typescript
// infrastructure/adapters/outbound/persistence/PostgresOrderRepository.ts
import { OrderRepository } from '../../../../application/ports/outbound/OrderRepository';
import { Order } from '../../../../domain/entities/Order';
import { OrderId } from '../../../../domain/value-objects/OrderId';
import { Pool } from 'pg';

export class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly pool: Pool) {}
  
  async save(order: Order): Promise<void> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      
      // Insert order
      await client.query(
        `INSERT INTO orders (id, customer_id, status, created_at)
         VALUES ($1, $2, $3, $4)`,
        [
          order.getId().getValue(),
          order.getCustomerId(),
          order.getStatus().toString(),
          new Date()
        ]
      );
      
      // Insert order items
      for (const item of order.getItems()) {
        await client.query(
          `INSERT INTO order_items (order_id, product_id, quantity, price)
           VALUES ($1, $2, $3, $4)`,
          [
            order.getId().getValue(),
            item.getProductId(),
            item.getQuantity(),
            item.getPrice().getAmount()
          ]
        );
      }
      
      await client.query('COMMIT');
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
  
  async findById(id: OrderId): Promise<Order | null> {
    const result = await this.pool.query(
      `SELECT o.*, 
              json_agg(
                json_build_object(
                  'product_id', oi.product_id,
                  'quantity', oi.quantity,
                  'price', oi.price
                )
              ) as items
       FROM orders o
       LEFT JOIN order_items oi ON o.id = oi.order_id
       WHERE o.id = $1
       GROUP BY o.id`,
      [id.getValue()]
    );
    
    if (result.rows.length === 0) {
      return null;
    }
    
    return this.toDomain(result.rows[0]);
  }
  
  private toDomain(row: any): Order {
    // Map database row to domain entity
    // Implementation details...
  }
}
```

### Step 7: Implement Inbound Adapters
Controllers, CLI handlers, etc.

```typescript
// infrastructure/adapters/inbound/rest/OrderController.ts
import { Request, Response } from 'express';
import { CreateOrderUseCase } from '../../../../application/ports/inbound/CreateOrderUseCase';

export class OrderController {
  constructor(
    private readonly createOrderUseCase: CreateOrderUseCase
  ) {}
  
  async createOrder(req: Request, res: Response): Promise<void> {
    try {
      const response = await this.createOrderUseCase.execute({
        customerId: req.body.customerId,
        items: req.body.items,
        shippingAddress: req.body.shippingAddress
      });
      
      res.status(201).json(response);
    } catch (error) {
      console.error('Error creating order:', error);
      res.status(400).json({
        error: error.message
      });
    }
  }
}
```

### Step 8: Configure Dependency Injection
Wire up all dependencies.

```typescript
// infrastructure/config/dependency-injection.ts
import { Container } from 'inversify';
import { Pool } from 'pg';

// Ports
import { CreateOrderUseCase } from '../../application/ports/inbound/CreateOrderUseCase';
import { OrderRepository } from '../../application/ports/outbound/OrderRepository';
import { PaymentGateway } from '../../application/ports/outbound/PaymentGateway';

// Services
import { CreateOrderService } from '../../application/services/CreateOrderService';

// Adapters
import { PostgresOrderRepository } from '../adapters/outbound/persistence/PostgresOrderRepository';
import { StripePaymentGateway } from '../adapters/outbound/payment/StripePaymentGateway';
import { OrderController } from '../adapters/inbound/rest/OrderController';

const TYPES = {
  // Infrastructure
  DatabasePool: Symbol.for('DatabasePool'),
  
  // Outbound ports
  OrderRepository: Symbol.for('OrderRepository'),
  PaymentGateway: Symbol.for('PaymentGateway'),
  
  // Inbound ports
  CreateOrderUseCase: Symbol.for('CreateOrderUseCase'),
  
  // Controllers
  OrderController: Symbol.for('OrderController')
};

const container = new Container();

// Infrastructure
container.bind<Pool>(TYPES.DatabasePool).toConstantValue(
  new Pool({ connectionString: process.env.DATABASE_URL })
);

// Outbound adapters
container.bind<OrderRepository>(TYPES.OrderRepository)
  .to(PostgresOrderRepository)
  .inSingletonScope();

container.bind<PaymentGateway>(TYPES.PaymentGateway)
  .to(StripePaymentGateway)
  .inSingletonScope();

// Application services
container.bind<CreateOrderUseCase>(TYPES.CreateOrderUseCase)
  .to(CreateOrderService)
  .inRequestScope();

// Inbound adapters
container.bind<OrderController>(TYPES.OrderController)
  .to(OrderController)
  .inRequestScope();

export { container, TYPES };
```

## Language-Specific Examples

### Python with FastAPI

```python
# infrastructure/adapters/inbound/rest/order_controller.py
from fastapi import APIRouter, Depends, HTTPException
from application.ports.inbound.create_order_handler import CreateOrderHandler
from infrastructure.config.di_container import get_create_order_handler

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", status_code=201)
async def create_order(
    request: CreateOrderRequest,
    handler: CreateOrderHandler = Depends(get_create_order_handler)
):
    try:
        order_id = await handler.handle(CreateOrderCommand(
            customer_id=request.customer_id,
            items=request.items,
            shipping_address=request.shipping_address
        ))
        return {"orderId": str(order_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Go Implementation

```go
// domain/order.go
package domain

type Order struct {
    id         OrderID
    customerID CustomerID
    items      []OrderItem
    status     OrderStatus
    createdAt  time.Time
}

func NewOrder(customerID CustomerID, items []OrderItem) (*Order, error) {
    if len(items) == 0 {
        return nil, errors.New("order must have at least one item")
    }
    
    return &Order{
        id:         GenerateOrderID(),
        customerID: customerID,
        items:      items,
        status:     OrderStatusPending,
        createdAt:  time.Now(),
    }, nil
}

func (o *Order) Confirm() error {
    if o.status != OrderStatusPending {
        return errors.New("only pending orders can be confirmed")
    }
    o.status = OrderStatusConfirmed
    return nil
}
```

## Migration Strategies

### Strategy 1: Strangler Fig Pattern
Gradually replace legacy code with hexagonal architecture.

1. Identify a bounded context
2. Create new hexagonal module alongside legacy code
3. Route new features to hexagonal module
4. Gradually migrate existing features
5. Remove legacy code when fully migrated

### Strategy 2: New Features First
Implement all new features using hexagonal architecture.

1. Set up hexagonal structure
2. Build new features in hexagonal style
3. Leave legacy code as-is
4. Refactor legacy during maintenance

### Strategy 3: Extract Domain Logic
Pull domain logic out of existing layers.

1. Identify pure business logic
2. Extract to domain entities
3. Create ports around extracted logic
4. Implement adapters for existing infrastructure
5. Refactor incrementally

## Common Pitfalls

### Pitfall 1: Domain Logic in Application Layer
**Wrong:**
```typescript
class CreateOrderService {
  async execute(request: CreateOrderRequest) {
    // ❌ Business logic in application layer
    if (request.items.length === 0) {
      throw new Error('Order must have items');
    }
    const total = request.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  }
}
```

**Correct:**
```typescript
class CreateOrderService {
  async execute(request: CreateOrderRequest) {
    // ✅ Delegate to domain
    const order = Order.create(request.customerId, request.items);
    const total = order.calculateTotal();
  }
}
```

### Pitfall 2: Leaking Infrastructure into Domain
**Wrong:**
```typescript
// ❌ Domain depends on infrastructure
import { Entity, Column } from 'typeorm';

class Order extends Entity {
  @Column()
  customerId: string;
}
```

**Correct:**
```typescript
// ✅ Pure domain, no infrastructure dependencies
class Order {
  constructor(
    private customerId: string
  ) {}
}
```

### Pitfall 3: Anemic Domain Model
**Wrong:**
```typescript
// ❌ Just data, no behavior
class Order {
  id: string;
  status: string;
  items: any[];
}

// Logic in service
class OrderService {
  confirm(order: Order) {
    if (order.status !== 'PENDING') throw new Error();
    order.status = 'CONFIRMED';
  }
}
```

**Correct:**
```typescript
// ✅ Rich domain model
class Order {
  confirm() {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be confirmed');
    }
    this.status = OrderStatus.CONFIRMED;
  }
}
```

### Pitfall 4: Too Many Layers
Keep it simple. Don't create unnecessary abstractions.

**Wrong:** Domain → Application → Service → Repository → DAO → Database

**Correct:** Domain → Application → Infrastructure

### Pitfall 5: Port Explosion
Don't create a port for every single method.

**Wrong:** `FindOrderByIdPort`, `FindOrderByCustomerPort`, `SaveOrderPort`

**Correct:** `OrderRepository` with multiple methods