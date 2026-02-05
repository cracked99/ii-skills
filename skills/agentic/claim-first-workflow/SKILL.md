---
name: claim-first-workflow
description: Implement claim-based task delegation for multi-agent systems. Use when designing agent coordination, task distribution, or competitive resource allocation.
---

# Claim-First Workflow

**Version**: 2.0  
**Origin**: Overwatch Agent Network - ADR-003

## When to Use

- Designing multi-agent coordination systems
- Implementing task delegation workflows
- Building competitive task allocation
- Resource-efficient agent spawning
- Quality-driven work assignment

## Core Philosophy

> "Claim before you spawn."
> Resources are allocated only to proven capability.

## The Claim-First Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAIM-FIRST WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│  1. PM Decomposes Task    → Creates atomic subtasks             │
│  2. Subtasks Published    → Broadcast to specialist pool        │
│  3. Specialists Claim     → Submit implementation proposals     │
│  4. PM Reviews Claims     → Selects best proposal               │
│  5. Sandbox Spawns        → Only for winning specialist         │
│  6. Specialist Executes   → In isolated environment             │
│  7. Results Aggregated    → PM reports to orchestrator          │
└─────────────────────────────────────────────────────────────────┘
```

## Why Claim-First?

| Traditional Approach | Claim-First Approach |
|---------------------|---------------------|
| Spawn agent, then assign work | Claim work, then spawn agent |
| Resources wasted on idle agents | Resources allocated on-demand |
| First-available assignment | Best-fit assignment |
| No quality gate before execution | Quality verified via claim |
| Expensive failures | Cheap claim rejection |

## Claim Types

### Plan-Only Claim
```yaml
type: plan-only
max_words: 200
content: |
  I will implement the user authentication endpoint by:
  1. Creating a JWT token service using jsonwebtoken
  2. Adding password hashing with bcrypt (12 rounds)
  3. Implementing rate limiting middleware
  4. Adding comprehensive error handling
```

### Code-Only Claim
```yaml
type: code-only
max_lines: 10
content: |
  export async function authenticate(email: string, password: string) {
    const user = await db.users.findByEmail(email);
    if (!user || !await bcrypt.compare(password, user.passwordHash)) {
      throw new UnauthorizedError('Invalid credentials');
    }
    return jwt.sign({ userId: user.id }, SECRET, { expiresIn: '1h' });
  }
```

### Hybrid Claim
```yaml
type: hybrid
max_words: 100
max_lines: 5
content: |
  Using JWT with RS256 for better security. The token service will:
  - Generate tokens with 1-hour expiry
  - Support refresh token rotation
  
  ```typescript
  const token = jwt.sign(payload, privateKey, { algorithm: 'RS256' });
  ```
```

## Step-by-Step Implementation

### Step 1: Define Subtask Structure

```typescript
interface Subtask {
  id: string;
  title: string;
  description: string;
  requirements: string[];
  acceptanceCriteria: string[];
  capabilities: string[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  estimatedEffort: string;
}

interface SubtaskPool {
  available: Subtask[];
  claimed: Map<string, Claim>;
  completed: Subtask[];
}
```

### Step 2: Implement Claim Submission

```typescript
interface Claim {
  id: string;
  subtaskId: string;
  specialistId: string;
  type: 'plan-only' | 'code-only' | 'hybrid';
  content: string;
  capabilities: string[];
  submittedAt: Date;
  status: 'pending' | 'approved' | 'rejected';
}

class ClaimService {
  async submitClaim(subtaskId: string, specialistId: string, claimData: ClaimSubmission): Promise<Claim> {
    this.validateClaimFormat(claimData);
    const subtask = await this.getSubtask(subtaskId);
    this.validateCapabilities(specialistId, subtask.capabilities);
    
    const claim: Claim = {
      id: crypto.randomUUID(),
      subtaskId,
      specialistId,
      type: claimData.type,
      content: claimData.content,
      capabilities: claimData.capabilities,
      submittedAt: new Date(),
      status: 'pending'
    };
    
    await this.storeClaim(claim);
    return claim;
  }
}
```

### Step 3: Implement Claim Review

```typescript
class ClaimReviewService {
  async reviewClaims(subtaskId: string): Promise<Claim | null> {
    const claims = await this.getClaimsForSubtask(subtaskId);
    if (claims.length === 0) return null;

    const scoredClaims = claims.map(claim => ({
      claim,
      score: this.scoreClaim(claim)
    }));

    scoredClaims.sort((a, b) => b.score - a.score);

    const winner = scoredClaims[0];
    if (winner.score >= this.minThreshold) {
      await this.approveClaim(winner.claim.id);
      for (const { claim } of scoredClaims.slice(1)) {
        await this.rejectClaim(claim.id, 'Better claim selected');
      }
      return winner.claim;
    }
    return null;
  }

  private scoreClaim(claim: Claim): number {
    let score = 0;
    score += this.scoreTechnicalAccuracy(claim.content);  // 0-40
    score += this.scorePatternAdherence(claim.content);   // 0-20
    score += this.scoreCompleteness(claim);               // 0-20
    score += this.scoreClarity(claim.content);            // 0-20
    return score;
  }
}
```

### Step 4: Spawn Sandbox After Approval

```typescript
class SandboxManager {
  private activeSandboxes = new Map<string, Sandbox>();
  
  async spawnForClaim(claim: Claim): Promise<Sandbox> {
    if (claim.status !== 'approved') {
      throw new Error('Cannot spawn sandbox for unapproved claim');
    }

    if (this.activeSandboxes.size >= this.maxConcurrent) {
      throw new ResourceError('Max concurrent sandboxes reached');
    }

    const sandbox = await this.createSandbox({
      timeout: 300_000,
      memory: 512,
      cpu: 1,
      networkAccess: true
    });

    this.activeSandboxes.set(claim.id, sandbox);
    return sandbox;
  }
}
```

## Configuration

```yaml
claim_pool:
  enabled: true
  min_claims_before_review: 1
  max_claims_per_subtask: 5
  claim_timeout: 60000
  review_mode: quick_review

specialist_pool:
  max_concurrent: 5
  capabilities: [frontend, backend, database, testing, devops]

sandbox:
  provider: e2b
  timeout: 300000
  max_concurrent: 20

scoring:
  min_threshold: 70
  weights:
    technical_accuracy: 0.40
    pattern_adherence: 0.20
    completeness: 0.20
    clarity: 0.20
```

## Anti-Patterns

- ❌ Spawning sandboxes before claim approval
- ❌ Auto-approving claims without review
- ❌ Allowing unlimited claims per subtask
- ❌ No timeout on claim submissions
- ❌ Ignoring specialist capabilities

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No claims received | Check specialist pool, verify capabilities |
| All claims rejected | Lower threshold or improve subtask description |
| Sandbox timeout | Increase timeout, break into smaller subtasks |
| Resource exhaustion | Reduce max_concurrent, clean up sandboxes |