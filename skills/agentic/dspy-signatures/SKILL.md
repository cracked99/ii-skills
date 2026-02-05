---
name: dspy-signatures
description: Design and implement DSPy-style signatures for structured AI agent I/O. Use when defining agent contracts, implementing typed predictions, creating reusable prompt templates, or building systems with automated prompt optimization.
allowed-tools:
  - Bash
  - Read
  - str_replace_based_edit_tool
---

# DSPy Signatures

**Origin**: Overwatch Agent Network - ADR-004  
**Reference**: Stanford DSPy Framework

## When to Use

- Defining structured agent input/output contracts
- Building reusable, optimizable prompt templates
- Creating typed predictions for LLM calls
- Implementing automated prompt optimization
- Designing agent interfaces that are portable across LLMs

## Core Concept

DSPy signatures separate the **interface** (what) from the **implementation** (how):

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SIGNATURE-FIRST DESIGN                        │
├─────────────────────────────────────────────────────────────────────┤
│  Traditional Prompting      │  DSPy Signatures                      │
│  ─────────────────────────  │  ──────────────────────               │
│  "You are an assistant..."  │  task -> analysis, recommendation     │
│  Manual prompt iteration    │  Automated optimization               │
│  Prompts mixed with logic   │  Signatures separate interface        │
│  Single-model focus         │  Portable across LMs                  │
│  String manipulation        │  Typed predictions                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Signature Format

### Inline Syntax

Simple signature in single line:

```python
# Basic signature
"question -> answer"

# Multi-input
"context, question -> answer"

# Multi-output
"task -> analysis, recommendation, confidence"

# With descriptions
"code: str, language: str -> bugs: list[Bug], suggestions: list[str]"
```

### YAML Configuration

Detailed signature in agent configs:

```yaml
signature:
  description: |
    Analyze code for bugs and provide actionable recommendations.
  inline: "code, language, context -> bugs, suggestions, summary"
  
  inputs:
    - name: code
      type: string
      required: true
      description: "Source code to analyze"
      constraints:
        - "Must be syntactically valid"
        - "Maximum 10,000 characters"
    
    - name: language
      type: string
      required: true
      enum: [python, typescript, javascript, go, rust]
    
    - name: context
      type: object
      required: false
      properties:
        project_name: string
        dependencies: string[]
  
  outputs:
    - name: bugs
      type: array
      items:
        type: object
        properties:
          line: number
          severity: enum[low, medium, high, critical]
          description: string
          fix: string
      validation:
        - "Each bug must have a line number"
        - "Each bug must have a suggested fix"
    
    - name: suggestions
      type: array
      items: string
      validation:
        - "At least one suggestion required"
    
    - name: summary
      type: string
      max_length: 500
```

## Type System

| Type | Description | Example |
|------|-------------|---------|
| `string` | Plain text | `"hello world"` |
| `number` | Numeric value | `42`, `3.14` |
| `boolean` | True/false | `true`, `false` |
| `object` | Structured data | `{ name: "John" }` |
| `array` / `T[]` | List of type T | `[1, 2, 3]` |
| `enum[...]` | Restricted values | `enum[low, medium, high]` |

### Custom Types

```yaml
types:
  TaskDecomposition:
    properties:
      title: string
      description: string
      subtasks: AtomicSubtask[]
  
  AtomicSubtask:
    properties:
      id: string
      action: string
      requirements: string[]
      test_criteria: string
  
  CodeArtifact:
    properties:
      path: string
      content: string
      language: string
```

## DSPy Modules

### Basic Modules

```python
import dspy

# Simple prediction
class BasicQA(dspy.Signature):
    """Answer questions based on context."""
    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

qa = dspy.Predict(BasicQA)
result = qa(context="...", question="What is X?")
```

### Chain of Thought

```python
class ReasonedAnswer(dspy.Signature):
    """Answer with step-by-step reasoning."""
    question: str = dspy.InputField()
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning")
    answer: str = dspy.OutputField()

reasoner = dspy.ChainOfThought(ReasonedAnswer)
```

### ReAct (Reasoning + Acting)

```python
class ToolUser(dspy.Signature):
    """Use tools to answer questions."""
    question: str = dspy.InputField()
    tools_used: list[str] = dspy.OutputField()
    answer: str = dspy.OutputField()

agent = dspy.ReAct(ToolUser, tools=[search, calculate])
```

## Module Reference

| Module | Purpose | Use Case |
|--------|---------|----------|
| `Predict` | Simple LM call | Basic Q&A |
| `ChainOfThought` | Step-by-step reasoning | Complex reasoning |
| `ReAct` | Reasoning + tool use | Tool-augmented agents |
| `ProgramOfThought` | Code generation + execution | Computation tasks |
| `Refine` | Iterative improvement | Quality enhancement |
| `BestOfN` | Sample N, pick best | High-stakes decisions |

## Optimizers

### MIPROv2

Multi-stage optimization:

```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(
    metric=accuracy_metric,
    num_candidates=10,
    init_temperature=1.0
)

optimized_program = optimizer.compile(
    program,
    trainset=examples,
    num_batches=5
)
```

### BootstrapFewShot

Learn from successful traces:

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(
    metric=quality_metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=8
)

optimized = optimizer.compile(program, trainset=examples)
```

## Agent Configuration with Signatures

```yaml
name: specialist-frontend
tier: ag

signature:
  description: |
    Implement frontend UI components and features.
  inline: "task_source, task, context -> claim_action, implementation, summary"
  
  inputs:
    - name: task
      type: string
      required: true
      constraints:
        - "Must include clear acceptance criteria"
    
    - name: context
      type: object
      properties:
        existing_patterns: string[]
        dependencies: string[]
  
  outputs:
    - name: implementation
      type: object
      required: true
      validation:
        required_fields: [files_created, files_modified, lint_passed]
    
    - name: summary
      type: string
      max_length: 200

# Signature enforcement
configuration:
  signature_enforcement:
    enabled: true
    mode: strict
    block_on_violation: true
    max_corrections: 3
```

## Signature as Constraint

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LLM INFERENCE LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│  WHEN TOOLS ARE USED (execute mode):                                │
│  1. Signature.output → task_complete tool schema                    │
│     - Output fields become required tool parameters                 │
│     - LLM is CONSTRAINED to provide structured output               │
│                                                                     │
│  WHEN NO TOOLS (prompt/chat mode):                                  │
│  1. Signature → toJsonSchema() → response_format                    │
│     - LLM API receives json_schema response_format                  │
│     - LLM is CONSTRAINED to output valid JSON                       │
├─────────────────────────────────────────────────────────────────────┤
│  Result: Signature acts as a HARD constraint at inference time      │
└─────────────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Define signatures before implementation** - The signature is the contract
2. **Use descriptive field names** - Self-documenting interfaces
3. **Add constraints** - Validation rules prevent bad outputs
4. **Keep signatures focused** - Single responsibility principle
5. **Version your signatures** - Track changes over time

## Anti-Patterns

- ❌ Vague output types like `any` or `object`
- ❌ Missing required field markers
- ❌ No validation rules on critical outputs
- ❌ Signatures that are too broad (do everything)
- ❌ Ignoring signature during implementation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid outputs | Check type constraints, add validation |
| Missing fields | Mark as required, add defaults |
| Inconsistent format | Use enum types, strict schemas |
| Poor optimization | Add more training examples |