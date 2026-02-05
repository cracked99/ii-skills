---
name: solid-principles
description: Apply SOLID object-oriented design principles for maintainable, flexible software. Use when designing classes, refactoring code, reviewing architecture, implementing clean code practices, or when code maintainability, testability, and extensibility are priorities. Triggers include requests for clean architecture, OOP best practices, design pattern implementation, code refactoring, or reducing coupling and increasing cohesion.
license: MIT
---

# SOLID Principles

## Overview

SOLID is an acronym for five fundamental object-oriented design principles that promote maintainable, flexible, and scalable software. Following SOLID principles leads to code that is easier to understand, test, modify, and extend.

**The Five Principles**:
- **S** - Single Responsibility Principle
- **O** - Open/Closed Principle
- **L** - Liskov Substitution Principle
- **I** - Interface Segregation Principle
- **D** - Dependency Inversion Principle

## The Five Principles Explained

### S - Single Responsibility Principle (SRP)

**Definition**: A class should have one, and only one, reason to change.

**Key Concept**: Each class should do one thing and do it well. If a class has multiple responsibilities, changes to one responsibility may affect the others.

**Quick Example**:
```typescript
// ❌ Bad - Multiple responsibilities
class User {
  saveToDatabase() { /* ... */ }
  sendEmail() { /* ... */ }
  generateReport() { /* ... */ }
}

// ✅ Good - Single responsibility per class
class User {
  constructor(public name: string, public email: string) {}
}

class UserRepository {
  save(user: User) { /* ... */ }
}

class EmailService {
  send(to: string, message: string) { /* ... */ }
}

class ReportGenerator {
  generate(user: User) { /* ... */ }
}
```

**Benefits**:
- Easier to understand and maintain
- Reduces coupling between components
- Easier to test in isolation
- Changes are localized

---

### O - Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification.

**Key Concept**: You should be able to add new functionality without changing existing code. Use abstraction and polymorphism to achieve this.

**Quick Example**:
```typescript
// ❌ Bad - Requires modification to add new shapes
class AreaCalculator {
  calculate(shape: any): number {
    if (shape.type === 'circle') {
      return Math.PI * shape.radius ** 2;
    } else if (shape.type === 'rectangle') {
      return shape.width * shape.height;
    }
    // Need to modify this class to add new shapes
  }
}

// ✅ Good - Open for extension, closed for modification
interface Shape {
  calculateArea(): number;
}

class Circle implements Shape {
  constructor(private radius: number) {}
  calculateArea(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  calculateArea(): number {
    return this.width * this.height;
  }
}

class AreaCalculator {
  calculate(shape: Shape): number {
    return shape.calculateArea(); // No modification needed for new shapes
  }
}
```

**Benefits**:
- Reduces risk when adding new features
- Existing code remains stable
- Easier to add new functionality
- Better separation of concerns

---

### L - Liskov Substitution Principle (LSP)

**Definition**: Objects of a superclass should be replaceable with objects of a subclass without breaking the application.

**Key Concept**: Derived classes must be substitutable for their base classes. Subclasses should extend, not replace, the behavior of base classes.

**Quick Example**:
```typescript
// ❌ Bad - Violates LSP
class Bird {
  fly() { /* ... */ }
}

class Penguin extends Bird {
  fly() {
    throw new Error('Penguins cannot fly!'); // Breaks LSP
  }
}

function makeBirdFly(bird: Bird) {
  bird.fly(); // Will fail with Penguin
}

// ✅ Good - Follows LSP
interface Bird {
  move(): void;
}

class FlyingBird implements Bird {
  fly() { /* ... */ }
  move() { this.fly(); }
}

class Penguin implements Bird {
  swim() { /* ... */ }
  move() { this.swim(); }
}

function makeBirdMove(bird: Bird) {
  bird.move(); // Works with all birds
}
```

**Benefits**:
- Predictable behavior
- Enables polymorphism
- Reduces unexpected errors
- Improves code reusability

---

### I - Interface Segregation Principle (ISP)

