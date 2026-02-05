---
name: prompt-optimization
description: Optimize natural language into agentic prompts using DSPy signature patterns. Use when converting casual instructions into structured, high-performance prompts for AI agents.
license: MIT
---

# Prompt Optimization with DSPy Signatures

## When to Use

Use this skill when converting natural language instructions into optimized agentic prompts, when improving prompt clarity and effectiveness, or when creating structured prompt templates for AI systems.

## Core Concept

Transform informal, ambiguous natural language into precise, structured prompts using DSPy signature patterns. This creates type-safe, composable, and testable prompt interfaces.

## The Optimization Pipeline

Step 1: Parse Intent - Extract the core goal from natural language input
Step 2: Identify Components - Determine inputs, outputs, constraints, and context
Step 3: Define Signature - Create typed input/output specification
Step 4: Add Structure - Apply agentic patterns (role, task, format, constraints)
Step 5: Validate - Test prompt against expected behaviors

## DSPy Signature Pattern

A signature defines the contract between user intent and agent behavior.

Input Fields: What information the prompt receives (with types and descriptions)
Output Fields: What the prompt should produce (with types and descriptions)
Instructions: How to transform inputs to outputs
Constraints: Boundaries and requirements for valid outputs

## Optimization Techniques

Decomposition: Break complex requests into atomic sub-tasks
Specification: Add explicit types, formats, and examples
Contextualization: Include relevant background and constraints
Structuring: Organize with clear sections (role, task, output, rules)
Grounding: Add concrete examples and edge cases

## From Natural Language to Agentic Prompt

Natural Input Example: "Help me write better code"

Optimized Agentic Prompt:

Role: You are an expert code reviewer and improvement specialist.

Task: Analyze the provided code and suggest improvements for readability, performance, maintainability, and best practices.

Input: code_snippet (string) - The code to analyze, language (string) - Programming language

Output: analysis (object) containing issues_found (list of problems), improvements (list of specific suggestions), refactored_code (improved version), explanation (reasoning for changes)

Constraints: Preserve original functionality. Follow language-specific conventions. Prioritize readability over cleverness. Include comments for complex changes.

Format: Return structured JSON with all output fields populated.

## Signature Template

Use this template to structure optimized prompts:

Name: descriptive-action-name
Description: One sentence explaining purpose and trigger conditions

Inputs:
- field_name: type - description and constraints
- field_name: type - description and constraints

Outputs:
- field_name: type - description of expected content
- field_name: type - description of expected content

Instructions: Clear, imperative statements describing the transformation

Constraints: Explicit boundaries, requirements, and validation rules

Examples: Input-output pairs demonstrating expected behavior

## Optimization Checklist

Clarity: Is the intent unambiguous?
Completeness: Are all inputs and outputs specified?
Constraints: Are boundaries and rules explicit?
Structure: Is the prompt well-organized?
Testability: Can outputs be validated?
Composability: Can this prompt chain with others?

## Common Transformations

Vague to Specific: "Make it better" becomes "Improve readability by reducing function length to under 20 lines"

Implicit to Explicit: "Fix the bug" becomes "Identify the root cause, explain the issue, provide corrected code with tests"

Unstructured to Structured: Free-form request becomes Role + Task + Input + Output + Constraints format

Single to Multi-step: Monolithic request becomes pipeline of atomic operations

## Best Practices

Start with user intent analysis before optimization. Preserve original meaning while adding structure. Use concrete examples to disambiguate. Define failure modes and edge cases. Make constraints testable and measurable. Design for composability with other prompts.

## Integration with Agent Systems

Optimized prompts integrate with agent frameworks through typed signatures. Each signature becomes a callable module that can be chained, tested, and monitored. Use consistent naming conventions and output schemas across your prompt library.
