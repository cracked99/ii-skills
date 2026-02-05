---
name: agent-configuration
description: Configure AI agents using YAML-based specifications. Use when setting up agent hierarchies, defining tool access, configuring workflows, or establishing agent constraints and behaviors for multi-agent systems.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Agent Configuration

**Origin**: Overwatch Agent Network Framework

## When to Use

- Setting up new agents in a multi-agent system
- Defining agent roles, capabilities, and constraints
- Configuring tool access and permissions
- Establishing workflow sequences
- Integrating DSPy signatures and self-correction

## Configuration Sections

### Complete Agent Configuration

```yaml
# ═══════════════════════════════════════════════════════════════════
# SECTION 1: IDENTITY (Single Responsibility Principle)
# ═══════════════════════════════════════════════════════════════════
name: specialist-frontend
description: Frontend development specialist for React/TypeScript
version: 2.1.0
tier: ag                    # oc (orchestrator), pm (project manager), ag (agent)
domain: frontend

# ═══════════════════════════════════════════════════════════════════
# SECTION 2: MODEL CONFIGURATION (Dependency Inversion)
# ═══════════════════════════════════════════════════════════════════
model: inherit              # or specific: claude-3-5-sonnet, gpt-4o
autonomy: high              # low, medium, high
temperature: 0.7
max_tokens: 4096

# ═══════════════════════════════════════════════════════════════════
# SECTION 3: BROKER INTEGRATION
# ═══════════════════════════════════════════════════════════════════
broker:
  enabled: true
  connection: inherit       # or ws://localhost:8080
  claim_pool:
    enabled: true
    capabilities: [frontend, react, typescript, css, ui]
    auto_subscribe: true

# ═══════════════════════════════════════════════════════════════════
# SECTION 4: DSPy SIGNATURE (Specification-First)
# ═══════════════════════════════════════════════════════════════════
signature:
  description: |
    Implement frontend UI components and features following React
    best practices and project design system.
  inline: "task_source, task, context -> claim_action, implementation, summary"
  
  inputs:
    - name: task
      type: string
      required: true
      constraints:
        - "Must include clear acceptance criteria"
        - "Must reference design specifications"
    
    - name: context
      type: object
      required: false
      properties:
        existing_components: string[]
        design_tokens: object
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

# ═══════════════════════════════════════════════════════════════════
# SECTION 5: WORKFLOW (SLATE phases marked)
# ═══════════════════════════════════════════════════════════════════
workflow:
  - step: 1
    action: "Check claim pool for available subtasks"
    tool: claim_subtask
    slate: L                # Loaded Context
  
  - step: 2
    action: "Evaluate subtask complexity"
    tool: claim_subtask
    slate: S                # Specification
  
  - step: 3
    action: "Submit claim with implementation proposal"
    tool: claim_subtask
    slate: A                # Augmented Intelligence
  
  - step: 4
    action: "Wait for PM approval"
    blocking: true
    slate: A
  
  - step: 5
    action: "Check existing patterns in codebase"
    tool: project_context
    slate: L
  
  - step: 6
    action: "Acquire file locks"
    tool: acquire_file_lock
    slate: E                # Engineering Excellence
  
  - step: 7
    action: "Implement the feature with TDD"
    tool: Write
    slate: T                # Test-Driven
  
  - step: 8
    action: "Run tests and linting"
    tool: Bash
    slate: T
  
  - step: 9
    action: "Release file locks"
    tool: release_file_lock
    slate: E
  
  - step: 10
    action: "Record decision and complete"
    tool: record_decision
    slate: E

# ═══════════════════════════════════════════════════════════════════
# SECTION 6: CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════
constraints:
  - "NEVER implement before claim is approved"
  - "ALWAYS use TypeScript strict mode"
  - "ALWAYS run lint and typecheck before completing"
  - "NEVER bypass file locking"
  - "ALWAYS follow existing component patterns"

# ═══════════════════════════════════════════════════════════════════
# SECTION 7: ANTI-PATTERNS
# ═══════════════════════════════════════════════════════════════════
anti_patterns:
  - "Implementing before claim approval"
  - "Skipping lint/typecheck verification"
  - "Creating components without design tokens"
  - "Ignoring existing patterns"
  - "Not writing tests"

# ═══════════════════════════════════════════════════════════════════
# SECTION 8: EXECUTION INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════════
instructions: |
  CRITICAL: Execute steps IN ORDER. Do NOT skip steps.
  
  1. ALWAYS check the claim pool first
  2. NEVER start implementation without approved claim
  3. ALWAYS check existing patterns before coding
  4. ALWAYS use project's component library
  5. ALWAYS run tests before marking complete
  
  If stuck, request help via task_complete with status: blocked

# ═══════════════════════════════════════════════════════════════════
# SECTION 9: TEXTGRAD SELF-CORRECTION
# ═══════════════════════════════════════════════════════════════════
self_correction:
  enabled: true
  max_iterations: 2
  threshold: 0.85
  
  criteria:
    - name: "Completeness"
      description: "Is the component fully functional?"
      weight: 0.30
    
    - name: "Accessibility"
      description: "Does it meet WCAG AA standards?"
      weight: 0.20
    
    - name: "Responsiveness"
      description: "Works across all breakpoints?"
      weight: 0.20
    
    - name: "Pattern Adherence"
      description: "Follows project conventions?"
      weight: 0.15
    
    - name: "Performance"
      description: "No unnecessary re-renders?"
      weight: 0.15

# ═══════════════════════════════════════════════════════════════════
# SECTION 10: VALIDATION
# ═══════════════════════════════════════════════════════════════════
validation:
  enabled: true
  strict: false             # true = block on any violation
  
  rules:
    - "No placeholder or TODO comments"
    - "All props must be typed"
    - "No inline styles (use Tailwind)"
    - "Components must be exported"

# ═══════════════════════════════════════════════════════════════════
# SECTION 11: TRACE COLLECTION
# ═══════════════════════════════════════════════════════════════════
traces:
  enabled: true
  auto_collect: true
  min_score: 0.80
  
  include:
    - task_description
    - implementation_approach
    - files_changed
    - test_results

# ═══════════════════════════════════════════════════════════════════
# SECTION 12: SIGNATURE ENFORCEMENT
# ═══════════════════════════════════════════════════════════════════
configuration:
  signature_enforcement:
    enabled: true
    mode: strict            # strict, warn, off
    block_on_violation: true
    max_corrections: 3
    track_workflow: true
    check_constraints: true
    detect_anti_patterns: true

# ═══════════════════════════════════════════════════════════════════
# SECTION 13: TOOLS (Interface Segregation)
# ═══════════════════════════════════════════════════════════════════
tools:
  read:
    - Read
    - Grep
    - Glob
    - LS
  
  write:
    - Write
    - Edit
    - Bash
  
  claims:
    - claim_subtask
    - get_active_work
  
  locks:
    - check_file_status
    - acquire_file_lock
    - release_file_lock
  
  context:
    - project_context
    - record_decision
    - query_decisions
  
  optimization:
    - checkpoint_optimize

# ═══════════════════════════════════════════════════════════════════
# SECTION 14: LIMITS
# ═══════════════════════════════════════════════════════════════════
limits:
  max_iterations: 20
  timeout_seconds: 300
  max_file_size: 50000      # bytes
  max_context_tokens: 100000
```

