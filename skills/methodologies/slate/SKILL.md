---
name: slate-methodology
description: Apply the S.L.A.T.E. development methodology for structured software engineering. Use when planning complex features, establishing development workflows, or ensuring engineering excellence.
license: MIT
---

# S.L.A.T.E. Development Methodology

Version 2025.1 - Overwatch Agent Network

## When to Use

Use this skill when starting a complex feature, establishing structured development workflows, ensuring specification-first development, or when engineering excellence is required.

## The S.L.A.T.E. Principles

**S - Specification-First**: Define contracts, interfaces, types BEFORE implementation. No code generation without defined requirements.

**L - Loaded Context**: Lazy loading - use grep/search BEFORE read. Load ONLY what is needed. Context is a system resource.

**A - Augmented Intelligence**: Tools are function calls. Verify state before acting. Combine tool calls when independent.

**T - Test-Driven**: Tests are the evaluation metric. RED-GREEN-REFACTOR cycle per feature.

**E - Engineering Excellence**: Follow project style signature. Consistency over Novelty. Run lint/typecheck after changes.

## Execution Tracks

### Standard Track (Complex Tasks)

Phase 0: Constitution - Load project standards, patterns, conventions
Phase 1: Specify - Create/update spec.md with requirements  
Phase 2: Plan - Create/update plan.md with technical approach
Phase 3: Analyze - Determine scope, affected files, dependencies
Phase 4: Task - Break into atomic, testable tasks
Phase 5: Implement - TDD Loop (Red-Green-Refactor)

### Fast-Track (Simple Tasks)

Phase 1: Context - Create context.md with bullet-point requirements
Phase 2: Implement - Direct implementation with testing
Phase 3: Validate - Run tests, lint, typecheck

## The Golden Rule

The Prompt is a Downstream Artifact of the Specification. If it is not in the Spec (Input), it should not be in the Code (Output).

## Quality Gates

Before Implementation: Does the task have a Test Requirement? Is the Interface defined? Are acceptance criteria clear?

After Implementation: Do all tests pass? Is coverage above 90%? Are there 0 linting errors? Has typecheck passed?
