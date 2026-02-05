---
name: textgrad-correction
description: Implement TextGrad-style self-correction loops for AI agents. Use when building agents that need to critique and refine their outputs, implementing iterative improvement cycles, or creating quality-assured AI workflows with automated feedback.
---

# TextGrad Self-Correction

**Origin**: Overwatch Agent Network - Prompt Programming Framework  
**Reference**: TextGrad (Yuksekgonul et al., 2024)

## When to Use

- Building agents that improve outputs iteratively
- Implementing quality gates with automated refinement
- Creating self-critique and revision loops
- Designing agents that can recover from errors
- Building high-reliability AI systems

## Core Concept

TextGrad applies gradient descent concepts to text:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-CORRECTION KERNEL                        │
├─────────────────────────────────────────────────────────────────┤
│  1. DRAFT: Generate tentative output                             │
│                     ↓                                            │
│  2. CRITIC: Evaluate against criteria                            │
│             "Does this match the specification?"                 │
│             "Is this action safe?"                               │
│             "Is this the most efficient approach?"               │
│                     ↓                                            │
│  3. GRADIENT: Generate textual feedback                          │
│             "The code is missing error handling..."              │
│                     ↓                                            │
│  4. REFINE: Apply feedback to improve output                     │
│                     ↓                                            │
│  5. VALIDATE: Check if threshold met                             │
│             └── If not: LOOP back to CRITIC                      │
│             └── If yes: EXECUTE final action                     │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

```yaml
self_correction:
  enabled: true
  max_iterations: 3
  threshold: 0.85
  
  criteria:
    - name: completeness
      weight: 0.30
      description: "Is the implementation fully functional?"
    
    - name: correctness
      weight: 0.25
      description: "Does it correctly solve the problem?"
    
    - name: safety
      weight: 0.20
      description: "Are there any security concerns?"
    
    - name: efficiency
      weight: 0.15
      description: "Is this the optimal approach?"
    
    - name: style
      weight: 0.10
      description: "Does it follow project conventions?"

  stop_conditions:
    - "All criteria score >= threshold"
    - "Max iterations reached"
    - "No improvement between iterations"
```

## Implementation

### Basic Loop

```typescript
interface SelfCorrectionConfig {
  maxIterations: number;
  threshold: number;
  criteria: CriterionConfig[];
}

interface CorrectionResult {
  output: string;
  score: number;
  iterations: number;
  gradients: TextualGradient[];
}

async function selfCorrect(
  draft: string,
  config: SelfCorrectionConfig
): Promise<CorrectionResult> {
  let current = draft;
  let gradients: TextualGradient[] = [];
  
  for (let i = 0; i < config.maxIterations; i++) {
    // Critique phase
    const critique = await evaluateCriteria(current, config.criteria);
    
    if (critique.score >= config.threshold) {
      return { output: current, score: critique.score, iterations: i, gradients };
    }
    
    // Generate textual gradient
    const gradient = await generateGradient(current, critique);
    gradients.push(gradient);
    
    // Refine phase
    current = await applyGradient(current, gradient);
  }
  
  return { output: current, score: await score(current), iterations: config.maxIterations, gradients };
}
```

### Critique Function

```typescript
interface Criterion {
  name: string;
  weight: number;
  description: string;
}

interface Critique {
  score: number;
  feedback: CriterionFeedback[];
}

async function evaluateCriteria(
  output: string,
  criteria: Criterion[]
): Promise<Critique> {
  const feedback: CriterionFeedback[] = [];
  let totalScore = 0;
  
  for (const criterion of criteria) {
    const evaluation = await llm.evaluate({
      prompt: `
        Evaluate this output against the criterion:
        
        Criterion: ${criterion.name}
        Description: ${criterion.description}
        
        Output:
        ${output}
        
        Provide:
        1. Score (0-1)
        2. Specific feedback
        3. Suggested improvements
      `,
      schema: CriterionFeedbackSchema
    });
    
    feedback.push({
      criterion: criterion.name,
      score: evaluation.score,
      feedback: evaluation.feedback,
      improvements: evaluation.improvements
    });
    
    totalScore += evaluation.score * criterion.weight;
  }
  
  return { score: totalScore, feedback };
}
```

