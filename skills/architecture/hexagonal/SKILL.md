---
name: hexagonal-architecture
description: Apply hexagonal (ports and adapters) architecture pattern. Use when designing systems that need to be testable, maintainable, and independent of external dependencies.
license: MIT
---

# Hexagonal Architecture

## When to Use

Use this skill when designing systems requiring testability, maintainability, and independence from external dependencies like databases, APIs, or UI frameworks.

## Core Concepts

Domain Core - Pure business logic with no external dependencies
Ports - Interfaces that define how the domain interacts with the outside world
Adapters - Implementations that connect ports to external systems

## Structure

Inbound Ports - Interfaces for incoming requests (use cases)
Outbound Ports - Interfaces for external dependencies (repositories, services)
Inbound Adapters - Controllers, CLI handlers, message consumers
Outbound Adapters - Database implementations, API clients, file systems

## Benefits

Testability through dependency injection. Technology independence. Clear separation of concerns. Easy to swap implementations.

## Best Practices

Keep domain pure. Define ports as interfaces. Inject adapters at runtime. Test domain in isolation.
