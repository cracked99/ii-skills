---
name: three-tier-agents
description: Apply three-tier agent architecture for AI systems. Use when designing multi-agent systems with clear separation between orchestration, execution, and tool layers.
license: MIT
---

# Three-Tier Agent Architecture

## When to Use

Use this skill when designing multi-agent AI systems requiring clear separation between orchestration, task execution, and tool integration layers.

## The Three Tiers

Orchestration Tier - High-level planning, task decomposition, agent coordination
Execution Tier - Task-specific agents that implement business logic
Tool Tier - Low-level tool integrations, API calls, file operations

## Communication Patterns

Top-down delegation from orchestrator to executors. Bottom-up reporting from tools to executors. Horizontal coordination between peer agents.

## Best Practices

Keep orchestrators focused on planning. Make executors task-specific. Abstract tool complexity. Use clear interfaces between tiers.
