---
name: claim-first-workflow
description: Apply claim-first development workflow for AI agents. Use when building agents that need to make assertions, validate claims, and self-correct.
license: MIT
---

# Claim-First Workflow

## When to Use

Use this skill when building AI agents that need to make assertions, validate their outputs, and implement self-correction mechanisms.

## Core Concept

Make a claim first, then validate it. If validation fails, correct and retry.

## Workflow

1. Formulate Claim - State what you intend to produce or verify
2. Generate Output - Create the artifact or perform the action
3. Validate Claim - Check if output matches the claim
4. Correct if Needed - If validation fails, analyze error and retry

## Benefits

Explicit success criteria. Built-in validation. Self-correction capability. Traceable reasoning.

## Best Practices

Make claims specific and testable. Include validation criteria upfront. Log claim-validation pairs. Learn from correction patterns.
