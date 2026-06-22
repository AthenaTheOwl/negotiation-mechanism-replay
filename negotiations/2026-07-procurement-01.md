---
{
  "id": "2026-07-procurement-01",
  "redacted": true,
  "created_at": "2026-07",
  "redacted_summary": "A buyer exposed fallback uncertainty while trying to preserve capacity optionality across two supplier roles.",
  "incentive_map": [
    {
      "actor_role": "buyer",
      "optimizes_for": "capacity optionality and credible fallback posture",
      "constrained_by": "limited disclosure and approval evidence needs"
    },
    {
      "actor_role": "supplier-1",
      "optimizes_for": "early lock-in before the buyer validates a fallback",
      "constrained_by": "unclear buyer switching cost"
    },
    {
      "actor_role": "supplier-2",
      "optimizes_for": "late entry after the buyer reveals urgency",
      "constrained_by": "limited visibility into the active negotiation"
    }
  ],
  "leakages": [
    {
      "kind": "information",
      "direction": {
        "from": "buyer",
        "to": "supplier-1"
      },
      "magnitude_tier": "material",
      "mechanism_one_liner": "Fallback uncertainty leaked before supplier-1 committed a concrete option.",
      "mechanism_tags": [
        "signaling-leakage",
        "commitment-credibility"
      ]
    }
  ],
  "equilibrium": {
    "observed_behavior": "Supplier-1 can wait for buyer uncertainty instead of improving the option first.",
    "stable_strategy": "The buyer states role-level constraints and withholds fallback quality until an option is on the table.",
    "failure_mode": "Unpriced fallback uncertainty becomes leverage for supplier-1."
  },
  "cross_applications": [
    {
      "repo_slug": "agent-routing-table",
      "failing_surface": "handoff payloads expose urgency fields before a receiving agent needs them",
      "recommendation": "Make the router pass role-level state until the receiving agent has a scoped need for urgency or preference fields.",
      "one_sprint_fix": [
        "src/router/handoff_policy.py: drop urgency and preference fields from outbound handoff payloads",
        "tests/test_handoff_policy.py: assert role-only signals leave the router"
      ],
      "confidence": "high"
    },
    {
      "repo_slug": "prompt-budget-ledger",
      "failing_surface": "budget commitments are recorded after the model call has already spent context",
      "recommendation": "Record the commitment before dispatch so the spender and approver see the same constraint.",
      "one_sprint_fix": [
        "src/budget/ledger.py: record budget commitments before model calls are dispatched",
        "docs/commitment-rules.md: name the condition that releases a budget hold"
      ],
      "confidence": "medium"
    }
  ]
}
---

# Negotiation Mechanism Replay: 2026-07-procurement-01

## Redacted summary

A buyer exposed fallback uncertainty while trying to preserve capacity optionality across two supplier roles.

## Incentive map

- `buyer` optimizes for capacity optionality and credible fallback posture; constrained by limited disclosure and approval evidence needs.
- `supplier-1` optimizes for early lock-in before the buyer validates a fallback; constrained by unclear buyer switching cost.
- `supplier-2` optimizes for late entry after the buyer reveals urgency; constrained by limited visibility into the active negotiation.

## Leakage list

- Information from `buyer` to `supplier-1` (material): fallback uncertainty leaked before supplier-1 committed a concrete option. Tags: signaling-leakage, commitment-credibility.

## Implied equilibrium

- Observed behavior: supplier-1 can wait for buyer uncertainty instead of improving the option first.
- Stable strategy: the buyer states role-level constraints and withholds fallback quality until an option is on the table.
- Failure mode: unpriced fallback uncertainty becomes leverage for supplier-1.

## Cross-application to portfolio repos

### agent-routing-table

- Failing surface: handoff payloads expose urgency fields before a receiving agent needs them.
- Recommendation: make the router pass role-level state until the receiving agent has a scoped need for urgency or preference fields.
- One-sprint fix:
  - src/router/handoff_policy.py: drop urgency and preference fields from outbound handoff payloads
  - tests/test_handoff_policy.py: assert role-only signals leave the router
- Confidence: high

### prompt-budget-ledger

- Failing surface: budget commitments are recorded after the model call has already spent context.
- Recommendation: record the commitment before dispatch so the spender and approver see the same constraint.
- One-sprint fix:
  - src/budget/ledger.py: record budget commitments before model calls are dispatched
  - docs/commitment-rules.md: name the condition that releases a budget hold
- Confidence: medium
