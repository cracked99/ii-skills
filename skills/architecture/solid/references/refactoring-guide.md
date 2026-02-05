# SOLID Principles - Refactoring Guide

## Table of Contents
1. [Refactoring Process](#refactoring-process)
2. [Refactoring to SRP](#refactoring-to-srp)
3. [Refactoring to OCP](#refactoring-to-ocp)
4. [Refactoring to LSP](#refactoring-to-lsp)
5. [Refactoring to ISP](#refactoring-to-isp)
6. [Refactoring to DIP](#refactoring-to-dip)
7. [Complete Refactoring Example](#complete-refactoring-example)

---

## Refactoring Process

### General Workflow

**Step 1: Add Tests (If Missing)**
Before refactoring, ensure tests exist to verify behavior doesn't change.

```typescript
// Write characterization tests
describe('UserManager', () => {
  it('should save user and send email', () => {
    const manager = new UserManager();
    manager.createUser('john@example.com', 'John');
    // Verify current behavior
  });
});
```

**Step 2: Identify Violations**
Look for code smells and SOLID violations.

**Step 3: Apply One Principle at a Time**
Don't try to fix everything at once. Focus on one principle per refactoring session.

**Step 4: Keep Tests Green**
Run tests after each small change. If tests fail, revert and try a smaller step.

**Step 5: Commit Frequently**
Commit after each successful refactoring step.

**Step 6: Review and Refine**
After applying SOLID, review for clarity and simplicity.

---

## Refactoring to SRP

### Identifying SRP Violations

**Code Smells**:
- Class with many dependencies
- Class with diverse method names
- Long classes (>300 lines)
- Classes with "And", "Manager", "Utility" in name
- Methods that operate on different subsets of class fields

### Example: God Class Refactoring

**Before (Violates SRP):**
```typescript
class UserManager {
  createUser(email: string, password: string, name: string): void {
    // Validation
    if (!email.includes('@')) {
      throw new Error('Invalid email');
    }
    if (password.length < 8) {
      throw new Error('Password too short');
    }
    
    // Password hashing
    const bcrypt = require('bcrypt');
    const hashedPassword = bcrypt.hashSync(password, 10);
    
    // Database saving
    const db = new Database();
    db.execute(
      'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
      [email, hashedPassword, name]
    );
    
    // Email sending
    const emailer = new EmailService();
    emailer.send(email, 'Welcome!', 'Thanks for joining!');
    
    // Logging
    const logger = new Logger();
    logger.log(`User created: ${email}`);
    
    // Analytics
    const analytics = new Analytics();
    analytics.track('user_created', { email, name });
  }
}
```

**Refactoring Steps**:

**Step 1: Extract Validation**
```typescript
class UserValidator {
  validate(email: string, password: string): void {
    if (!email.includes('@')) {
      throw new Error('Invalid email');
    }
    if (password.length < 8) {
      throw new Error('Password too short');
    }
  }
}

class UserManager {
  private validator = new UserValidator();
  
  createUser(email: string, password: string, name: string): void {
    this.validator.validate(email, password);
    
    // Rest of the code...
  }
}
```

**Step 2: Extract Password Hashing**
```typescript
class PasswordHasher {
  hash(password: string): string {
    const bcrypt = require('bcrypt');
    return bcrypt.hashSync(password, 10);
  }
}

class UserManager {
  private validator = new UserValidator();
  private hasher = new PasswordHasher();
  
  createUser(email: string, password: string, name: string): void {
    this.validator.validate(email, password);
    const hashedPassword = this.hasher.hash(password);
    
    // Rest of the code...
  }
}
```

**Step 3: Extract Database Persistence**
```typescript
class UserRepository {
  save(email: string, hashedPassword: string, name: string): void {
    const db = new Database();
    db.execute(
      'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
      [email, hashedPassword, name]
    );
  }
}

class UserManager {
  private validator = new UserValidator();
  private hasher = new PasswordHasher();
  private repository = new UserRepository();
  
  createUser(email: string, password: string, name: string): void {
    this.validator.validate(email, password);
    const hashedPassword = this.hasher.hash(password);
    this.repository.save(email, hashedPassword, name);
    
    // Rest of the code...
  }
}
```

**Step 4: Extract Email Notification**
```typescript
class UserNotifier {
  sendWelcomeEmail(email: string): void {
    const emailer = new EmailService();
    emailer.send(email, 'Welcome!', 'Thanks for joining!');
  }
}

class UserManager {
  private validator = new UserValidator();
  private hasher = new PasswordHasher();
  private repository = new UserRepository();
  private notifier = new UserNotifier();
  
  createUser(email: string, password: string, name: string): void {
    this.validator.validate(email, password);
    const hashedPassword = this.hasher.hash(password);
    this.repository.save(email, hashedPassword, name);
    this.notifier.sendWelcomeEmail(email);
    
    // Rest of the code...
  }
}
```

**Step 5: Extract Logging and Analytics**
```typescript
class UserActivityLogger {
  logCreation(email: string): void {
    const logger = new Logger();
    logger.log(`User created: ${email}`);
  }
}

class UserAnalytics {
  trackCreation(email: string, name: string): void {
    const analytics = new Analytics();
    analytics.track('user_created', { email, name });
  }
}

// Final orchestrator - now has single responsibility of coordinating
class CreateUserService {
  constructor(
    private validator: UserValidator,
    private hasher: PasswordHasher,
    private repository: UserRepository,
    private notifier: UserNotifier,
    private activityLogger: UserActivityLogger,
    private analytics: UserAnalytics
  ) {}
  
  execute(email: string, password: string, name: string): void {
    this.validator.validate(email, password);
    const hashedPassword = this.hasher.hash(password);
    this.repository.save(email, hashedPassword, name);
    this.notifier.sendWelcomeEmail(email);
    this.activityLogger.logCreation(email);
    this.analytics.trackCreation(email, name);
  }
}
```

**After (Follows SRP):**
Each class now has exactly one reason to change:
- `UserValidator` - Validation logic changes
- `PasswordHasher` - Hashing algorithm changes
- `UserRepository` - Database schema changes
- `UserNotifier` - Email template changes
- `UserActivityLogger` - Logging format changes
- `UserAnalytics` - Analytics provider changes
- `CreateUserService` - Coordination logic changes

---

## Refactoring to OCP

### Identifying OCP Violations

**Code Smells**:
- Long if/else or switch statements checking types
- Modifying existing class to add new features
- Type checking with instanceof or typeof

### Example: Type Checking Refactoring

**Before (Violates OCP):**
```typescript
class ReportGenerator {
  generate(data: any[], format: string): string {
    if (format === 'html') {
      return this.generateHTML(data);
    } else if (format === 'pdf') {
      return this.generatePDF(data);
    } else if (format === 'excel') {
      return this.generateExcel(data);
    } else if (format === 'csv') {
      // Need to modify this class to add CSV support
      return this.generateCSV(data);
    }
    throw new Error('Unknown format');
  }
  
  private generateHTML(data: any[]): string { /* ... */ }
  private generatePDF(data: any[]): string { /* ... */ }
  private generateExcel(data: any[]): string { /* ... */ }
  private generateCSV(data: any[]): string { /* ... */ }
}
```

**Refactoring Steps**:

**Step 1: Define Interface**
```typescript
interface ReportFormatter {
  format(data: any[]): string;
}
```

**Step 2: Extract Each Format**
```typescript
class HTMLReportFormatter implements ReportFormatter {
  format(data: any[]): string {
    // HTML generation logic
    return '<html>...</html>';
  }
}

class PDFReportFormatter implements ReportFormatter {
  format(data: any[]): string {
    // PDF generation logic
    return 'PDF binary data';
  }
}

class ExcelReportFormatter implements ReportFormatter {
  format(data: any[]): string {
    // Excel generation logic
    return 'Excel binary data';
  }
}
```

**Step 3: Use Strategy Pattern**
```typescript
class ReportGenerator {
  constructor(private formatter: ReportFormatter) {}
  
  generate(data: any[]): string {
    return this.formatter.format(data);
  }
}

// Usage
const htmlGenerator = new ReportGenerator(new HTMLReportFormatter());
const pdfGenerator = new ReportGenerator(new PDFReportFormatter());

// Adding CSV - no modification needed!
class CSVReportFormatter implements ReportFormatter {
  format(data: any[]): string {
    // CSV generation logic
    return 'CSV data';
  }
}

const csvGenerator = new ReportGenerator(new CSVReportFormatter());
```

**Alternative: Factory Pattern**
```typescript
class ReportFormatterFactory {
  private formatters = new Map<string, ReportFormatter>();
  
  constructor() {
    this.register('html', new HTMLReportFormatter());
    this.register('pdf', new PDFReportFormatter());
    this.register('excel', new ExcelReportFormatter());
  }
  
  register(format: string, formatter: ReportFormatter): void {
    this.formatters.set(format, formatter);
  }
  
  create(format: string): ReportFormatter {
    const formatter = this.formatters.get(format);
    if (!formatter) {
      throw new Error(`Unknown format: ${format}`);
    }
    return formatter;
  }
}

// Usage
const factory = new ReportFormatterFactory();
const formatter = factory.create('html');
const generator = new ReportGenerator(formatter);

// Adding CSV
factory.register('csv', new CSVReportFormatter());
```

---

## Refactoring to LSP

### Identifying LSP Violations

**Code Smells**:
- Subclass throws exceptions parent doesn't
- Subclass has empty/stub methods
- Type checking before using polymorphism
- Subclass weakens postconditions or strengthens preconditions

### Example: Rectangle/Square Refactoring

**Before (Violates LSP):**
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
  setWidth(width: number): void {
    this.width = width;
    this.height = width; // Breaks LSP
  }
  
  setHeight(height: number): void {
    this.width = height; // Breaks LSP
    this.height = height;
  }
}

// This breaks with Square!
function resizeRectangle(rect: Rectangle): void {
  rect.setWidth(5);
  rect.setHeight(10);
  console.log(rect.getArea()); // Expected 50, got 100 with Square
}
```

**Refactoring Steps**:

**Step 1: Identify the Problem**
The problem is that Square and Rectangle have different invariants. Inheritance is wrong here.

**Step 2: Use Composition Instead**
```typescript
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
```

**Step 3: Use Polymorphism Correctly**
```typescript
function calculateTotalArea(shapes: Shape[]): number {
  return shapes.reduce((total, shape) => total + shape.getArea(), 0);
}

// Now both work correctly
const shapes: Shape[] = [
  new Rectangle(5, 10),
  new Square(7)
];
console.log(calculateTotalArea(shapes)); // Works!
```

---

## Refactoring to ISP

### Identifying ISP Violations

**Code Smells**:
- Interfaces with many methods (>5)
- Classes implementing interfaces with empty methods
- NotImplementedError exceptions
- Clients using only subset of interface

### Example: Fat Interface Refactoring

**Before (Violates ISP):**
```typescript
interface IMultiFunctionDevice {
  print(document: Document): void;
  scan(document: Document): void;
  fax(document: Document): void;
  copy(document: Document): void;
  email(document: Document): void;
}

class MultiFunctionPrinter implements IMultiFunctionDevice {
  print(doc: Document): void { /* ... */ }
  scan(doc: Document): void { /* ... */ }
  fax(doc: Document): void { /* ... */ }
  copy(doc: Document): void { /* ... */ }
  email(doc: Document): void { /* ... */ }
}

class SimplePrinter implements IMultiFunctionDevice {
  print(doc: Document): void { /* ... */ }
  
  // Forced to implement these
  scan(doc: Document): void {
    throw new Error('Scan not supported');
  }
  
  fax(doc: Document): void {
    throw new Error('Fax not supported');
  }
  
  copy(doc: Document): void {
    throw new Error('Copy not supported');
  }
  
  email(doc: Document): void {
    throw new Error('Email not supported');
  }
}
```

**Refactoring Steps**:

**Step 1: Segregate into Focused Interfaces**
```typescript
interface IPrinter {
  print(document: Document): void;
}

interface IScanner {
  scan(document: Document): void;
}

interface IFax {
  fax(document: Document): void;
}

interface ICopier {
  copy(document: Document): void;
}

interface IEmailer {
  email(document: Document): void;
}
```

**Step 2: Implement Only What's Needed**
```typescript
class SimplePrinter implements IPrinter {
  print(doc: Document): void {
    console.log('Printing...');
  }
}

class MultiFunctionDevice implements 
  IPrinter, IScanner, IFax, ICopier, IEmailer {
  print(doc: Document): void { /* ... */ }
  scan(doc: Document): void { /* ... */ }
  fax(doc: Document): void { /* ... */ }
  copy(doc: Document): void { /* ... */ }
  email(doc: Document): void { /* ... */ }
}

class PrinterScanner implements IPrinter, IScanner {
  print(doc: Document): void { /* ... */ }
  scan(doc: Document): void { /* ... */ }
}
```

**Step 3: Update Clients**
```typescript
// Before
function processDocument(device: IMultiFunctionDevice, doc: Document): void {
  device.print(doc); // What if device is SimplePrinter?
}

// After
function printDocument(printer: IPrinter, doc: Document): void {
  printer.print(doc);
}

function scanDocument(scanner: IScanner, doc: Document): void {
  scanner.scan(doc);
}
```

---

## Refactoring to DIP

### Identifying DIP Violations

**Code Smells**:
- `new` keyword scattered throughout code
- Direct imports of concrete classes
- Hard to write unit tests
- Tight coupling to specific implementations

### Example: Direct Dependencies Refactoring

**Before (Violates DIP):**
```typescript
class OrderService {
  processOrder(order: Order): void {
    // Direct dependencies on concrete classes
    const validator = new OrderValidator();
    const paymentProcessor = new StripePaymentProcessor();
    const emailService = new SendGridEmailService();
    const logger = new FileLogger();
    
    validator.validate(order);
    paymentProcessor.process(order.total);
    emailService.send(order.customerEmail, 'Order confirmed');
    logger.log(`Order ${order.id} processed`);
  }
}
```

**Refactoring Steps**:

**Step 1: Define Abstractions**
```typescript
interface OrderValidator {
  validate(order: Order): void;
}

interface PaymentProcessor {
  process(amount: number): void;
}

interface EmailService {
  send(to: string, message: string): void;
}

interface Logger {
  log(message: string): void;
}
```

**Step 2: Extract Concrete Implementations**
```typescript
class DefaultOrderValidator implements OrderValidator {
  validate(order: Order): void {
    // Validation logic
  }
}

class StripePaymentProcessor implements PaymentProcessor {
  process(amount: number): void {
    // Stripe-specific logic
  }
}

class SendGridEmailService implements EmailService {
  send(to: string, message: string): void {
    // SendGrid-specific logic
  }
}

class FileLogger implements Logger {
  log(message: string): void {
    // File logging logic
  }
}
```

**Step 3: Inject Dependencies**
```typescript
class OrderService {
  constructor(
    private validator: OrderValidator,
    private paymentProcessor: PaymentProcessor,
    private emailService: EmailService,
    private logger: Logger
  ) {}
  
  processOrder(order: Order): void {
    this.validator.validate(order);
    this.paymentProcessor.process(order.total);
    this.emailService.send(order.customerEmail, 'Order confirmed');
    this.logger.log(`Order ${order.id} processed`);
  }
}
```

**Step 4: Configure Dependencies**
```typescript
// Production configuration
const orderService = new OrderService(
  new DefaultOrderValidator(),
  new StripePaymentProcessor(),
  new SendGridEmailService(),
  new FileLogger()
);

// Test configuration
const testOrderService = new OrderService(
  new MockOrderValidator(),
  new MockPaymentProcessor(),
  new MockEmailService(),
  new MockLogger()
);

// Different payment provider
const paypalOrderService = new OrderService(
  new DefaultOrderValidator(),
  new PayPalPaymentProcessor(),  // Easy to swap!
  new SendGridEmailService(),
  new FileLogger()
);
```

---

## Complete Refactoring Example

### Legacy Code

```typescript
class UserController {
  handleRegistration(req: Request, res: Response): void {
    const { email, password, name } = req.body;
    
    // Validation
    if (!email || !password || !name) {
      res.status(400).json({ error: 'Missing fields' });
      return;
    }
    
    if (!email.includes('@')) {
      res.status(400).json({ error: 'Invalid email' });
      return;
    }
    
    if (password.length < 8) {
      res.status(400).json({ error: 'Password too short' });
      return;
    }
    
    // Check if user exists
    const db = new Database();
    const existingUser = db.query(
      'SELECT * FROM users WHERE email = ?',
      [email]
    );
    
    if (existingUser.length > 0) {
      res.status(409).json({ error: 'User already exists' });
      return;
    }
    
    // Hash password
    const bcrypt = require('bcrypt');
    const hashedPassword = bcrypt.hashSync(password, 10);
    
    // Save user
    db.execute(
      'INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
      [email, hashedPassword, name]
    );
    
    // Send welcome email
    const nodemailer = require('nodemailer');
    const transporter = nodemailer.createTransport({
      host: 'smtp.example.com',
      auth: { user: 'user', pass: 'pass' }
    });
    
    transporter.sendMail({
      to: email,
      subject: 'Welcome!',
      text: `Hi ${name}, welcome!`
    });
    
    // Log activity
    const fs = require('fs');
    fs.appendFileSync(
      'activity.log',
      `User registered: ${email}\n`
    );
    
    res.status(201).json({ message: 'User created' });
  }
}
```

### After Applying SOLID

```typescript
// ===== DOMAIN LAYER =====

class User {
  constructor(
    public readonly id: string,
    public readonly email: Email,
    public readonly passwordHash: PasswordHash,
    public readonly name: string
  ) {}
}

class Email {
  private constructor(private readonly value: string) {}
  
  static create(value: string): Email {
    if (!value.includes('@')) {
      throw new Error('Invalid email');
    }
    return new Email(value);
  }
  
  getValue(): string { return this.value; }
}

class PasswordHash {
  private constructor(private readonly hash: string) {}
  
  static fromPlaintext(plaintext: string): PasswordHash {
    if (plaintext.length < 8) {
      throw new Error('Password too short');
    }
    const bcrypt = require('bcrypt');
    const hash = bcrypt.hashSync(plaintext, 10);
    return new PasswordHash(hash);
  }
  
  getHash(): string { return this.hash; }
}

// ===== APPLICATION LAYER =====

// Inbound Port
interface RegisterUserUseCase {
  execute(request: RegisterUserRequest): Promise<void>;
}

interface RegisterUserRequest {
  email: string;
  password: string;
  name: string;
}

// Outbound Ports
interface UserRepository {
  existsByEmail(email: Email): Promise<boolean>;
  save(user: User): Promise<void>;
}

interface EmailService {
  sendWelcome(email: Email, name: string): Promise<void>;
}

interface ActivityLogger {
  logRegistration(email: Email): void;
}

// Application Service
class RegisterUserService implements RegisterUserUseCase {
  constructor(
    private repository: UserRepository,
    private emailService: EmailService,
    private logger: ActivityLogger
  ) {}
  
  async execute(request: RegisterUserRequest): Promise<void> {
    const email = Email.create(request.email);
    
    if (await this.repository.existsByEmail(email)) {
      throw new Error('User already exists');
    }
    
    const user = new User(
      crypto.randomUUID(),
      email,
      PasswordHash.fromPlaintext(request.password),
      request.name
    );
    
    await this.repository.save(user);
    await this.emailService.sendWelcome(email, request.name);
    this.logger.logRegistration(email);
  }
}

// ===== INFRASTRUCTURE LAYER =====

// Outbound Adapters
class DatabaseUserRepository implements UserRepository {
  constructor(private db: Database) {}
  
  async existsByEmail(email: Email): Promise<boolean> {
    const result = await this.db.query(
      'SELECT COUNT(*) as count FROM users WHERE email = ?',
      [email.getValue()]
    );
    return result[0].count > 0;
  }
  
  async save(user: User): Promise<void> {
    await this.db.execute(
      'INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)',
      [user.id, user.email.getValue(), user.passwordHash.getHash(), user.name]
    );
  }
}

class NodemailerEmailService implements EmailService {
  constructor(private transporter: any) {}
  
  async sendWelcome(email: Email, name: string): Promise<void> {
    await this.transporter.sendMail({
      to: email.getValue(),
      subject: 'Welcome!',
      text: `Hi ${name}, welcome!`
    });
  }
}

class FileActivityLogger implements ActivityLogger {
  logRegistration(email: Email): void {
    const fs = require('fs');
    fs.appendFileSync('activity.log', `User registered: ${email.getValue()}\n`);
  }
}

// Inbound Adapter - Controller
class UserController {
  constructor(private registerUserUseCase: RegisterUserUseCase) {}
  
  async handleRegistration(req: Request, res: Response): Promise<void> {
    try {
      await this.registerUserUseCase.execute({
        email: req.body.email,
        password: req.body.password,
        name: req.body.name
      });
      
      res.status(201).json({ message: 'User created' });
    } catch (error) {
      const message = (error as Error).message;
      
      if (message.includes('Invalid email') || 
          message.includes('Password too short')) {
        res.status(400).json({ error: message });
      } else if (message.includes('already exists')) {
        res.status(409).json({ error: message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}

// Dependency Injection
const db = new Database();
const transporter = createNodemailerTransporter();

const userRepository = new DatabaseUserRepository(db);
const emailService = new NodemailerEmailService(transporter);
const activityLogger = new FileActivityLogger();

const registerUserUseCase = new RegisterUserService(
  userRepository,
  emailService,
  activityLogger
);

const userController = new UserController(registerUserUseCase);
```

### Benefits Achieved

**Before:**
- 1 class, 100+ lines
- Hard to test (no mocking)
- Tightly coupled to database, email, logging
- Difficult to change any component

**After:**
- 15+ classes, each focused
- Easy to test (dependency injection)
- Loosely coupled
- Easy to swap implementations
- Follows all SOLID principles

---

## Refactoring Tips

### Start Small
Don't try to refactor everything at once. Start with the most painful area.

### Use IDE Refactorings
Modern IDEs have automated refactorings:
- Extract Method
- Extract Class
- Inline Method/Variable
- Rename
- Move

### Keep Tests Green
Run tests after each small change. If they fail, the step was too big.

### Commit Often
Commit after each successful refactoring step. Easy to revert if needed.

### Pair Programming
Refactoring is easier with a partner to discuss design decisions.

### Code Review
Have someone review your refactored code for clarity and SOLID compliance.

---

## Common Mistakes

### Over-Engineering
Don't create abstractions for hypothetical future needs. Refactor when you need it.

### Breaking Existing Functionality
Always maintain existing behavior during refactoring. Tests must pass.

### Refactoring Without Tests
Don't refactor without tests. How will you know you didn't break anything?

### Big Bang Refactoring
Don't try to refactor the entire codebase at once. Incremental is better.

### Ignoring the Boy Scout Rule
Leave code better than you found it. Small improvements add up.