---
{
  "id": "2026-07-procurement-99",
  "redacted": true,
  "created_at": "2026-07",
  "redacted_summary": "A buyer compared two capacity paths after supplier-1 inferred schedule pressure from sequencing language.",
  "incentive_map": [
    {
      "actor_role": "buyer",
      "optimizes_for": "credible optionality while keeping the schedule stable",
      "constrained_by": "limited safe disclosure and an internal approval path"
    },
    {
      "actor_role": "supplier-1",
      "optimizes_for": "early commitment before the buyer validates fallback capacity",
      "constrained_by": "uncertain buyer alternatives"
    },
    {
      "actor_role": "internal-finance",
      "optimizes_for": "clean approval evidence before commitment",
      "constrained_by": "role-only facts from the negotiation channel"
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
      "mechanism_one_liner": "Sequencing language revealed priority before the buyer traded for a concession.",
      "mechanism_tags": [
        "signaling-leakage"
      ]
    }
  ],
  "equilibrium": {
    "observed_behavior": "Supplier-1 waits for the buyer to reveal urgency before improving the offer.",
    "stable_strategy": "The buyer keeps priority signals role-level until supplier-1 gives a concrete option.",
    "failure_mode": "Free urgency signals become leverage for the supplier side."
  },
  "cross_applications": [
    {
      "repo_slug": "agent-routing-table",
      "failing_surface": "handoff payloads expose urgency fields before a receiving agent needs them",
      "recommendation": "Keep handoff payloads to role-level state and hide preference fields until the receiving agent has a scoped need.",
      "one_sprint_fix": [
        "src/router/handoff_policy.py: drop urgency and preference fields from outbound handoff payloads",
        "tests/test_handoff_policy.py: assert role-only signals leave the router"
      ],
      "confidence": "high"
    }
  ]
}
---

# Negotiation Mechanism Replay: 2026-07-procurement-99

## Redacted summary

A buyer compared two capacity paths after supplier-1 inferred schedule pressure from sequencing language.

## Incentive map

- `buyer` optimizes for credible optionality while keeping the schedule stable; constrained by limited safe disclosure and an internal approval path.
- `supplier-1` optimizes for early commitment before the buyer validates fallback capacity; constrained by uncertain buyer alternatives.
- `internal-finance` optimizes for clean approval evidence before commitment; constrained by role-only facts from the negotiation channel.

## Leakage list

- Information from `buyer` to `supplier-1` (material): sequencing language revealed priority before the buyer traded for a concession. Tags: signaling-leakage.

## Implied equilibrium

- Observed behavior: supplier-1 waits for the buyer to reveal urgency before improving the offer.
- Stable strategy: the buyer keeps priority signals role-level until supplier-1 gives a concrete option.
- Failure mode: free urgency signals become leverage for the supplier side.

## Cross-application to portfolio repos

### agent-routing-table

- Failing surface: handoff payloads expose urgency fields before a receiving agent needs them.
- Recommendation: keep handoff payloads to role-level state and hide preference fields until the receiving agent has a scoped need.
- One-sprint fix:
  - src/router/handoff_policy.py: drop urgency and preference fields from outbound handoff payloads
  - tests/test_handoff_policy.py: assert role-only signals leave the router
- Confidence: high
