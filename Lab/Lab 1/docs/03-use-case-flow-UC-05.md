# Use-Case Flow Specification — UC-05

**System:** CreatorEscrow · **Document:** Deliverable 3 of 3 · **Covers:** FR-005, NFR-002

> Typeset single-page version for submission: **[`03-use-case-flow-UC-05.pdf`](03-use-case-flow-UC-05.pdf)** (generated from [`03-use-case-flow-UC-05.html`](03-use-case-flow-UC-05.html) — checked to fit exactly one A4 page).

| Field | Value |
|---|---|
| **Use Case ID / Name** | UC-05 — Approve Milestone & Release Escrow Payment |
| **Scope / Level** | CreatorEscrow Platform · User-goal level |
| **Primary Actor** | Client Sponsor |
| **Supporting Actors** | Escrow Payment Gateway (moves the money); Content Creator (gets notified) |
| **Trigger** | Sponsor clicks **Approve & Release** on a milestone in `PENDING_SIGNOFF`. |
| **Frequency** | 1–20 times per contract. It is the most important transaction in the system. |

**Stakeholders & Interests** — *Content Creator:* wants to be paid quickly, and paid once. *Client Sponsor:* wants to pay only for work they have personally approved, and to get the original files afterwards. *Platform:* wants the account totals to stay balanced and every payment to be traceable.

### Preconditions
1. The Client Sponsor is logged in, and has passed two-factor authentication in the last 12 hours.
2. The contract is `ACTIVE` and this sponsor is either part of it or a delegate named in it.
3. The milestone is in state `PENDING_SIGNOFF`, meaning the sponsor already approved the latest version in UC-04.
4. The escrow account is holding exactly the milestone amount (the milestone was `FUNDED` in FR-002).
5. There is no open dispute on this milestone.

### Postconditions
**If it succeeds**
1. The milestone is `COMPLETED`, and a sign-off record has been saved with the sponsor ID, the time, which version was approved, and the signature.
2. The milestone amount comes out of escrow, (amount − platform fee) goes into the creator's balance, and the fee goes to the platform account. The totals still add up.
3. The sponsor can now download the original un-watermarked files, and the licence terms are saved.
4. An entry is added to the audit log and both users are notified.
5. The milestone can no longer be revised or disputed.

**If anything fails** — the whole transaction is rolled back. The milestone stays `PENDING_SIGNOFF`, the money stays in escrow, nobody is partly paid, and the failure is written to the log.

### Main Success Scenario
1. Sponsor opens the milestone from the contract dashboard and clicks **Approve & Release**.
2. System runs UC-10 *Verify Sign-off Authorization*: is the session still valid, is this sponsor allowed to sign off on this contract, is the milestone in the right state, and is there no dispute open?
3. System shows a summary before confirming: which version was approved, the total amount, the platform fee, what the creator will actually receive, and the licence terms.
4. Sponsor confirms by entering their password again or a one-time passcode.
5. System saves the sign-off so it cannot later be denied: sponsor ID, the time, a SHA-256 hash of the approved version, and the signature.
6. System starts a single transaction, creates a unique request key so the payment cannot happen twice, and runs UC-09 *Process Escrow Transaction* to move the money out of escrow and into the creator's balance.
7. Escrow Payment Gateway confirms the payment went through for that request key.
8. System commits the transaction, marks the milestone `COMPLETED`, and writes the audit record.
9. System gives the sponsor access to the original un-watermarked files and records the licence transfer.
10. System tells the creator the money is available and the sponsor the files are available, then moves the contract on to the next milestone, or closes it if this was the last one.

### Alternate Flow — A1: Sponsor Asks for Changes Instead of Approving
*Branches at step 3, at the extension point **Decision Recorded**. This is UC-11.*

- **A1.1** At the summary screen the sponsor clicks **Request Revision** instead of confirming.
- **A1.2** System asks for a comment of at least 20 characters and checks how many revision rounds have already been used against the agreed limit (FR-004).
- **A1.3** *Limit not reached:* System saves the comment against version v(n), sets the milestone to `REVISION_REQUESTED`, leaves the escrow money alone, and notifies the creator within 60 seconds. The flow goes back to UC-03 for version v(n+1), and **UC-05 ends without any money being released.**
- **A1.4** *Limit reached:* System blocks the request, explains that all the agreed revisions have been used, and offers UC-12 *Raise Milestone Dispute* instead. The milestone stays `PENDING_SIGNOFF`.

### Exception Flows *(extra — the required alternate flow is A1 above)*
- **E1 — Gateway times out at step 7.** The transaction is rolled back and the milestone stays `PENDING_SIGNOFF`. The system retries with the *same* request key up to 3 times, waiting a bit longer each time. If it still fails, the milestone is flagged `RELEASE_PENDING_MANUAL` and the support team is alerted. Because the key never changes, the creator can never be paid twice (NFR-002).
- **E2 — A dispute is raised at the same time (UC-12).** The system notices the milestone changed between steps 5 and 8 by checking its version number, cancels the release, keeps the money locked, and moves the milestone to `DISPUTED`.

### Business Rules
| ID | Rule |
|---|---|
| BR-01 | Money never leaves escrow without a sign-off record, as required by FR-005. |
| BR-02 | A milestone can be released at most once. The unique request key enforces this (NFR-002). |
| BR-03 | The sponsor gets the original files only at the moment the payment actually succeeds. |
| BR-04 | If a dispute is raised before the transaction commits, the dispute wins and the release is cancelled. |
