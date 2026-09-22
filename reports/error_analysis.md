# Error Analysis & Edge Cases

## Common Failure Modes & Mitigations
1. **Ambiguous Deadlines**:
   - *Example*: "Let's update this soon."
   - *Behavior*: Correctly flagged with `ambiguous_deadline` and routed to Human Review Queue. Date is kept null to prevent false scheduling.
2. **Unassigned Tasks**:
   - *Example*: "Someone should update the documentation."
   - *Behavior*: Owner is set to `null` with `missing_owner` validation flag. The system never invents an owner.
3. **Past Completed Tasks**:
   - *Example*: "The team already fixed the payment bug."
   - *Behavior*: Filtered out from candidate action items.
