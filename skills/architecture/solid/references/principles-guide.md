# SOLID Principles - Detailed Guide

## Table of Contents
1. [Single Responsibility Principle](#single-responsibility-principle)
2. [Open/Closed Principle](#openclosed-principle)
3. [Liskov Substitution Principle](#liskov-substitution-principle)
4. [Interface Segregation Principle](#interface-segregation-principle)
5. [Dependency Inversion Principle](#dependency-inversion-principle)

---

## Single Responsibility Principle (SRP)

### Formal Definition
A class should have one, and only one, reason to change.

### In-Depth Explanation

**What is a "Responsibility"?**
A responsibility is a reason to change. If you can think of more than one motive for changing a class, that class has more than one responsibility.

**Why One Responsibility?**
- Changes to one responsibility don't affect others
- Easier to understand and reason about
- Reduces coupling
- Improves testability

### Detailed Examples

#### Example 1: User Management

**❌ Violation:**
```typescript
class User {
  constructor(
    public id: string,
    public name: string,
    public email: string
  ) {}
  
  // Responsibility 1: User data validation
  validate(): boolean {
    return this.email.includes('@') && this.name.length > 0;
  }
  
  // Responsibility 2: Database persistence
  save(): void {
    const db = new Database();
    db.execute(`INSERT INTO users VALUES ('${this.id}', '${this.name}', '${this.email}')`);
  }
  
  // Responsibility 3: Email notification
  sendWelcomeEmail(): void {
    const emailer = new EmailService();
    emailer.send(this.email, 'Welcome!', 'Thanks for joining!');
  }
  
  // Responsibility 4: Logging
  logActivity(action: string): void {
    const logger = new Logger();
    logger.log(`User ${this.id} performed: ${action}`);
  }
  
  // Responsibility 5: Business logic
  applyDiscount(amount: number): number {
    return this.isPremium() ? amount * 0.9 : amount;
  }
  
  isPremium(): boolean {
    // Check premium status
    return true;
  }
}
```

**Problems:**
- Changes to database schema affect User class
- Changes to email templates affect User class
- Changes to logging format affect User class
- Difficult to test each responsibility in isolation
- High coupling to multiple external systems

**✅ Proper SRP Application:**
```typescript
// Responsibility 1: User entity (domain model)
class User {
  constructor(
    public readonly id: UserId,
    public name: string,
    public email: Email
  ) {}
  
  isPremium(): boolean {
    // Pure business logic only
    return true;
  }
  
  applyDiscount(amount: Money): Money {
    return this.isPremium() 
      ? amount.multiply(0.9) 
      : amount;
  }
}

// Responsibility 2: Validation
class UserValidator {
  validate(user: User): ValidationResult {
    const errors: string[] = [];
    
    if (!user.email.isValid()) {
      errors.push('Invalid email format');
    }
    
    if (user.name.length === 0) {
      errors.push('Name cannot be empty');
    }
    
    return errors.length === 0
      ? ValidationResult.success()
      : ValidationResult.failure(errors);
  }
}

// Responsibility 3: Database persistence
class UserRepository {
  constructor(private db: Database) {}
  
  async save(user: User): Promise<void> {
    await this.db.execute(
      'INSERT INTO users (id, name, email) VALUES (?, ?, ?)',
      [user.id.value, user.name, user.email.value]
    );
  }
  
  async findById(id: UserId): Promise<User | null> {
    const result = await this.db.query(
      'SELECT * FROM users WHERE id = ?',
      [id.value]
    );
    return result ? this.toDomain(result) : null;
  }
  
  private toDomain(row: any): User {
    return new User(
      new UserId(row.id),
      row.name,
      Email.create(row.email)
    );
  }
}

// Responsibility 4: Email notifications
class UserNotificationService {
  constructor(private emailService: EmailService) {}
  
  async sendWelcomeEmail(user: User): Promise<void> {
    await this.emailService.send({
      to: user.email.value,
      subject: 'Welcome!',
      body: this.getWelcomeTemplate(user.name)
    });
  }
  
  private getWelcomeTemplate(name: string): string {
    return `Hi ${name}, thanks for joining!`;
  }
}

// Responsibility 5: Activity logging
class UserActivityLogger {
  constructor(private logger: Logger) {}
  
  logActivity(userId: UserId, action: string): void {
    this.logger.info({
      userId: userId.value,
      action,
      timestamp: new Date()
    });
  }
}

// Usage (orchestrated by application service)
class RegisterUserService {
  constructor(
    private validator: UserValidator,
    private repository: UserRepository,
    private notifier: UserNotificationService,
    private activityLogger: UserActivityLogger
  ) {}
  
  async execute(request: RegisterUserRequest): Promise<void> {
    const user = new User(
      UserId.generate(),
      request.name,
      Email.create(request.email)
    );
    
    const validation = this.validator.validate(user);
    if (!validation.isValid) {
      throw new ValidationError(validation.errors);
    }
    
    await this.repository.save(user);
    await this.notifier.sendWelcomeEmail(user);
    this.activityLogger.logActivity(user.id, 'registered');
  }
}
```

**Benefits of Refactoring:**
- Each class has one reason to change
- Easy to test each responsibility independently
- Can swap implementations (e.g., different database)
- Changes isolated to relevant class

---

#### Example 2: Report Generation

**❌ Violation:**
```typescript
class SalesReport {
  generateReport(startDate: Date, endDate: Date): void {
    // Responsibility 1: Data retrieval
    const sales = this.fetchSalesData(startDate, endDate);
    
    // Responsibility 2: Calculations
    const total = sales.reduce((sum, sale) => sum + sale.amount, 0);
    const average = total / sales.length;
    
    // Responsibility 3: Formatting
    const formattedReport = this.formatAsHTML(sales, total, average);
    
    // Responsibility 4: Persistence
    this.saveToFile(formattedReport, 'report.html');
    
    // Responsibility 5: Notification
    this.emailReport(formattedReport);
  }
  
  private fetchSalesData(start: Date, end: Date) { /* ... */ }
  private formatAsHTML(data: any, total: number, avg: number) { /* ... */ }
  private saveToFile(content: string, filename: string) { /* ... */ }
  private emailReport(content: string) { /* ... */ }
}
```

**✅ Proper SRP:**
```typescript
// Data retrieval
class SalesDataRepository {
  async fetchSales(startDate: Date, endDate: Date): Promise<Sale[]> {
    // Database query logic
  }
}

// Calculations
class SalesCalculator {
  calculateMetrics(sales: Sale[]): SalesMetrics {
    const total = sales.reduce((sum, sale) => sum + sale.amount, 0);
    const average = sales.length > 0 ? total / sales.length : 0;
    const count = sales.length;
    
    return { total, average, count };
  }
}

// Formatting
interface ReportFormatter {
  format(sales: Sale[], metrics: SalesMetrics): string;
}

class HTMLReportFormatter implements ReportFormatter {
  format(sales: Sale[], metrics: SalesMetrics): string {
    return `
      <html>
        <h1>Sales Report</h1>
        <p>Total: ${metrics.total}</p>
        <p>Average: ${metrics.average}</p>
        <!-- ... -->
      </html>
    `;
  }
}

class PDFReportFormatter implements ReportFormatter {
  format(sales: Sale[], metrics: SalesMetrics): string {
    // PDF generation logic
  }
}

// Persistence
class ReportStorage {
  async save(content: string, filename: string): Promise<void> {
    // File system logic
  }
}

// Notification
class ReportDistributor {
  async email(recipient: string, content: string): Promise<void> {
    // Email logic
  }
}

// Orchestration
class GenerateSalesReportService {
  constructor(
    private dataRepo: SalesDataRepository,
    private calculator: SalesCalculator,
    private formatter: ReportFormatter,
    private storage: ReportStorage,
    private distributor: ReportDistributor
  ) {}
  
  async execute(request: GenerateReportRequest): Promise<void> {
    const sales = await this.dataRepo.fetchSales(
      request.startDate,
      request.endDate
    );
    
    const metrics = this.calculator.calculateMetrics(sales);
    const formatted = this.formatter.format(sales, metrics);
    
    await this.storage.save(formatted, request.filename);
    
    if (request.emailTo) {
      await this.distributor.email(request.emailTo, formatted);
    }
  }
}
```

---

### Identifying SRP Violations

**Red Flags:**
1. Class name contains "And", "Manager", "Helper", "Utility"
2. Class has many dependencies
3. Class has methods from different domains
4. Changes in one area affect unrelated methods
5. Difficult to write a concise class description

**Exercise: Spot the Violations**
```typescript
class OrderManager {
  validateOrder(order: Order) { }
  calculateTax(order: Order) { }
  saveToDatabase(order: Order) { }
  sendConfirmationEmail(order: Order) { }
  generateInvoicePDF(order: Order) { }
  processRefund(order: Order) { }
  checkInventory(order: Order) { }
}
```

**Violations:** All of them! This class has at least 7 responsibilities.

---

## Open/Closed Principle (OCP)

### Formal Definition
Software entities (classes, modules, functions) should be open for extension but closed for modification.

### In-Depth Explanation

**Open for Extension:**
You can add new functionality to a module.

**Closed for Modification:**
Existing code should not be changed when adding new functionality.

**How to Achieve:**
- Use abstraction (interfaces/abstract classes)
- Use polymorphism
- Use composition over inheritance
- Use design patterns (Strategy, Template Method, etc.)

### Detailed Examples

#### Example 1: Payment Processing

**❌ Violation:**
```typescript
class PaymentProcessor {
  processPayment(amount: number, method: string): void {
    if (method === 'credit_card') {
      // Process credit card
      console.log('Processing credit card payment');
      this.validateCreditCard();
      this.chargeCreditCard(amount);
    } else if (method === 'paypal') {
      // Process PayPal
      console.log('Processing PayPal payment');
      this.validatePayPalAccount();
      this.chargePayPal(amount);
    } else if (method === 'bitcoin') {
      // Process Bitcoin
      console.log('Processing Bitcoin payment');
      this.validateBitcoinWallet();
      this.chargeBitcoin(amount);
    } else if (method === 'bank_transfer') {
      // Need to modify this class AGAIN
      console.log('Processing bank transfer');
      this.validateBankAccount();
      this.chargeBankTransfer(amount);
    }
  }
  
  // Need to add more methods for each payment type
  private validateCreditCard() { }
  private chargeCreditCard(amount: number) { }
  private validatePayPalAccount() { }
  private chargePayPal(amount: number) { }
  // ... and so on
}
```

**Problems:**
- Every new payment method requires modifying this class
- Risk of breaking existing functionality
- Class grows indefinitely
- Violates SRP too (handles all payment types)

**✅ Proper OCP:**
```typescript
// Abstraction
interface PaymentMethod {
  validate(): Promise<boolean>;
  charge(amount: Money): Promise<PaymentResult>;
}

// Concrete implementations (extensions)
class CreditCardPayment implements PaymentMethod {
  constructor(
    private cardNumber: string,
    private cvv: string,
    private expiryDate: string
  ) {}
  
  async validate(): Promise<boolean> {
    // Credit card validation logic
    return this.cardNumber.length === 16;
  }
  
  async charge(amount: Money): Promise<PaymentResult> {
    // Credit card charging logic
    return PaymentResult.success('txn_123');
  }
}

class PayPalPayment implements PaymentMethod {
  constructor(private email: string) {}
  
  async validate(): Promise<boolean> {
    // PayPal validation
    return this.email.includes('@');
  }
  
  async charge(amount: Money): Promise<PaymentResult> {
    // PayPal charging logic
    return PaymentResult.success('pp_456');
  }
}

class BitcoinPayment implements PaymentMethod {
  constructor(private walletAddress: string) {}
  
  async validate(): Promise<boolean> {
    // Bitcoin validation
    return this.walletAddress.length === 34;
  }
  
  async charge(amount: Money): Promise<PaymentResult> {
    // Bitcoin charging logic
    return PaymentResult.success('btc_789');
  }
}

// Closed for modification, open for extension
class PaymentProcessor {
  async process(method: PaymentMethod, amount: Money): Promise<void> {
    const isValid = await method.validate();
    if (!isValid) {
      throw new Error('Invalid payment method');
    }
    
    const result = await method.charge(amount);
    if (!result.isSuccessful) {
      throw new Error('Payment failed');
    }
    
    console.log(`Payment successful: ${result.transactionId}`);
  }
}

// Usage - Adding new payment method without modifying PaymentProcessor
class ApplePayPayment implements PaymentMethod {
  constructor(private token: string) {}
  
  async validate(): Promise<boolean> {
    return this.token.length > 0;
  }
  
  async charge(amount: Money): Promise<PaymentResult> {
    // Apple Pay logic
    return PaymentResult.success('ap_999');
  }
}

// No changes needed to PaymentProcessor!
const processor = new PaymentProcessor();
await processor.process(new ApplePayPayment('token'), Money.dollars(100));
```

**Benefits:**
- Add new payment methods without touching PaymentProcessor
- Existing code remains stable and tested
- Each payment method is independent
- Easy to test each payment type

---

#### Example 2: Discount Calculation

**❌ Violation:**
```typescript
class DiscountCalculator {
  calculate(customer: Customer, order: Order): number {
    if (customer.type === 'regular') {
      return order.total * 0.05; // 5% discount
    } else if (customer.type === 'premium') {
      return order.total * 0.10; // 10% discount
    } else if (customer.type === 'vip') {
      return order.total * 0.20; // 20% discount
    } else if (customer.type === 'employee') {
      // New requirement - must modify this class
      return order.total * 0.30; // 30% discount
    }
    return 0;
  }
}
```

**✅ Proper OCP with Strategy Pattern:**
```typescript
// Strategy interface
interface DiscountStrategy {
  calculate(orderTotal: Money): Money;
}

// Concrete strategies
class NoDiscount implements DiscountStrategy {
  calculate(orderTotal: Money): Money {
    return Money.zero(orderTotal.currency);
  }
}

class PercentageDiscount implements DiscountStrategy {
  constructor(private percentage: number) {}
  
  calculate(orderTotal: Money): Money {
    return orderTotal.multiply(this.percentage / 100);
  }
}

class FixedAmountDiscount implements DiscountStrategy {
  constructor(private amount: Money) {}
  
  calculate(orderTotal: Money): Money {
    return this.amount;
  }
}

class TieredDiscount implements DiscountStrategy {
  calculate(orderTotal: Money): Money {
    if (orderTotal.greaterThan(Money.dollars(1000))) {
      return orderTotal.multiply(0.20);
    } else if (orderTotal.greaterThan(Money.dollars(500))) {
      return orderTotal.multiply(0.10);
    } else {
      return orderTotal.multiply(0.05);
    }
  }
}

// Context
class Customer {
  constructor(
    public name: string,
    private discountStrategy: DiscountStrategy
  ) {}
  
  calculateDiscount(orderTotal: Money): Money {
    return this.discountStrategy.calculate(orderTotal);
  }
}

// Usage
const regularCustomer = new Customer('John', new PercentageDiscount(5));
const premiumCustomer = new Customer('Jane', new PercentageDiscount(10));
const vipCustomer = new Customer('Bob', new PercentageDiscount(20));
const employeeCustomer = new Customer('Alice', new PercentageDiscount(30));

// New discount type - no modification needed!
class SeasonalDiscount implements DiscountStrategy {
  calculate(orderTotal: Money): Money {
    const currentMonth = new Date().getMonth();
    const isHolidaySeason = currentMonth === 11 || currentMonth === 0;
    return isHolidaySeason 
      ? orderTotal.multiply(0.15) 
      : Money.zero(orderTotal.currency);
  }
}

const seasonalCustomer = new Customer('Charlie', new SeasonalDiscount());
```

---

### Achieving OCP

**Techniques:**

1. **Use Interfaces/Abstract Classes**
2. **Strategy Pattern** - Encapsulate algorithms
3. **Template Method Pattern** - Define skeleton, let subclasses override
4. **Decorator Pattern** - Add functionality without modification
5. **Dependency Injection** - Inject behaviors

**When to Apply:**
- Frequent changes expected in an area
- Multiple variants of behavior exist
- Need to support plugins/extensions

---

## Liskov Substitution Principle (LSP)

### Formal Definition
Objects of a superclass should be replaceable with objects of its subclasses without breaking the application.

### In-Depth Explanation

**Barbara Liskov's Original Definition (1988):**
"If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering any of the desirable properties of the program."

**Key Rules:**
1. Subclass must accept all inputs parent accepts
2. Subclass must produce all outputs parent produces
3. Subclass must not throw new exceptions parent doesn't
4. Preconditions cannot be strengthened
5. Postconditions cannot be weakened
6. Invariants must be preserved

### Detailed Examples

#### Example 1: Rectangle and Square Problem

**❌ Classic LSP Violation:**
```typescript
class Rectangle {
  constructor(
    protected width: number,
    protected height: number
  ) {}
  
  setWidth(width: number): void {
    this.width = width;
  }
  
  setHeight(height: number): void {
    this.height = height;
  }
  
  getArea(): number {
    return this.width * this.height;
  }
}

class Square extends Rectangle {
  constructor(size: number) {
    super(size, size);
  }
  
  // Square must have equal sides
  setWidth(width: number): void {
    this.width = width;
    this.height = width; // Maintain square invariant
  }
  
  setHeight(height: number): void {
    this.width = height; // Maintain square invariant
    this.height = height;
  }
}

// This breaks LSP!
function resizeRectangle(rect: Rectangle): void {
  rect.setWidth(5);
  rect.setHeight(10);
  
  // Expected: 50 (5 * 10)
  // With Square: 100 (10 * 10) - WRONG!
  console.log(rect.getArea());
}

const rect = new Rectangle(2, 3);
resizeRectangle(rect); // 50 ✓

const square = new Square(2);
resizeRectangle(square); // 100 ✗ - Violates LSP!
```

**✅ Proper LSP:**
```typescript
// Use composition, not inheritance
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape {
  constructor(
    private width: number,
    private height: number
  ) {}
  
  setWidth(width: number): void {
    this.width = width;
  }
  
  setHeight(height: number): void {
    this.height = height;
  }
  
  getArea(): number {
    return this.width * this.height;
  }
}

class Square implements Shape {
  constructor(private size: number) {}
  
  setSize(size: number): void {
    this.size = size;
  }
  
  getArea(): number {
    return this.size * this.size;
  }
}

// Now both shapes can be used polymorphically
function calculateTotalArea(shapes: Shape[]): number {
  return shapes.reduce((total, shape) => total + shape.getArea(), 0);
}

const shapes: Shape[] = [
  new Rectangle(5, 10),
  new Square(7)
];

console.log(calculateTotalArea(shapes)); // Works correctly!
```

---

#### Example 2: Bird Hierarchy

**❌ Violation:**
```typescript
class Bird {
  fly(): void {
    console.log('Flying...');
  }
}

class Sparrow extends Bird {
  // Sparrow can fly
}

class Penguin extends Bird {
  fly(): void {
    throw new Error('Penguins cannot fly!'); // Violates LSP
  }
}

class Ostrich extends Bird {
  fly(): void {
    throw new Error('Ostriches cannot fly!'); // Violates LSP
  }
}

function makeBirdFly(bird: Bird): void {
  bird.fly(); // Will crash with Penguin or Ostrich!
}
```

**✅ Proper LSP:**
```typescript
// Split into appropriate abstractions
interface Bird {
  eat(): void;
  sleep(): void;
}

interface FlyingBird extends Bird {
  fly(): void;
}

interface SwimmingBird extends Bird {
  swim(): void;
}

class Sparrow implements FlyingBird {
  eat(): void { console.log('Eating seeds'); }
  sleep(): void { console.log('Sleeping in nest'); }
  fly(): void { console.log('Flying high'); }
}

class Penguin implements SwimmingBird {
  eat(): void { console.log('Eating fish'); }
  sleep(): void { console.log('Sleeping on ice'); }
  swim(): void { console.log('Swimming fast'); }
}

class Duck implements FlyingBird, SwimmingBird {
  eat(): void { console.log('Eating'); }
  sleep(): void { console.log('Sleeping'); }
  fly(): void { console.log('Flying'); }
  swim(): void { console.log('Swimming'); }
}

// Now type-safe functions
function makeFly(bird: FlyingBird): void {
  bird.fly(); // Only flying birds accepted
}

function makeSwim(bird: SwimmingBird): void {
  bird.swim(); // Only swimming birds accepted
}

// Usage
makeFly(new Sparrow()); // ✓
makeFly(new Duck()); // ✓
// makeFly(new Penguin()); // Compile error ✓

makeSwim(new Penguin()); // ✓
makeSwim(new Duck()); // ✓
// makeSwim(new Sparrow()); // Compile error ✓
```

---

### LSP Contract Rules

**Preconditions** (inputs):
- Subclass cannot strengthen (make stricter)
- Can weaken (accept more inputs)

**Postconditions** (outputs):
- Subclass cannot weaken (return less)
- Can strengthen (guarantee more)

**Example:**
```typescript
class EmailSender {
  // Precondition: email must be valid
  // Postcondition: returns success boolean
  send(email: string): boolean {
    if (!this.isValidEmail(email)) {
      throw new Error('Invalid email');
    }
    // Send email
    return true;
  }
  
  protected isValidEmail(email: string): boolean {
    return email.includes('@');
  }
}

// ❌ Bad: Strengthens precondition
class StrictEmailSender extends EmailSender {
  protected isValidEmail(email: string): boolean {
    // Now requires domain verification too - stricter!
    return super.isValidEmail(email) && 
           email.endsWith('.com'); // Violates LSP
  }
}

// ✅ Good: Weakens precondition
class LenientEmailSender extends EmailSender {
  protected isValidEmail(email: string): boolean {
    // Accepts more inputs - OK!
    return email.length > 0; // Weaker condition
  }
}
```

---

## Interface Segregation Principle (ISP)

### Formal Definition
No client should be forced to depend on methods it does not use.

### In-Depth Explanation

**Problem:** Fat interfaces force clients to depend on methods they don't need.

**Solution:** Many specific interfaces instead of one general-purpose interface.

**Benefits:**
- Reduces coupling
- Improves cohesion
- Easier to implement
- Better separation of concerns

### Detailed Examples

#### Example 1: Worker Interface

**❌ Violation:**
```typescript
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
  getDailyReport(): Report;
}

class HumanWorker implements Worker {
  work(): void { console.log('Working...'); }
  eat(): void { console.log('Eating lunch...'); }
  sleep(): void { console.log('Sleeping...'); }
  getDailyReport(): Report { return new Report(); }
}

class RobotWorker implements Worker {
  work(): void { console.log('Working...'); }
  
  // Robots don't eat!
  eat(): void {
    throw new Error('Robots do not eat!');
  }
  
  // Robots don't sleep!
  sleep(): void {
    throw new Error('Robots do not sleep!');
  }
  
  getDailyReport(): Report { return new Report(); }
}

class Manager {
  constructor(private worker: Worker) {}
  
  manageLunchBreak(): void {
    this.worker.eat(); // Breaks with RobotWorker!
  }
}
```

**✅ Proper ISP:**
```typescript
// Segregated interfaces
interface Workable {
  work(): void;
}

interface Feedable {
  eat(): void;
}

interface Restable {
  sleep(): void;
}

interface Reportable {
  getDailyReport(): Report;
}

// Humans implement all interfaces
class HumanWorker implements Workable, Feedable, Restable, Reportable {
  work(): void { console.log('Working...'); }
  eat(): void { console.log('Eating lunch...'); }
  sleep(): void { console.log('Sleeping...'); }
  getDailyReport(): Report { return new Report(); }
}

// Robots only implement what they can do
class RobotWorker implements Workable, Reportable {
  work(): void { console.log('Working...'); }
  getDailyReport(): Report { return new Report(); }
}

// Managers work with specific interfaces
class WorkManager {
  manageWork(worker: Workable): void {
    worker.work();
  }
}

class BreakManager {
  manageLunch(worker: Feedable): void {
    worker.eat(); // Only callable with Feedable workers
  }
  
  manageNap(worker: Restable): void {
    worker.sleep(); // Only callable with Restable workers
  }
}

// Usage
const human = new HumanWorker();
const robot = new RobotWorker();

const workMgr = new WorkManager();
workMgr.manageWork(human); // ✓
workMgr.manageWork(robot); // ✓

const breakMgr = new BreakManager();
breakMgr.manageLunch(human); // ✓
// breakMgr.manageLunch(robot); // Compile error ✓ - Good!
```

---

#### Example 2: Document Interface

**❌ Violation:**
```typescript
interface Document {
  open(): void;
  close(): void;
  save(): void;
  print(): void;
  fax(): void;
  scan(): void;
  email(): void;
}

class ModernDocument implements Document {
  open(): void { /* ... */ }
  close(): void { /* ... */ }
  save(): void { /* ... */ }
  print(): void { /* ... */ }
  fax(): void { /* ... */ }
  scan(): void { /* ... */ }
  email(): void { /* ... */ }
}

class ReadOnlyDocument implements Document {
  open(): void { /* ... */ }
  close(): void { /* ... */ }
  
  save(): void {
    throw new Error('Cannot save read-only document!');
  }
  
  print(): void { /* Can print */ }
  fax(): void { throw new Error('Cannot fax!'); }
  scan(): void { throw new Error('Cannot scan!'); }
  email(): void { throw new Error('Cannot email!'); }
}
```

**✅ Proper ISP:**
```typescript
// Segregated interfaces
interface Openable {
  open(): void;
  close(): void;
}

interface Savable {
  save(): void;
}

interface Printable {
  print(): void;
}

interface Faxable {
  fax(): void;
}

interface Scannable {
  scan(): void;
}

interface Emailable {
  email(): void;
}

// Full-featured document
class EditableDocument implements 
  Openable, Savable, Printable, Faxable, Scannable, Emailable {
  open(): void { /* ... */ }
  close(): void { /* ... */ }
  save(): void { /* ... */ }
  print(): void { /* ... */ }
  fax(): void { /* ... */ }
  scan(): void { /* ... */ }
  email(): void { /* ... */ }
}

// Read-only document - only implements what it can do
class ReadOnlyDocument implements Openable, Printable {
  open(): void { /* ... */ }
  close(): void { /* ... */ }
  print(): void { /* ... */ }
}

// PDF document
class PDFDocument implements Openable, Printable, Emailable {
  open(): void { /* ... */ }
  close(): void { /* ... */ }
  print(): void { /* ... */ }
  email(): void { /* ... */ }
}

// Clients depend only on what they need
class DocumentPrinter {
  print(doc: Printable): void {
    doc.print();
  }
}

class DocumentSaver {
  save(doc: Savable): void {
    doc.save();
  }
}

// Usage
const editable = new EditableDocument();
const readOnly = new ReadOnlyDocument();
const pdf = new PDFDocument();

const printer = new DocumentPrinter();
printer.print(editable); // ✓
printer.print(readOnly); // ✓
printer.print(pdf); // ✓

const saver = new DocumentSaver();
saver.save(editable); // ✓
// saver.save(readOnly); // Compile error ✓ - Prevents runtime error!
```

---

## Dependency Inversion Principle (DIP)

### Formal Definition
1. High-level modules should not depend on low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

### In-Depth Explanation

**Traditional Dependency Flow:**
High-Level → Low-Level

**Inverted Dependency Flow:**
High-Level → Abstraction ← Low-Level

**Key Concepts:**
- Depend on interfaces, not concrete classes
- Inject dependencies (don't create them)
- Inversion of Control (IoC)

### Detailed Examples

#### Example 1: Notification System

**❌ Violation:**
```typescript
// Low-level module
class EmailService {
  sendEmail(to: string, subject: string, body: string): void {
    console.log(`Sending email to ${to}`);
    // SMTP logic
  }
}

// High-level module depends on low-level
class UserRegistrationService {
  private emailService = new EmailService(); // Direct dependency
  
  registerUser(user: User): void {
    // Registration logic
    this.saveUser(user);
    
    // Tightly coupled to EmailService
    this.emailService.sendEmail(
      user.email,
      'Welcome!',
      'Thanks for registering'
    );
  }
  
  private saveUser(user: User): void { /* ... */ }
}
```

**Problems:**
- Hard to test (can't mock EmailService)
- Can't switch to SMS or Push notifications easily
- UserRegistrationService knows concrete EmailService

**✅ Proper DIP:**
```typescript
// Abstraction (interface)
interface NotificationService {
  send(recipient: string, message: string): Promise<void>;
}

// Low-level modules implement abstraction
class EmailNotificationService implements NotificationService {
  constructor(private smtpConfig: SMTPConfig) {}
  
  async send(recipient: string, message: string): Promise<void> {
    console.log(`Sending email to ${recipient}`);
    // SMTP logic
  }
}

class SMSNotificationService implements NotificationService {
  constructor(private twilioClient: TwilioClient) {}
  
  async send(recipient: string, message: string): Promise<void> {
    console.log(`Sending SMS to ${recipient}`);
    // Twilio API logic
  }
}

class PushNotificationService implements NotificationService {
  constructor(private firebaseClient: FirebaseClient) {}
  
  async send(recipient: string, message: string): Promise<void> {
    console.log(`Sending push notification to ${recipient}`);
    // Firebase logic
  }
}

// High-level module depends on abstraction
class UserRegistrationService {
  constructor(
    private notificationService: NotificationService // Injected dependency
  ) {}
  
  async registerUser(user: User): Promise<void> {
    await this.saveUser(user);
    
    // Uses abstraction, doesn't know concrete implementation
    await this.notificationService.send(
      user.email,
      'Welcome! Thanks for registering'
    );
  }
  
  private async saveUser(user: User): Promise<void> { /* ... */ }
}

// Usage - Easy to swap implementations
const emailService = new EmailNotificationService(smtpConfig);
const registrationService1 = new UserRegistrationService(emailService);

const smsService = new SMSNotificationService(twilioClient);
const registrationService2 = new UserRegistrationService(smsService);

// Testing - Easy to mock
const mockNotification: NotificationService = {
  send: jest.fn()
};
const testService = new UserRegistrationService(mockNotification);
```

---

#### Example 2: Data Access Layer

**❌ Violation:**
```typescript
// Low-level module
class MySQLDatabase {
  query(sql: string): any[] {
    console.log('Executing MySQL query');
    // MySQL-specific logic
    return [];
  }
}

// High-level module depends on MySQL directly
class UserService {
  private database = new MySQLDatabase(); // Concrete dependency
  
  getUsers(): User[] {
    const rows = this.database.query('SELECT * FROM users');
    return rows.map(row => this.toUser(row));
  }
  
  private toUser(row: any): User {
    return new User(row.id, row.name, row.email);
  }
}
```

**Problems:**
- Locked into MySQL
- Can't test without MySQL database
- Can't switch to PostgreSQL, MongoDB, etc.

**✅ Proper DIP:**
```typescript
// Abstraction
interface UserRepository {
  findAll(): Promise<User[]>;
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<void>;
}

// Low-level modules implement abstraction
class MySQLUserRepository implements UserRepository {
  constructor(private connection: MySQLConnection) {}
  
  async findAll(): Promise<User[]> {
    const rows = await this.connection.query('SELECT * FROM users');
    return rows.map(row => this.toDomain(row));
  }
  
  async findById(id: string): Promise<User | null> {
    const rows = await this.connection.query(
      'SELECT * FROM users WHERE id = ?',
      [id]
    );
    return rows.length > 0 ? this.toDomain(rows[0]) : null;
  }
  
  async save(user: User): Promise<void> {
    await this.connection.query(
      'INSERT INTO users (id, name, email) VALUES (?, ?, ?)',
      [user.id, user.name, user.email]
    );
  }
  
  async delete(id: string): Promise<void> {
    await this.connection.query('DELETE FROM users WHERE id = ?', [id]);
  }
  
  private toDomain(row: any): User {
    return new User(row.id, row.name, row.email);
  }
}

class MongoUserRepository implements UserRepository {
  constructor(private collection: MongoCollection) {}
  
  async findAll(): Promise<User[]> {
    const docs = await this.collection.find({}).toArray();
    return docs.map(doc => this.toDomain(doc));
  }
  
  async findById(id: string): Promise<User | null> {
    const doc = await this.collection.findOne({ _id: id });
    return doc ? this.toDomain(doc) : null;
  }
  
  async save(user: User): Promise<void> {
    await this.collection.insertOne({
      _id: user.id,
      name: user.name,
      email: user.email
    });
  }
  
  async delete(id: string): Promise<void> {
    await this.collection.deleteOne({ _id: id });
  }
  
  private toDomain(doc: any): User {
    return new User(doc._id, doc.name, doc.email);
  }
}

class InMemoryUserRepository implements UserRepository {
  private users: Map<string, User> = new Map();
  
  async findAll(): Promise<User[]> {
    return Array.from(this.users.values());
  }
  
  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }
  
  async save(user: User): Promise<void> {
    this.users.set(user.id, user);
  }
  
  async delete(id: string): Promise<void> {
    this.users.delete(id);
  }
}

// High-level module depends on abstraction
class UserService {
  constructor(private repository: UserRepository) {} // Injected
  
  async getUsers(): Promise<User[]> {
    return await this.repository.findAll();
  }
  
  async getUserById(id: string): Promise<User | null> {
    return await this.repository.findById(id);
  }
}

// Usage - Easy to swap
const mysqlRepo = new MySQLUserRepository(mysqlConnection);
const service1 = new UserService(mysqlRepo);

const mongoRepo = new MongoUserRepository(mongoCollection);
const service2 = new UserService(mongoRepo);

// Testing - Use in-memory
const testRepo = new InMemoryUserRepository();
const testService = new UserService(testRepo);
```

---

### Dependency Injection Patterns

**Constructor Injection (Preferred):**
```typescript
class OrderService {
  constructor(
    private repository: OrderRepository,
    private payment: PaymentGateway,
    private notifier: NotificationService
  ) {}
}
```

**Property Injection:**
```typescript
class OrderService {
  repository!: OrderRepository;
  payment!: PaymentGateway;
  
  // Set after construction
}
```

**Method Injection:**
```typescript
class OrderService {
  processOrder(
    order: Order,
    payment: PaymentGateway // Injected per method call
  ): void {
    payment.charge(order.total);
  }
}
```

---

### IoC Containers

**Manual DI:**
```typescript
const repository = new MySQLOrderRepository(connection);
const payment = new StripePaymentGateway(apiKey);
const notifier = new EmailNotificationService(smtp);
const orderService = new OrderService(repository, payment, notifier);
```

**With Container (e.g., InversifyJS):**
```typescript
container.bind<OrderRepository>(TYPES.OrderRepository)
  .to(MySQLOrderRepository);
  
container.bind<PaymentGateway>(TYPES.PaymentGateway)
  .to(StripePaymentGateway);
  
container.bind<NotificationService>(TYPES.NotificationService)
  .to(EmailNotificationService);
  
container.bind<OrderService>(TYPES.OrderService)
  .to(OrderService);

// Automatic resolution
const orderService = container.get<OrderService>(TYPES.OrderService);
```

---

## Summary

**SOLID Benefits:**
- **Maintainability**: Easier to understand and change
- **Testability**: Simple to mock and test
- **Flexibility**: Easy to extend and adapt
- **Reusability**: Components can be reused
- **Reduced Coupling**: Components are independent

**When to Apply:**
- During initial design
- When refactoring legacy code
- When code smells appear
- Before significant changes

**Balance:** Don't over-engineer for hypothetical future needs. Apply SOLID when it solves real problems.