**Definition**: No client should be forced to depend on methods it does not use.

**Key Concept**: Many specific interfaces are better than one general-purpose interface. Keep interfaces focused and minimal.

**Quick Example**:
```typescript
// ❌ Bad - Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

class Robot implements Worker {
  work() { /* ... */ }
  eat() { throw new Error('Robots don't eat!'); } // Forced to implement
  sleep() { throw new Error('Robots don't sleep!'); } // Forced to implement
}

// ✅ Good - Segregated interfaces
interface Workable {
  work(): void;
}

interface Feedable {
  eat(): void;
}

interface Restable {
  sleep(): void;
}

class Human implements Workable, Feedable, Restable {
  work() { /* ... */ }
  eat() { /* ... */ }
  sleep() { /* ... */ }
}

class Robot implements Workable {
  work() { /* ... */ }
}
```

**Benefits**:
- Smaller, focused interfaces
- Reduces unnecessary dependencies
- Easier to implement and test
- More flexible design

---

### D - Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

**Key Concept**: Depend on interfaces/abstractions, not concrete implementations. Inject dependencies rather than creating them internally.

**Quick Example**:
```typescript
// ❌ Bad - High-level depends on low-level
class MySQLDatabase {
  save(data: string) { /* ... */ }
}

class UserService {
  private db = new MySQLDatabase(); // Direct dependency
  
  saveUser(user: string) {
    this.db.save(user);
  }
}

// ✅ Good - Both depend on abstraction
interface Database {
  save(data: string): void;
}

class MySQLDatabase implements Database {
  save(data: string) { /* ... */ }
}

class MongoDatabase implements Database {
  save(data: string) { /* ... */ }
}

class UserService {
  constructor(private db: Database) {} // Dependency injection
  
  saveUser(user: string) {
    this.db.save(user);
  }
}

// Usage
const userService = new UserService(new MySQLDatabase());
// Can easily swap: new UserService(new MongoDatabase());
```

**Benefits**:
- Decouples high-level and low-level modules
- Easier to swap implementations
- Improves testability (can inject mocks)
- More flexible architecture

---

## Quick Reference Guide

### When to Apply Each Principle

**Single Responsibility (S)**:
- Class has multiple unrelated methods
- Class name contains "And" or "Manager"
- Changes in one area affect unrelated functionality
- Class is difficult to name clearly

**Open/Closed (O)**:
- Frequently modifying existing code to add features
- Using switch/if-else chains for type checking
- Adding new types requires code changes in multiple places
- Need to extend behavior without risk

**Liskov Substitution (L)**:
- Subclasses override parent methods with exceptions
- Subclasses have empty/stub implementations
- Type checking required before using polymorphism
- Inheritance hierarchy seems awkward

**Interface Segregation (I)**:
- Interfaces have many methods
- Classes implement interfaces with empty methods
- Different clients use different subsets of interface
- Interface changes affect unrelated clients