## Tool Access by Tier

| Tier | Read | Write | Planning | Claims | Locks |
|------|:----:|:-----:|:--------:|:------:|:-----:|
| Orchestrator (oc) | ✅ | ❌ | ✅ | ❌ | ❌ |
| Project Manager (pm) | ✅ | ❌ | ❌ | ✅ | ❌ |
| Specialist (ag) | ✅ | ✅ | ❌ | Partial | ✅ |

## Configuration Templates

### Orchestrator Template

```yaml
name: orchestrator
tier: oc
model: claude-3-5-sonnet
autonomy: high

tools:
  read: [Read, Grep, Glob, LS]
  planning: [plan, spec, delegate, check_delegation]
  context: [project_context, checkpoint_optimize]

constraints:
  - "NEVER modify code directly"
  - "ALWAYS delegate to Project Managers"
```

### Project Manager Template

```yaml
name: pm-feature
tier: pm
domain: feature

tools:
  read: [Read, Grep, Glob, LS]
  claims: [manage_subtask_pool, review_claims, monitor_claims]
  context: [project_context, record_decision]
  workspace: [project_workspace]

constraints:
  - "NEVER implement code"
  - "ALWAYS review claims before approval"
```

### Specialist Template

```yaml
name: specialist-backend
tier: ag
domain: backend

tools:
  read: [Read, Grep, Glob, LS]
  write: [Write, Edit, Bash]
  claims: [claim_subtask, get_active_work]
  locks: [acquire_file_lock, release_file_lock]

constraints:
  - "NEVER implement before claim approval"
  - "ALWAYS run tests before completing"
```

## Validation

Validate configuration before deployment:

```bash
# Validate YAML syntax
yq eval '.' agent-config.yaml

# Check required fields
yq eval '.name, .tier, .tools' agent-config.yaml

# Validate signature
yq eval '.signature.inputs[] | .name + ": " + .type' agent-config.yaml
```

## Anti-Patterns

- ❌ Missing tier designation
- ❌ Tools without appropriate tier permissions
- ❌ No constraints defined
- ❌ Signature without validation rules
- ❌ Workflow steps without SLATE phases

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool access denied | Check tier permissions |
| Signature violation | Review input/output validation |
| Workflow stuck | Check blocking steps, timeouts |
| Config not loading | Validate YAML syntax |