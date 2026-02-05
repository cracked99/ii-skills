# Hexagonal Architecture Patterns

## Table of Contents
1. [Core Architecture Patterns](#core-architecture-patterns)
2. [Port Definitions](#port-definitions)
3. [Adapter Implementations](#adapter-implementations)
4. [Dependency Injection](#dependency-injection)
5. [Testing Strategies](#testing-strategies)
6. [Common Patterns](#common-patterns)

## Core Architecture Patterns

### Layer Organization

```
┌─────────────────────────────────────────────┐
│            Adapters (Infrastructure)        │
│  ┌───────────────────────────────────────┐  │
│  │         Application Layer             │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │       Domain Layer              │  │  │
│  │  │  (Business Logic - Pure)        │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Domain Layer (Inner Hexagon)
- Pure business logic
- No framework dependencies
- No infrastructure dependencies
- Contains entities, value objects, domain services
- Domain events for state changes

### Application Layer (Orchestration)
- Use cases / application services
- Orchestrates domain objects
- Defines inbound ports (interfaces)
- Defines outbound ports (interfaces)
- Transaction boundaries
- Security enforcement

### Infrastructure Layer (Outer Hexagon)
- Adapters for external systems
- Framework-specific code
- Database implementations
- API clients
- Message queue handlers
- Web controllers

## Port Definitions

### Inbound Ports (Driving Ports)
Define how external actors interact with the application.

**Pattern: Use Case Interface**
```typescript
// TypeScript Example
interface CreateOrderUseCase {
  execute(request: CreateOrderRequest): Promise<CreateOrderResponse>;
}

interface CreateOrderRequest {
  customerId: string;
  items: OrderItem[];
  shippingAddress: Address;
}

interface CreateOrderResponse {
  orderId: string;
  totalAmount: Money;
  estimatedDelivery: Date;
}
```

**Pattern: Command Handler**
```python
# Python Example
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CreateOrderCommand:
    customer_id: str
    items: list[OrderItem]
    shipping_address: Address

class CreateOrderHandler(ABC):
    @abstractmethod
    async def handle(self, command: CreateOrderCommand) -> OrderId:
        pass
```

### Outbound Ports (Driven Ports)
Define how the application interacts with external systems.

**Pattern: Repository Interface**
```typescript
// TypeScript Example
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(orderId: OrderId): Promise<Order | null>;
  findByCustomer(customerId: CustomerId): Promise<Order[]>;
  delete(orderId: OrderId): Promise<void>;
}
```

**Pattern: External Service Interface**
```python
# Python Example
from abc import ABC, abstractmethod

class PaymentGateway(ABC):
    @abstractmethod
    async def process_payment(
        self, 
        amount: Money, 
        payment_method: PaymentMethod
    ) -> PaymentResult:
        pass
    
    @abstractmethod
    async def refund_payment(
        self, 
        transaction_id: str
    ) -> RefundResult:
        pass
```

**Pattern: Notification Service**
```typescript
interface NotificationService {
  sendEmail(recipient: Email, subject: string, body: string): Promise<void>;
  sendSMS(phoneNumber: Phone, message: string): Promise<void>;
}
```

## Adapter Implementations

### Inbound Adapters (Primary/Driving Adapters)

**REST API Controller**
```typescript
// Express.js adapter
class OrderController {
  constructor(private createOrderUseCase: CreateOrderUseCase) {}
  
  async createOrder(req: Request, res: Response): Promise<void> {
    try {
      const request: CreateOrderRequest = {
        customerId: req.body.customerId,
        items: req.body.items,
        shippingAddress: req.body.shippingAddress
      };
      
      const response = await this.createOrderUseCase.execute(request);
      res.status(201).json(response);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
}
```

**CLI Adapter**
```python
# Click CLI adapter
import click
from domain.ports.inbound import CreateOrderHandler

class OrderCLI:
    def __init__(self, create_order_handler: CreateOrderHandler):
        self.create_order_handler = create_order_handler
    
    @click.command()
    @click.option('--customer-id', required=True)
    @click.option('--items', required=True)
    def create_order(self, customer_id: str, items: str):
        command = CreateOrderCommand(
            customer_id=customer_id,
            items=parse_items(items),
            shipping_address=get_default_address()
        )
        
        order_id = await self.create_order_handler.handle(command)
        click.echo(f"Order created: {order_id}")
```

**Message Queue Consumer**
```typescript
// RabbitMQ adapter
class OrderEventConsumer {
  constructor(private processOrderUseCase: ProcessOrderUseCase) {}
  
  async consume(message: Message): Promise<void> {
    const event = JSON.parse(message.content.toString());
    
    await this.processOrderUseCase.execute({
      orderId: event.orderId,
      action: event.action
    });
    
    message.ack();
  }
}
```

### Outbound Adapters (Secondary/Driven Adapters)

**Database Repository Adapter**
```typescript
// PostgreSQL adapter using TypeORM
class PostgresOrderRepository implements OrderRepository {
  constructor(private connection: Connection) {}
  
  async save(order: Order): Promise<void> {
    const entity = this.toEntity(order);
    await this.connection.getRepository(OrderEntity).save(entity);
  }
  
  async findById(orderId: OrderId): Promise<Order | null> {
    const entity = await this.connection
      .getRepository(OrderEntity)
      .findOne({ where: { id: orderId.value } });
    
    return entity ? this.toDomain(entity) : null;
  }
  
  private toEntity(order: Order): OrderEntity {
    // Map domain object to database entity
  }
  
  private toDomain(entity: OrderEntity): Order {
    // Map database entity to domain object
  }
}
```

**External API Adapter**
```python
# Stripe payment gateway adapter
import stripe
from domain.ports.outbound import PaymentGateway

class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str):
        stripe.api_key = api_key
    
    async def process_payment(
        self, 
        amount: Money, 
        payment_method: PaymentMethod
    ) -> PaymentResult:
        try:
            charge = stripe.Charge.create(
                amount=amount.cents,
                currency=amount.currency.code.lower(),
                source=payment_method.token
            )
            
            return PaymentResult(
                transaction_id=charge.id,
                status=PaymentStatus.SUCCEEDED,
                amount=amount
            )
        except stripe.error.CardError as e:
            return PaymentResult(
                transaction_id=None,
                status=PaymentStatus.FAILED,
                error=str(e)
            )
```

**In-Memory Adapter (Testing)**
```typescript
// In-memory repository for testing
class InMemoryOrderRepository implements OrderRepository {
  private orders: Map<string, Order> = new Map();
  
  async save(order: Order): Promise<void> {
    this.orders.set(order.id.value, order);
  }
  
  async findById(orderId: OrderId): Promise<Order | null> {
    return this.orders.get(orderId.value) || null;
  }
  
  async findByCustomer(customerId: CustomerId): Promise<Order[]> {
    return Array.from(this.orders.values())
      .filter(order => order.customerId.equals(customerId));
  }
  
  clear(): void {
    this.orders.clear();
  }
}
```

## Dependency Injection

### Constructor Injection
```typescript
// Application service with injected dependencies
class CreateOrderService implements CreateOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private paymentGateway: PaymentGateway,
    private notificationService: NotificationService,
    private inventoryService: InventoryService
  ) {}
  
  async execute(request: CreateOrderRequest): Promise<CreateOrderResponse> {
    // Use injected dependencies
    const order = Order.create(request);
    
    await this.inventoryService.reserve(order.items);
    const payment = await this.paymentGateway.process(order.totalAmount);
    
    if (payment.isSuccessful()) {
      await this.orderRepository.save(order);
      await this.notificationService.sendConfirmation(order);
    }
    
    return this.toResponse(order);
  }
}
```

### Dependency Injection Container
```typescript
// IoC Container setup
class Container {
  registerDependencies(): void {
    // Register outbound adapters
    this.bind<OrderRepository>(TYPES.OrderRepository)
      .to(PostgresOrderRepository)
      .inSingletonScope();
    
    this.bind<PaymentGateway>(TYPES.PaymentGateway)
      .to(StripePaymentGateway)
      .inSingletonScope();
    
    // Register application services
    this.bind<CreateOrderUseCase>(TYPES.CreateOrderUseCase)
      .to(CreateOrderService)
      .inRequestScope();
    
    // Register inbound adapters
    this.bind<OrderController>(TYPES.OrderController)
      .to(OrderController)
      .inRequestScope();
  }
}
```

## Testing Strategies

### Unit Testing Domain Logic
```typescript
describe('Order', () => {
  it('should calculate total correctly', () => {
    const order = Order.create({
      items: [
        { productId: '1', quantity: 2, price: Money.from(10, 'USD') },
        { productId: '2', quantity: 1, price: Money.from(20, 'USD') }
      ]
    });
    
    expect(order.totalAmount).toEqual(Money.from(40, 'USD'));
  });
  
  it('should not allow negative quantities', () => {
    expect(() => {
      Order.create({
        items: [{ productId: '1', quantity: -1, price: Money.from(10, 'USD') }]
      });
    }).toThrow('Quantity must be positive');
  });
});
```

### Integration Testing with Test Adapters
```typescript
describe('CreateOrderService', () => {
  let service: CreateOrderService;
  let orderRepository: InMemoryOrderRepository;
  let paymentGateway: FakePaymentGateway;
  
  beforeEach(() => {
    orderRepository = new InMemoryOrderRepository();
    paymentGateway = new FakePaymentGateway();
    
    service = new CreateOrderService(
      orderRepository,
      paymentGateway,
      new FakeNotificationService(),
      new FakeInventoryService()
    );
  });
  
  it('should create order when payment succeeds', async () => {
    paymentGateway.setNextResult(PaymentResult.success());
    
    const response = await service.execute({
      customerId: 'customer-1',
      items: [{ productId: '1', quantity: 1 }]
    });
    
    expect(response.orderId).toBeDefined();
    const savedOrder = await orderRepository.findById(new OrderId(response.orderId));
    expect(savedOrder).toBeDefined();
  });
  
  it('should not create order when payment fails', async () => {
    paymentGateway.setNextResult(PaymentResult.failed('Insufficient funds'));
    
    await expect(service.execute({
      customerId: 'customer-1',
      items: [{ productId: '1', quantity: 1 }]
    })).rejects.toThrow('Payment failed');
    
    const orders = await orderRepository.findAll();
    expect(orders).toHaveLength(0);
  });
});
```

### End-to-End Testing
```python
# E2E test with real adapters
import pytest
from tests.fixtures import database, test_client

def test_create_order_e2e(database, test_client):
    # Arrange
    customer = create_test_customer(database)
    product = create_test_product(database, price=Money(1000, 'USD'))
    
    # Act
    response = test_client.post('/api/orders', json={
        'customerId': customer.id,
        'items': [{'productId': product.id, 'quantity': 2}]
    })
    
    # Assert
    assert response.status_code == 201
    order_id = response.json['orderId']
    
    # Verify order in database
    order = database.query(Order).filter_by(id=order_id).first()
    assert order is not None
    assert order.total_amount == Money(2000, 'USD')
```

## Common Patterns

### Repository Pattern
Use for data persistence abstraction. Domain defines interface, infrastructure implements it.

### Factory Pattern
Use for complex object creation in domain layer.

```typescript
class OrderFactory {
  static create(request: CreateOrderRequest): Order {
    const items = request.items.map(item => 
      OrderItem.create(item.productId, item.quantity, item.price)
    );
    
    return new Order(
      OrderId.generate(),
      new CustomerId(request.customerId),
      items,
      request.shippingAddress,
      OrderStatus.PENDING
    );
  }
}
```

### Domain Events Pattern
Use for decoupling domain logic and triggering side effects.

```typescript
class Order {
  private events: DomainEvent[] = [];
  
  confirm(): void {
    this.status = OrderStatus.CONFIRMED;
    this.events.push(new OrderConfirmedEvent(this.id, this.customerId));
  }
  
  getEvents(): DomainEvent[] {
    return [...this.events];
  }
  
  clearEvents(): void {
    this.events = [];
  }
}
```

### Specification Pattern
Use for complex business rules and querying.

```typescript
interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
}

class HighValueOrderSpecification implements Specification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.totalAmount.greaterThan(Money.from(1000, 'USD'));
  }
}
```

### Anti-Corruption Layer
Use when integrating with legacy systems or external APIs.

```typescript
class LegacyOrderAdapter {
  constructor(private legacyApi: LegacyOrderApi) {}
  
  async fetchOrder(orderId: string): Promise<Order> {
    const legacyOrder = await this.legacyApi.getOrder(orderId);
    
    // Translate legacy format to domain model
    return Order.reconstitute({
      id: new OrderId(legacyOrder.order_id),
      customerId: new CustomerId(legacyOrder.cust_id),
      items: this.translateItems(legacyOrder.line_items),
      status: this.translateStatus(legacyOrder.state)
    });
  }
  
  private translateStatus(legacyStatus: string): OrderStatus {
    const mapping = {
      'NEW': OrderStatus.PENDING,
      'CONFIRMED': OrderStatus.CONFIRMED,
      'SHIPPED': OrderStatus.SHIPPED
    };
    return mapping[legacyStatus] || OrderStatus.PENDING;
  }
}
```