### Gradient Generation

```typescript
interface TextualGradient {
  issues: string[];
  suggestions: string[];
  priority: 'high' | 'medium' | 'low';
}

async function generateGradient(
  current: string,
  critique: Critique
): Promise<TextualGradient> {
  // Focus on lowest-scoring criteria
  const weakPoints = critique.feedback
    .filter(f => f.score < 0.7)
    .sort((a, b) => a.score - b.score);
  
  return await llm.generate({
    prompt: `
      The current output has these issues:
      ${weakPoints.map(w => `- ${w.criterion}: ${w.feedback}`).join('\n')}
      
      Generate a textual gradient - specific, actionable feedback
      that would improve the output:
    `,
    schema: TextualGradientSchema
  });
}
```

### Refinement

```typescript
async function applyGradient(
  current: string,
  gradient: TextualGradient
): Promise<string> {
  return await llm.generate({
    prompt: `
      Original output:
      ${current}
      
      Feedback to apply:
      Issues: ${gradient.issues.join(', ')}
      Suggestions: ${gradient.suggestions.join(', ')}
      
      Generate an improved version that addresses this feedback.
      Preserve what works well. Only change what needs improvement.
    `
  });
}
```

## Agent Integration

```yaml
name: specialist-backend
tier: ag

self_correction:
  enabled: true
  max_iterations: 2
  threshold: 0.85
  
  criteria:
    - name: "Completeness"
      description: "Is the implementation fully functional?"
      weight: 0.25
    
    - name: "Test Coverage"
      description: "Are all requirements tested?"
      weight: 0.25
    
    - name: "Error Handling"
      description: "Are edge cases and errors handled?"
      weight: 0.20
    
    - name: "Pattern Adherence"
      description: "Does it follow existing patterns?"
      weight: 0.15
    
    - name: "Performance"
      description: "Is the implementation efficient?"
      weight: 0.15

workflow:
  - step: 1
    action: "Generate initial implementation"
    tool: Write
  
  - step: 2
    action: "Self-critique against criteria"
    self_correction: true
  
  - step: 3
    action: "Apply textual gradient if needed"
    condition: "score < threshold"
  
  - step: 4
    action: "Final validation"
    tool: Bash
```

## Trace Collection

Collect successful corrections for optimization:

```yaml
traces:
  enabled: true
  auto_collect: true
  min_score: 0.80
  
  collect:
    - initial_draft
    - gradients
    - final_output
    - score_progression
```

## Examples

### Code Quality Correction

```
DRAFT:
function processUser(user) {
  return db.save(user);
}

CRITIQUE:
- Completeness: 0.4 - Missing validation, error handling
- Safety: 0.3 - No input sanitization
- Style: 0.8 - Simple and readable

GRADIENT:
Issues: No input validation, missing try-catch, no return type
Suggestions: Add Zod validation, wrap in try-catch, add TypeScript types

REFINED:
async function processUser(user: UserInput): Promise<Result<User>> {
  const validated = UserSchema.safeParse(user);
  if (!validated.success) {
    return { ok: false, error: validated.error };
  }
  
  try {
    const saved = await db.save(validated.data);
    return { ok: true, data: saved };
  } catch (error) {
    logger.error('Failed to save user', { error, user: validated.data });
    return { ok: false, error: new DatabaseError(error) };
  }
}

FINAL SCORE: 0.92 ✓
```

## Anti-Patterns

- ❌ Infinite correction loops (always set max_iterations)
- ❌ Criteria without clear definitions
- ❌ Ignoring unchanged scores between iterations
- ❌ Not preserving good aspects during refinement
- ❌ Too many criteria (focus on 3-5 key aspects)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Score not improving | Check gradient specificity, reduce criteria |
| Overcorrection | Lower weights, add "preserve what works" instruction |
| Slow convergence | Increase gradient detail, focus on critical issues |
| Inconsistent scores | Use structured evaluation, calibrate criteria |