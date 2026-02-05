---
name: three-tier-agents
description: Design multi-agent systems using Three-Tier Agent Hierarchy. Use when building orchestrated agent systems, implementing delegation patterns, or creating hierarchical task distribution with Orchestrator → Project Manager → Specialist structure.
allowed-tools: ["Bash", "Read", "str_replace_based_edit_tool"]
---

# Three-Tier Agent Hierarchy

**Origin**: Overwatch Agent Network - ADR-001

## When to Use

- Designing multi-agent orchestration systems
- Implementing strategic → tactical → operational workflows
- Building delegation-based task distribution
- Creating specialized agent pools
- Separating planning from execution

## The Three Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIER 1: ORCHESTRATOR                          │
│                       (Strategic Level)                          │
│         • Single instance per project                            │
│         • Maintains global context                               │
│         • Strategic decisions only                               │
│         • Delegates to Project Managers                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  TIER 2: PM   │   │  TIER 2: PM   │   │  TIER 2: PM   │
│  (Tactical)   │   │  (Tactical)   │   │  (Tactical)   │
│  pm-feature   │   │  pm-devops    │   │  pm-quality   │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
    ┌───┴───┐           ┌───┴───┐           ┌───┴───┐
    ▼       ▼           ▼       ▼           ▼       ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│TIER 3 │ │TIER 3 │ │TIER 3 │ │TIER 3 │ │TIER 3 │ │TIER 3 │
│frontend│ │backend│ │deploy │ │infra  │ │testing│ │security│
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
              SPECIALISTS (Operational Level)
```

## Tier Comparison

| Aspect | Orchestrator | Project Manager | Specialist |
|--------|--------------|-----------------|------------|
| **Role** | Strategic planning | Domain coordination | Code implementation |
| **Mode** | Interactive | Interactive | Stateless |
| **Instances** | 1 per project | 1 per domain | Pool per capability |
| **Tool Access** | Read-only | Read + Pool mgmt | Full read/write |
| **Spawning** | Can spawn PMs | Can spawn Specialists | None |
| **Context** | Global project | Domain-specific | Task-specific |
| **Persistence** | Long-running | Session-based | Ephemeral |

## Tier 1: Orchestrator

The single strategic brain of the system:

```yaml
name: orchestrator
tier: oc
description: Strategic planning and high-level coordination

responsibilities:
  - Maintain global project context
  - Create and manage project plans
  - Delegate tasks to appropriate PMs
  - Monitor overall progress
  - Make strategic decisions

constraints:
  - NEVER modify code directly
  - NEVER interact with external APIs
  - ALWAYS delegate implementation to PMs

tools:
  planning: [plan, spec, delegate, check_delegation]
  context: [project_context, checkpoint_optimize]
  read: [Read, Grep, Glob, LS]

workflow:
  - { step: 1, action: "Load project context", tool: project_context }
  - { step: 2, action: "Create plan with tasks", tool: plan }
  - { step: 3, action: "Delegate first task to PM", tool: delegate }
  - { step: 4, action: "Wait for completion", tool: check_delegation }
  - { step: 5, action: "Update plan status", tool: plan }
  - { step: 6, action: "Repeat until complete" }
```

## Tier 2: Project Managers

Domain-specific coordinators:

```yaml
# PM Types
pm-feature:
  domain: Feature development
  capabilities: [frontend, backend, database, api]
  
pm-devops:
  domain: Infrastructure
  capabilities: [deployment, ci-cd, monitoring, scaling]

pm-quality:
  domain: Testing and QA
  capabilities: [unit-tests, integration, e2e, security]

pm-security:
  domain: Security review
  capabilities: [audit, vulnerability, compliance]

pm-docs:
  domain: Documentation
  capabilities: [api-docs, guides, tutorials]
```

### PM Configuration Example

```yaml
name: pm-feature
tier: pm
domain: feature

responsibilities:
  - Decompose features into subtasks
  - Manage specialist pool
  - Review and approve claims
  - Aggregate specialist results
  - Report to orchestrator

tools:
  read: [Read, Grep, Glob, LS]
  claims: [manage_subtask_pool, review_claims, monitor_claims]
  context: [project_context, record_decision]
  workspace: [project_workspace, init_project]

workflow:
  - { step: 1, action: "Check project state", tool: project_context }
  - { step: 2, action: "Decompose into subtasks", slate: S }
  - { step: 3, action: "Publish to claim pool", tool: manage_subtask_pool }
  - { step: 4, action: "Wait for claims", tool: monitor_claims }
  - { step: 5, action: "Review and approve", tool: review_claims }
  - { step: 6, action: "Aggregate results" }
  - { step: 7, action: "Report completion", tool: task_complete }