**Dependency Inversion (D)**:
- Classes instantiate their dependencies directly
- Difficult to test (can't inject mocks)
- Tightly coupled to specific implementations
- Hard to swap implementations

---

## SOLID in Practice

### Decision Tree

```
Are you designing a new class?
├─ YES → Apply SRP: Does it have one clear responsibility?
│        Apply ISP: Are your interfaces focused?
│        Apply DIP: Are you depending on abstractions?
│
└─ NO → Are you modifying existing code?
         Apply OCP: Can you extend instead of modify?
         Apply LSP: Does substitution work correctly?
```

### Code Smell Indicators

**Violating SRP**:
- God classes with 500+ lines
- Classes with "Manager", "Handler", "Utility" in name
- Methods that do multiple unrelated things

**Violating OCP**:
- Long if/else or switch statements checking types
- Modifying existing classes to add features
- Fear of breaking existing functionality

**Violating LSP**:
- Subclass throws exceptions parent doesn't
- Type checking before casting
- Empty or stub method implementations

**Violating ISP**:
- NotImplementedError or empty method bodies
- Interfaces with >5 methods
- Clients using only a fraction of interface

**Violating DIP**:
- `new` keyword scattered throughout code
- Direct imports of concrete classes
- Hard to write unit tests

---

## Refactoring Workflow

### Step 1: Identify Violations
Look for code smells and anti-patterns listed above.

### Step 2: Choose Principle to Apply
Start with the most violated principle or the one causing the most pain.

### Step 3: Refactor Incrementally
- Write tests first (if not already present)
- Apply one principle at a time
- Keep tests passing after each change
- Commit frequently

### Step 4: Verify Improvement
- Code is easier to understand
- New features require less modification
- Tests are easier to write
- Coupling is reduced

---

## Testing and SOLID

SOLID principles naturally lead to more testable code:

**SRP** → Test one responsibility at a time
**OCP** → Test new extensions without modifying old tests
**LSP** → Test parent and child with same test suite
**ISP** → Mock only what you need
**DIP** → Inject test doubles easily

**Example**:
```typescript
// Easy to test with DIP
class OrderService {
  constructor(
    private paymentGateway: PaymentGateway,
    private emailService: EmailService
  ) {}
  
  processOrder(order: Order) {
    this.paymentGateway.charge(order.total);
    this.emailService.send(order.customer.email, 'Order confirmed');
  }
}

// Test with mocks
const mockPayment = { charge: jest.fn() };
const mockEmail = { send: jest.fn() };
const service = new OrderService(mockPayment, mockEmail);
service.processOrder(order);

expect(mockPayment.charge).toHaveBeenCalled();
expect(mockEmail.send).toHaveBeenCalled();
```

---

## Common Misconceptions

### "SOLID Leads to Over-Engineering"
**Reality**: SOLID should simplify, not complicate. If it feels over-engineered, you may be applying principles where they're not needed. Use judgment.

### "Follow All Principles Always"
**Reality**: SOLID are guidelines, not laws. Sometimes pragmatism trumps purity. Balance is key.

### "SOLID Only for OOP"
**Reality**: While designed for OOP, the underlying concepts apply broadly. Functional programming has similar principles.

### "SOLID Means More Code"
**Reality**: Initial code may increase, but maintenance burden decreases significantly. Long-term, SOLID saves time.

---

## Reference Documentation

For detailed explanations, examples, and refactoring guides:

**Detailed principles guide**: See [references/principles-guide.md](references/principles-guide.md)
- Deep dive into each principle
- Multiple examples per principle
- Edge cases and nuances
- Language-specific considerations

**Real-world examples**: See [references/examples.md](references/examples.md)
- Complete code examples in TypeScript, Python, Java
- Before/after refactoring scenarios
- Common patterns and anti-patterns
- Industry-standard applications

**Refactoring guide**: See [references/refactoring-guide.md](references/refactoring-guide.md)
- Step-by-step refactoring process
- Dealing with legacy code
- Incremental improvement strategies
- Testing during refactoring

Load these references when you need:
- Detailed explanations of each principle
- Multiple code examples in different languages
- Refactoring strategies for existing code
- Advanced patterns and edge cases

---

## Benefits of SOLID

✅ **Maintainability**: Easier to understand and modify code
✅ **Flexibility**: Easy to extend and adapt to new requirements
✅ **Testability**: Simple to write unit tests and mocks
✅ **Reusability**: Components can be reused in different contexts
✅ **Scalability**: Architecture supports growth
✅ **Reduced Bugs**: Clear responsibilities reduce unexpected interactions
✅ **Team Productivity**: Easier for teams to work on different parts

---

## Quick Checklist

Before considering your code SOLID, ask:

- [ ] **S**: Does each class have a single, clear responsibility?
- [ ] **O**: Can I add new features without modifying existing code?
- [ ] **L**: Can I substitute derived classes without breaking behavior?
- [ ] **I**: Are my interfaces small and focused?
- [ ] **D**: Am I depending on abstractions, not concrete implementations?

If you answer "YES" to all, you're writing SOLID code! 🎉