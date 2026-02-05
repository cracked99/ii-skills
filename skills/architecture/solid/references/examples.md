# SOLID Principles - Multi-Language Examples

## Table of Contents
1. [E-Commerce System Example](#e-commerce-system-example)
2. [Content Management System](#content-management-system)
3. [Payment Processing System](#payment-processing-system)
4. [Notification System](#notification-system)
5. [Language-Specific Examples](#language-specific-examples)

---

## E-Commerce System Example

### Complete System Following SOLID

#### TypeScript Implementation

```typescript
// ===== DOMAIN LAYER (Pure Business Logic) =====

// Value Objects (Immutable)
class Money {
  private constructor(
    private readonly amount: number,
    private readonly currency: string
  ) {}
  
  static create(amount: number, currency: string): Money {
    if (amount < 0) throw new Error('Amount cannot be negative');
    return new Money(amount, currency);
  }
  
  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return Money.create(this.amount + other.amount, this.currency);
  }
  
  multiply(factor: number): Money {
    return Money.create(this.amount * factor, this.currency);
  }
  
  greaterThan(other: Money): boolean {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return this.amount > other.amount;
  }
  
  getAmount(): number { return this.amount; }
  getCurrency(): string { return this.currency; }
}

class OrderId {
  private constructor(private readonly value: string) {}
  
  static create(value: string): OrderId {
    if (!value || value.trim().length === 0) {
      throw new Error('Order ID cannot be empty');
    }
    return new OrderId(value);
  }
  
  static generate(): OrderId {
    return new OrderId(crypto.randomUUID());
  }
  
  equals(other: OrderId): boolean {
    return this.value === other.value;
  }
  
  toString(): string { return this.value; }
}

// Entities
class Order {
  private constructor(
    private readonly id: OrderId,
    private readonly customerId: string,
    private items: OrderItem[],
    private status: OrderStatus,
    private readonly createdAt: Date
  ) {}
  
  static create(customerId: string, items: OrderItem[]): Order {
    if (items.length === 0) {
      throw new Error('Order must have at least one item');
    }
    
    return new Order(
      OrderId.generate(),
      customerId,
      items,
      OrderStatus.PENDING,
      new Date()
    );
  }
  
  // SRP: Order knows how to calculate its own total
  calculateTotal(): Money {
    return this.items.reduce(
      (total, item) => total.add(item.getSubtotal()),
      Money.create(0, 'USD')
    );
  }
  
  // SRP: Order knows its own confirmation logic
  confirm(): void {
    if (this.status !== OrderStatus.PENDING) {
      throw new Error('Only pending orders can be confirmed');
    }
    this.status = OrderStatus.CONFIRMED;
  }
  
  ship(): void {
    if (this.status !== OrderStatus.CONFIRMED) {
      throw new Error('Only confirmed orders can be shipped');
    }
    this.status = OrderStatus.SHIPPED;
  }
  
  cancel(): void {
    if (this.status === OrderStatus.SHIPPED) {
      throw new Error('Cannot cancel shipped orders');
    }
    this.status = OrderStatus.CANCELLED;
  }
  
  // Getters
  getId(): OrderId { return this.id; }
  getCustomerId(): string { return this.customerId; }
  getItems(): OrderItem[] { return [...this.items]; }
  getStatus(): OrderStatus { return this.status; }
  getCreatedAt(): Date { return this.createdAt; }
}

class OrderItem {
  constructor(
    private readonly productId: string,
    private readonly quantity: number,
    private readonly unitPrice: Money
  ) {
    if (quantity <= 0) {
      throw new Error('Quantity must be positive');
    }
  }
  
  getSubtotal(): Money {
    return this.unitPrice.multiply(this.quantity);
  }
  
  getProductId(): string { return this.productId; }
  getQuantity(): number { return this.quantity; }
  getUnitPrice(): Money { return this.unitPrice; }
}

enum OrderStatus {
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  SHIPPED = 'SHIPPED',
  CANCELLED = 'CANCELLED'
}

// ===== APPLICATION LAYER (Use Cases & Ports) =====

// Inbound Ports (Use Cases)
interface PlaceOrderUseCase {
  execute(request: PlaceOrderRequest): Promise<PlaceOrderResponse>;
}

interface PlaceOrderRequest {
  customerId: string;
  items: Array<{
    productId: string;
    quantity: number;
  }>;
  paymentMethod: string;
}

interface PlaceOrderResponse {
  orderId: string;
  totalAmount: number;
  currency: string;
}

// Outbound Ports (Dependencies)
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: OrderId): Promise<Order | null>;
}

interface ProductRepository {
  findById(id: string): Promise<Product | null>;
}

interface PaymentGateway {
  charge(amount: Money, method: string): Promise<PaymentResult>;
}

interface NotificationService {
  sendOrderConfirmation(customerId: string, orderId: OrderId): Promise<void>;
}

interface InventoryService {
  reserve(items: OrderItem[]): Promise<boolean>;
  release(items: OrderItem[]): Promise<void>;
}

// Application Service (Orchestrates Domain Logic)
class PlaceOrderService implements PlaceOrderUseCase {
  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly productRepository: ProductRepository,
    private readonly paymentGateway: PaymentGateway,
    private readonly notificationService: NotificationService,
    private readonly inventoryService: InventoryService
  ) {}
  
  async execute(request: PlaceOrderRequest): Promise<PlaceOrderResponse> {
    // 1. Fetch product details
    const orderItems = await this.buildOrderItems(request.items);
    
    // 2. Create order (domain logic)
    const order = Order.create(request.customerId, orderItems);
    const total = order.calculateTotal();
    
    // 3. Reserve inventory
    const reserved = await this.inventoryService.reserve(orderItems);
    if (!reserved) {
      throw new Error('Insufficient inventory');
    }
    
    try {
      // 4. Process payment
      const paymentResult = await this.paymentGateway.charge(
        total,
        request.paymentMethod
      );
      
      if (!paymentResult.isSuccessful()) {
        throw new Error('Payment failed');
      }
      
      // 5. Confirm order
      order.confirm();
      
      // 6. Save order
      await this.orderRepository.save(order);
      
      // 7. Send notification
      await this.notificationService.sendOrderConfirmation(
        order.getCustomerId(),
        order.getId()
      );
      
      // 8. Return response
      return {
        orderId: order.getId().toString(),
        totalAmount: total.getAmount(),
        currency: total.getCurrency()
      };
      
    } catch (error) {
      // Rollback inventory reservation
      await this.inventoryService.release(orderItems);
      throw error;
    }
  }
  
  private async buildOrderItems(
    items: Array<{ productId: string; quantity: number }>
  ): Promise<OrderItem[]> {
    const orderItems: OrderItem[] = [];
    
    for (const item of items) {
      const product = await this.productRepository.findById(item.productId);
      if (!product) {
        throw new Error(`Product not found: ${item.productId}`);
      }
      
      orderItems.push(new OrderItem(
        item.productId,
        item.quantity,
        product.getPrice()
      ));
    }
    
    return orderItems;
  }
}

// ===== INFRASTRUCTURE LAYER (Adapters) =====

// Inbound Adapter - REST Controller
class OrderController {
  constructor(private readonly placeOrderUseCase: PlaceOrderUseCase) {}
  
  async placeOrder(req: Request, res: Response): Promise<void> {
    try {
      const response = await this.placeOrderUseCase.execute({
        customerId: req.body.customerId,
        items: req.body.items,
        paymentMethod: req.body.paymentMethod
      });
      
      res.status(201).json(response);
    } catch (error) {
      console.error('Error placing order:', error);
      res.status(400).json({ error: (error as Error).message });
    }
  }
}

// Outbound Adapter - PostgreSQL Repository
class PostgresOrderRepository implements OrderRepository {
  constructor(private readonly pool: any) {}
  
  async save(order: Order): Promise<void> {
    const client = await this.pool.connect();
    
    try {
      await client.query('BEGIN');
      
      // Save order
      await client.query(
        `INSERT INTO orders (id, customer_id, status, created_at, total_amount)
         VALUES ($1, $2, $3, $4, $5)`,
        [
          order.getId().toString(),
          order.getCustomerId(),
          order.getStatus(),
          order.getCreatedAt(),
          order.calculateTotal().getAmount()
        ]
      );
      
      // Save order items
      for (const item of order.getItems()) {
        await client.query(
          `INSERT INTO order_items (order_id, product_id, quantity, unit_price)
           VALUES ($1, $2, $3, $4)`,
          [
            order.getId().toString(),
            item.getProductId(),
            item.getQuantity(),
            item.getUnitPrice().getAmount()
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
      'SELECT * FROM orders WHERE id = $1',
      [id.toString()]
    );
    
    if (result.rows.length === 0) {
      return null;
    }
    
    // Map to domain object
    // ... (mapping logic)
    return null; // Simplified
  }
}

// Outbound Adapter - Stripe Payment
class StripePaymentGateway implements PaymentGateway {
  constructor(private readonly stripeClient: any) {}
  
  async charge(amount: Money, method: string): Promise<PaymentResult> {
    try {
      const charge = await this.stripeClient.charges.create({
        amount: amount.getAmount() * 100, // Stripe uses cents
        currency: amount.getCurrency().toLowerCase(),
        source: method
      });
      
      return PaymentResult.success(charge.id);
    } catch (error) {
      return PaymentResult.failure((error as Error).message);
    }
  }
}

// Outbound Adapter - Email Notification
class SendGridNotificationService implements NotificationService {
  constructor(private readonly sendGridClient: any) {}
  
  async sendOrderConfirmation(
    customerId: string,
    orderId: OrderId
  ): Promise<void> {
    // Fetch customer email (simplified)
    const customerEmail = await this.getCustomerEmail(customerId);
    
    await this.sendGridClient.send({
      to: customerEmail,
      from: 'orders@example.com',
      subject: 'Order Confirmation',
      text: `Your order ${orderId.toString()} has been confirmed!`
    });
  }
  
  private async getCustomerEmail(customerId: string): Promise<string> {
    // Fetch from database
    return 'customer@example.com'; // Simplified
  }
}

// Dependency Injection Configuration
class DIContainer {
  private static instance: DIContainer;
  
  private constructor(
    public orderRepository: OrderRepository,
    public productRepository: ProductRepository,
    public paymentGateway: PaymentGateway,
    public notificationService: NotificationService,
    public inventoryService: InventoryService
  ) {}
  
  static configure(config: any): DIContainer {
    const orderRepo = new PostgresOrderRepository(config.dbPool);
    const productRepo = new PostgresProductRepository(config.dbPool);
    const paymentGateway = new StripePaymentGateway(config.stripeClient);
    const notificationService = new SendGridNotificationService(config.sendGridClient);
    const inventoryService = new InMemoryInventoryService();
    
    DIContainer.instance = new DIContainer(
      orderRepo,
      productRepo,
      paymentGateway,
      notificationService,
      inventoryService
    );
    
    return DIContainer.instance;
  }
  
  static getInstance(): DIContainer {
    return DIContainer.instance;
  }
  
  getPlaceOrderUseCase(): PlaceOrderUseCase {
    return new PlaceOrderService(
      this.orderRepository,
      this.productRepository,
      this.paymentGateway,
      this.notificationService,
      this.inventoryService
    );
  }
}

// Application Bootstrap
async function main() {
  const config = {
    dbPool: /* PostgreSQL pool */,
    stripeClient: /* Stripe client */,
    sendGridClient: /* SendGrid client */
  };
  
  const container = DIContainer.configure(config);
  const placeOrderUseCase = container.getPlaceOrderUseCase();
  const orderController = new OrderController(placeOrderUseCase);
  
  // Setup Express routes
  // app.post('/api/orders', (req, res) => orderController.placeOrder(req, res));
}
```

### SOLID Principles Applied

**Single Responsibility (S):**
- `Order` - Domain logic only
- `OrderRepository` - Persistence only
- `PaymentGateway` - Payment processing only
- `NotificationService` - Notifications only
- `PlaceOrderService` - Orchestration only

**Open/Closed (O):**
- Easy to add new payment gateways (implement `PaymentGateway`)
- Easy to add new notification channels (implement `NotificationService`)
- Can add new repositories without modifying existing code

**Liskov Substitution (L):**
- Any `PaymentGateway` implementation can replace another
- Any `OrderRepository` implementation works the same way
- All implementations honor the contract

**Interface Segregation (I):**
- `OrderRepository` - Only order persistence methods
- `ProductRepository` - Only product methods
- `PaymentGateway` - Only payment methods
- No fat interfaces forcing unused methods

**Dependency Inversion (D):**
- `PlaceOrderService` depends on interfaces, not concrete classes
- All dependencies injected via constructor
- Easy to swap implementations
- Easy to test with mocks

---

## Python Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

# ===== DOMAIN LAYER =====

class Money:
    def __init__(self, amount: float, currency: str):
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self._amount = amount
        self._currency = currency
    
    def add(self, other: 'Money') -> 'Money':
        if self._currency != other._currency:
            raise ValueError("Currency mismatch")
        return Money(self._amount + other._amount, self._currency)
    
    def multiply(self, factor: float) -> 'Money':
        return Money(self._amount * factor, self._currency)
    
    @property
    def amount(self) -> float:
        return self._amount
    
    @property
    def currency(self) -> str:
        return self._currency


class OrderId:
    def __init__(self, value: str):
        if not value:
            raise ValueError("Order ID cannot be empty")
        self._value = value
    
    @classmethod
    def generate(cls) -> 'OrderId':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        return isinstance(other, OrderId) and self._value == other._value


class OrderStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Money
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
    
    def get_subtotal(self) -> Money:
        return self.unit_price.multiply(self.quantity)


class Order:
    def __init__(
        self,
        order_id: OrderId,
        customer_id: str,
        items: List[OrderItem],
        status: OrderStatus,
        created_at: datetime
    ):
        self._id = order_id
        self._customer_id = customer_id
        self._items = items
        self._status = status
        self._created_at = created_at
    
    @classmethod
    def create(cls, customer_id: str, items: List[OrderItem]) -> 'Order':
        if not items:
            raise ValueError("Order must have at least one item")
        
        return cls(
            OrderId.generate(),
            customer_id,
            items,
            OrderStatus.PENDING,
            datetime.now()
        )
    
    def calculate_total(self) -> Money:
        total = Money(0, "USD")
        for item in self._items:
            total = total.add(item.get_subtotal())
        return total
    
    def confirm(self) -> None:
        if self._status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")
        self._status = OrderStatus.CONFIRMED
    
    @property
    def id(self) -> OrderId:
        return self._id
    
    @property
    def customer_id(self) -> str:
        return self._customer_id
    
    @property
    def status(self) -> OrderStatus:
        return self._status


# ===== APPLICATION LAYER =====

# Inbound Port
class PlaceOrderUseCase(ABC):
    @abstractmethod
    async def execute(self, request: 'PlaceOrderRequest') -> 'PlaceOrderResponse':
        pass


@dataclass
class PlaceOrderRequest:
    customer_id: str
    items: List[dict]
    payment_method: str


@dataclass
class PlaceOrderResponse:
    order_id: str
    total_amount: float
    currency: str


# Outbound Ports
class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        pass


class PaymentGateway(ABC):
    @abstractmethod
    async def charge(self, amount: Money, method: str) -> 'PaymentResult':
        pass


class NotificationService(ABC):
    @abstractmethod
    async def send_order_confirmation(
        self,
        customer_id: str,
        order_id: OrderId
    ) -> None:
        pass


# Application Service
class PlaceOrderService(PlaceOrderUseCase):
    def __init__(
        self,
        order_repository: OrderRepository,
        payment_gateway: PaymentGateway,
        notification_service: NotificationService
    ):
        self._order_repository = order_repository
        self._payment_gateway = payment_gateway
        self._notification_service = notification_service
    
    async def execute(self, request: PlaceOrderRequest) -> PlaceOrderResponse:
        # Create order
        order_items = [
            OrderItem(
                product_id=item['productId'],
                quantity=item['quantity'],
                unit_price=Money(item['price'], 'USD')
            )
            for item in request.items
        ]
        
        order = Order.create(request.customer_id, order_items)
        total = order.calculate_total()
        
        # Process payment
        payment_result = await self._payment_gateway.charge(
            total,
            request.payment_method
        )
        
        if not payment_result.is_successful:
            raise Exception("Payment failed")
        
        # Confirm order
        order.confirm()
        
        # Save order
        await self._order_repository.save(order)
        
        # Send notification
        await self._notification_service.send_order_confirmation(
            order.customer_id,
            order.id
        )
        
        return PlaceOrderResponse(
            order_id=str(order.id),
            total_amount=total.amount,
            currency=total.currency
        )


# ===== INFRASTRUCTURE LAYER =====

# Outbound Adapter - PostgreSQL
class PostgresOrderRepository(OrderRepository):
    def __init__(self, db_pool):
        self._pool = db_pool
    
    async def save(self, order: Order) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO orders (id, customer_id, status, created_at)
                VALUES ($1, $2, $3, $4)
                """,
                str(order.id),
                order.customer_id,
                order.status.value,
                order._created_at
            )
    
    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        # Implementation
        pass


# Outbound Adapter - Stripe
class StripePaymentGateway(PaymentGateway):
    def __init__(self, stripe_client):
        self._stripe = stripe_client
    
    async def charge(self, amount: Money, method: str) -> 'PaymentResult':
        try:
            charge = self._stripe.Charge.create(
                amount=int(amount.amount * 100),
                currency=amount.currency.lower(),
                source=method
            )
            return PaymentResult(is_successful=True, transaction_id=charge.id)
        except Exception as e:
            return PaymentResult(is_successful=False, error=str(e))


# Inbound Adapter - FastAPI Controller
from fastapi import APIRouter, Depends

router = APIRouter()

async def get_place_order_use_case() -> PlaceOrderUseCase:
    # Dependency injection
    order_repo = PostgresOrderRepository(db_pool)
    payment_gateway = StripePaymentGateway(stripe_client)
    notification_service = EmailNotificationService(sendgrid_client)
    
    return PlaceOrderService(order_repo, payment_gateway, notification_service)


@router.post("/orders")
async def place_order(
    request: PlaceOrderRequest,
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case)
):
    response = await use_case.execute(request)
    return response
```

---

## Java Implementation

```java
// ===== DOMAIN LAYER =====

public class Money {
    private final double amount;
    private final String currency;
    
    private Money(double amount, String currency) {
        if (amount < 0) {
            throw new IllegalArgumentException("Amount cannot be negative");
        }
        this.amount = amount;
        this.currency = currency;
    }
    
    public static Money create(double amount, String currency) {
        return new Money(amount, currency);
    }
    
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch");
        }
        return new Money(this.amount + other.amount, this.currency);
    }
    
    public Money multiply(double factor) {
        return new Money(this.amount * factor, this.currency);
    }
    
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
}

public class OrderId {
    private final String value;
    
    private OrderId(String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("Order ID cannot be empty");
        }
        this.value = value;
    }
    
    public static OrderId create(String value) {
        return new OrderId(value);
    }
    
    public static OrderId generate() {
        return new OrderId(UUID.randomUUID().toString());
    }
    
    @Override
    public String toString() {
        return value;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof OrderId)) return false;
        return this.value.equals(((OrderId) obj).value);
    }
}

public enum OrderStatus {
    PENDING,
    CONFIRMED,
    SHIPPED,
    CANCELLED
}

public class OrderItem {
    private final String productId;
    private final int quantity;
    private final Money unitPrice;
    
    public OrderItem(String productId, int quantity, Money unitPrice) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        this.productId = productId;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
    }
    
    public Money getSubtotal() {
        return unitPrice.multiply(quantity);
    }
    
    // Getters...
}

public class Order {
    private final OrderId id;
    private final String customerId;
    private final List<OrderItem> items;
    private OrderStatus status;
    private final Date createdAt;
    
    private Order(
        OrderId id,
        String customerId,
        List<OrderItem> items,
        OrderStatus status,
        Date createdAt
    ) {
        this.id = id;
        this.customerId = customerId;
        this.items = new ArrayList<>(items);
        this.status = status;
        this.createdAt = createdAt;
    }
    
    public static Order create(String customerId, List<OrderItem> items) {
        if (items.isEmpty()) {
            throw new IllegalArgumentException("Order must have at least one item");
        }
        
        return new Order(
            OrderId.generate(),
            customerId,
            items,
            OrderStatus.PENDING,
            new Date()
        );
    }
    
    public Money calculateTotal() {
        Money total = Money.create(0, "USD");
        for (OrderItem item : items) {
            total = total.add(item.getSubtotal());
        }
        return total;
    }
    
    public void confirm() {
        if (status != OrderStatus.PENDING) {
            throw new IllegalStateException("Only pending orders can be confirmed");
        }
        status = OrderStatus.CONFIRMED;
    }
    
    // Getters...
}

// ===== APPLICATION LAYER =====

// Inbound Port
public interface PlaceOrderUseCase {
    PlaceOrderResponse execute(PlaceOrderRequest request);
}

public class PlaceOrderRequest {
    private final String customerId;
    private final List<OrderItemRequest> items;
    private final String paymentMethod;
    
    // Constructor, getters...
}

public class PlaceOrderResponse {
    private final String orderId;
    private final double totalAmount;
    private final String currency;
    
    // Constructor, getters...
}

// Outbound Ports
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(OrderId id);
}

public interface PaymentGateway {
    PaymentResult charge(Money amount, String method);
}

public interface NotificationService {
    void sendOrderConfirmation(String customerId, OrderId orderId);
}

// Application Service
public class PlaceOrderService implements PlaceOrderUseCase {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final NotificationService notificationService;
    
    public PlaceOrderService(
        OrderRepository orderRepository,
        PaymentGateway paymentGateway,
        NotificationService notificationService
    ) {
        this.orderRepository = orderRepository;
        this.paymentGateway = paymentGateway;
        this.notificationService = notificationService;
    }
    
    @Override
    public PlaceOrderResponse execute(PlaceOrderRequest request) {
        // Create order
        List<OrderItem> orderItems = buildOrderItems(request.getItems());
        Order order = Order.create(request.getCustomerId(), orderItems);
        Money total = order.calculateTotal();
        
        // Process payment
        PaymentResult paymentResult = paymentGateway.charge(
            total,
            request.getPaymentMethod()
        );
        
        if (!paymentResult.isSuccessful()) {
            throw new RuntimeException("Payment failed");
        }
        
        // Confirm and save order
        order.confirm();
        orderRepository.save(order);
        
        // Send notification
        notificationService.sendOrderConfirmation(
            order.getCustomerId(),
            order.getId()
        );
        
        return new PlaceOrderResponse(
            order.getId().toString(),
            total.getAmount(),
            total.getCurrency()
        );
    }
    
    private List<OrderItem> buildOrderItems(List<OrderItemRequest> items) {
        // Implementation...
        return new ArrayList<>();
    }
}

// ===== INFRASTRUCTURE LAYER =====

// Outbound Adapter - JPA Repository
@Repository
public class JpaOrderRepository implements OrderRepository {
    private final EntityManager entityManager;
    
    public JpaOrderRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }
    
    @Override
    @Transactional
    public void save(Order order) {
        OrderEntity entity = toEntity(order);
        entityManager.persist(entity);
    }
    
    @Override
    public Optional<Order> findById(OrderId id) {
        OrderEntity entity = entityManager.find(
            OrderEntity.class,
            id.toString()
        );
        return Optional.ofNullable(entity).map(this::toDomain);
    }
    
    private OrderEntity toEntity(Order order) {
        // Mapping logic...
        return new OrderEntity();
    }
    
    private Order toDomain(OrderEntity entity) {
        // Mapping logic...
        return null;
    }
}

// Inbound Adapter - Spring REST Controller
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final PlaceOrderUseCase placeOrderUseCase;
    
    public OrderController(PlaceOrderUseCase placeOrderUseCase) {
        this.placeOrderUseCase = placeOrderUseCase;
    }
    
    @PostMapping
    public ResponseEntity<PlaceOrderResponse> placeOrder(
        @RequestBody PlaceOrderRequest request
    ) {
        try {
            PlaceOrderResponse response = placeOrderUseCase.execute(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
}

// Spring Configuration
@Configuration
public class ApplicationConfig {
    @Bean
    public PlaceOrderUseCase placeOrderUseCase(
        OrderRepository orderRepository,
        PaymentGateway paymentGateway,
        NotificationService notificationService
    ) {
        return new PlaceOrderService(
            orderRepository,
            paymentGateway,
            notificationService
        );
    }
}
```

---

## Benefits Demonstrated

All three implementations demonstrate:

1. **SRP**: Each class has one responsibility
2. **OCP**: Easy to extend (add new gateways, repos)
3. **LSP**: All implementations are substitutable
4. **ISP**: Small, focused interfaces
5. **DIP**: High-level modules depend on abstractions

**Testing Benefits**:
- Easy to mock dependencies
- Test domain logic in isolation
- Swap implementations for tests

**Maintenance Benefits**:
- Changes localized to relevant classes
- Easy to understand each component
- Safe to refactor

**Flexibility Benefits**:
- Switch databases without changing business logic
- Add new payment providers easily
- Support multiple notification channels