```

## Tier 3: Specialists

Stateless execution agents:

```yaml
# Specialist Types
specialist-frontend:
  capabilities: [react, vue, typescript, css, components]
  
specialist-backend:
  capabilities: [nodejs, python, api, database, graphql]

specialist-database:
  capabilities: [postgresql, mongodb, redis, migrations]

specialist-testing:
  capabilities: [unit, integration, e2e, mocking]

specialist-deploy:
  capabilities: [docker, kubernetes, aws, vercel]

specialist-ux:
  capabilities: [design, accessibility, user-flows]
```

### Specialist Configuration Example

```yaml
name: specialist-frontend
tier: ag
domain: frontend

responsibilities:
  - Claim available subtasks
  - Implement assigned work
  - Run tests and linting
  - Submit completed work

constraints:
  - NEVER implement before claim approval
  - ALWAYS run lint/typecheck before completing
  - ALWAYS follow existing project patterns

tools:
  read: [Read, Grep, Glob, LS]
  write: [Write, Edit, Bash]
  claims: [claim_subtask, get_active_work]
  locks: [acquire_file_lock, release_file_lock]

workflow:
  - { step: 1, action: "Check claim pool", tool: claim_subtask }
  - { step: 2, action: "Submit claim", tool: claim_subtask }
  - { step: 3, action: "Wait for approval" }
  - { step: 4, action: "Acquire locks", tool: acquire_file_lock }
  - { step: 5, action: "Implement feature", tool: Write }
  - { step: 6, action: "Run tests", tool: Bash }
  - { step: 7, action: "Release locks", tool: release_file_lock }
  - { step: 8, action: "Complete task", tool: task_complete }
```

## Tool Access by Tier

| Tool Category | Orchestrator | PM | Specialist |
|---------------|:------------:|:--:|:----------:|
| **Read** (Read, Grep, Glob) | ✅ | ✅ | ✅ |
| **Write** (Write, Edit, Bash) | ❌ | ❌ | ✅ |
| **Planning** (plan, spec, delegate) | ✅ | ❌ | ❌ |
| **Claims** (manage_pool, review) | ❌ | ✅ | ✅ (partial) |
| **Context** (project_context) | ✅ | ✅ | ✅ |
| **File Locks** | ❌ | ❌ | ✅ |

## Communication Flow

```
Orchestrator ──delegate──▶ PM ──publish_subtask──▶ Pool
                                                    │
Orchestrator ◀──report──── PM ◀──submit_claim───── Specialist
                              │
                              └──approve_claim──▶ Specialist
                                                    │
                              ◀──task_complete───── Specialist
```

## Implementation

### Message Types

```typescript
interface DelegateMessage {
  type: 'delegate';
  from: 'orchestrator';
  to: `pm-${string}`;
  payload: {
    taskId: string;
    description: string;
    requirements: string[];
    deadline?: Date;
  };
}

interface SubtaskMessage {
  type: 'subtask';
  from: `pm-${string}`;
  pool: 'specialists';
  payload: {
    id: string;
    title: string;
    capabilities: string[];
    priority: 'low' | 'medium' | 'high';
  };
}

interface ClaimMessage {
  type: 'claim';
  from: `specialist-${string}`;
  to: `pm-${string}`;
  payload: {
    subtaskId: string;
    proposal: string;
    confidence: number;
  };
}
```

### Tier Factory

```typescript
class AgentFactory {
  createAgent(config: AgentConfig): Agent {
    switch (config.tier) {
      case 'oc':
        return new OrchestratorAgent(config);
      case 'pm':
        return new ProjectManagerAgent(config);
      case 'ag':
        return new SpecialistAgent(config);
      default:
        throw new Error(`Unknown tier: ${config.tier}`);
    }
  }
}
```

## Anti-Patterns

- ❌ Orchestrator writing code directly
- ❌ PM skipping claim review
- ❌ Specialist spawning other agents
- ❌ Direct specialist-to-orchestrator communication
- ❌ Bypassing the delegation chain

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Orchestrator overloaded | Delegate more to PMs, reduce context |
| PM bottleneck | Increase specialist pool, parallel subtasks |
| Specialist conflicts | Use file locks, atomic subtasks |
| Lost context | Check project_context calls, use checkpoints |