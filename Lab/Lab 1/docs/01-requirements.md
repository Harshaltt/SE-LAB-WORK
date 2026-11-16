# Requirements Specification

**System:** CreatorEscrow — Freelance Content Creator Escrow Platform
**Problem Statement:** #53 (Media, Events & Community)
**Document:** Deliverable 1 of 3 — Complete Requirements Table

---

## 1. Actors in Scope

| Actor | Type | Description |
|---|---|---|
| **Content Creator** | Primary (human) | The freelancer. Agrees to the milestones, uploads draft files, and gets paid once a milestone is approved. |
| **Client Sponsor** | Primary (human) | The person paying. Puts money into escrow, reviews the watermarked drafts, and signs off on each milestone. |
| **Escrow Payment Gateway** | Supporting (external system) | Handles the actual payment: collects the money, holds it, and confirms when it has moved. |
| **Media Processing Service** | Supporting (external system) | Converts the uploaded files and adds the watermark to the preview copies. |

---

## 2. Functional Requirements — Summary Table

| ID | Type | Description (short) | Priority |
|---|---|---|---|
| **FR-001** | Functional — Contract Management | Sponsor creates a contract and adds milestones; the creator has to accept it. | **High** |
| **FR-002** | Functional — Escrow / Payment | Sponsor pays for a milestone; the money is locked in escrow and nobody can withdraw it. | **High** |
| **FR-003** | Functional — File Handling | Creator uploads draft files; the sponsor only ever sees a watermarked preview. | **High** |
| **FR-004** | Functional — Review Workflow | Sponsor either approves the draft or asks for changes, with a limit on revision rounds. | **Medium** |
| **FR-005** | Functional — Escrow / Payment | Sponsor signs off, the money goes to the creator, and the sponsor gets the original files. | **High** |

## 3. Non-Functional Requirements — Summary Table

| ID | Type | Description (short) | Priority |
|---|---|---|---|
| **NFR-001** | Performance & Security | Watermarked preview ready in under 5 seconds, even with 200 uploads at once. | **High** |
| **NFR-002** | Security & Reliability | Money transfers never half-finish, never pay twice, and are always logged. | **High** |

---

## 4. Functional Requirements — Full Specification

### FR-001 — Create Contract and Define Milestones
| Field | Detail |
|---|---|
| **ID** | FR-001 |
| **Type** | Functional — Contract Management |
| **Priority** | High |
| **Description** | The system shall let a Client Sponsor create a contract, invite a Content Creator, and add between 1 and 20 milestones. Each milestone shall have a title, a description of what is to be delivered, a due date, a payment amount, and the number of revisions allowed. The contract shall become `ACTIVE` only after the invited creator accepts it. Every new milestone shall start in the state `PENDING_FUNDING`. |
| **Acceptance Criteria** | **Pass:** The milestone amounts add up to the total contract value, the creator accepts the invite, and the contract then shows as `ACTIVE` with every milestone in `PENDING_FUNDING`. **Fail:** The contract becomes `ACTIVE` without the creator accepting, the amounts do not add up, or a milestone is saved with a zero or negative amount or a due date that has already passed. |
| **Rationale** | Everything else in the system happens milestone by milestone, so the milestones have to be fixed before any work or payment starts. Making both sides accept the contract first avoids arguments later about what was actually promised. |

### FR-002 — Fund a Milestone and Lock the Money in Escrow
| Field | Detail |
|---|---|
| **ID** | FR-002 |
| **Type** | Functional — Escrow / Payment |
| **Priority** | High |
| **Description** | The system shall let the Client Sponsor pay for one milestone at a time through the Escrow Payment Gateway. The money shall be held in the platform's escrow account and the milestone shall change to `FUNDED`. Until that milestone is either released or refunded, neither the sponsor nor the creator shall be able to withdraw the money. |
| **Acceptance Criteria** | **Pass:** After the gateway confirms the payment, the milestone shows `FUNDED` and the escrow balance goes up by exactly the milestone amount, while both users' withdrawable balances stay the same. **Fail:** The milestone is marked `FUNDED` when the payment actually failed or is still pending, or the escrow money shows up in someone's withdrawable balance. |
| **Rationale** | This is the main reason a creator would trust the platform. The creator can see the money is already paid in before starting work, and the sponsor knows it cannot be taken out again without their approval. |

### FR-003 — Upload Draft Files with Automatic Watermarking
| Field | Detail |
|---|---|
| **ID** | FR-003 |
| **Type** | Functional — File Handling |
| **Priority** | High |
| **Description** | The system shall let the Content Creator upload draft files (JPEG, PNG, MP4, MOV, up to 2 GB each) to a milestone that is already `FUNDED`. For every upload the system shall create a lower-resolution watermarked preview using the Media Processing Service, and shall show only this preview to the sponsor until the milestone is released. Each upload shall be saved as a new version (v1, v2, and so on) without deleting the older ones. |
| **Acceptance Criteria** | **Pass:** The sponsor sees only watermarked previews; trying to open the original file before release returns HTTP 403; uploading again creates v2 while v1 is still available. **Fail:** The sponsor can get the original un-watermarked file before release, or a new upload overwrites an older version. |
| **Rationale** | A creator cannot hand over usable files before being paid, but the sponsor still needs to judge the work. A watermarked preview solves both problems at once. Keeping the old versions also shows exactly which file was approved or rejected if there is a disagreement later. |

### FR-004 — Review the Draft and Request Revisions
| Field | Detail |
|---|---|
| **ID** | FR-004 |
| **Type** | Functional — Review Workflow |
| **Priority** | Medium |
| **Description** | The system shall let the Client Sponsor open the latest version and record one decision: **Approve** or **Request Revision**. A revision request shall need a comment of at least 20 characters. Approving shall move the milestone to `PENDING_SIGNOFF`. Requesting a revision shall move it to `REVISION_REQUESTED`, leave the escrow money untouched, and notify the creator within 60 seconds. The number of revision rounds shall be limited to the number agreed in the contract (3 by default); after that the system shall offer to raise a dispute instead. |
| **Acceptance Criteria** | **Pass:** The comment is saved against that version, the state changes to `REVISION_REQUESTED`, and the creator gets a notification within 60 seconds. Once the revision limit is reached, further requests are blocked and the dispute option is shown instead. **Fail:** A rejection is saved with no comment, or a decision on a version can be changed after it has been submitted. |
| **Rationale** | Without a limit, a sponsor could keep asking for small changes forever while the creator's money stays locked. A fixed limit plus a written reason keeps things moving and gives an arbitrator something to look at. Marked **Medium** because the payment flow still works with approval alone — this requirement is mainly about fairness. |

### FR-005 — Sign Off the Milestone and Release the Payment
| Field | Detail |
|---|---|
| **ID** | FR-005 |
| **Type** | Functional — Escrow / Payment |
| **Priority** | High |
| **Description** | The system shall release the escrow money to the Content Creator only after the Client Sponsor (or a delegate named in the contract) logs in again and signs off. In one single transaction the system shall take the amount out of escrow, add (amount − platform fee) to the creator's balance, add the fee to the platform account, set the milestone to `COMPLETED`, give the sponsor access to the original un-watermarked files, and save an audit record. If a dispute is raised before this finishes, the milestone shall become `DISPUTED` and the money shall stay locked. |
| **Acceptance Criteria** | **Pass:** The creator's balance goes up by (amount − fee), escrow goes down by exactly the amount, the milestone shows `COMPLETED`, and the audit record stores the sponsor ID, the time, the version approved, and the signature. **Fail:** Money is released with no sign-off recorded, released twice for the same milestone, or released while the milestone is `DISPUTED`. |
| **Rationale** | This is the step the whole system exists for, and it is also the most dangerous one. Paying without approval cheats the sponsor, and paying twice loses the platform real money, so this step needs the strictest checks in the system. |

---

## 5. Non-Functional Requirements — Full Specification

### NFR-001 — Watermarking Speed and Preview Safety
| Field | Detail |
|---|---|
| **ID** | NFR-001 |
| **Type** | Performance & Security |
| **Priority** | High |
| **Description** | The watermarked preview shall be ready within **5 seconds for 95% of uploads**, measured from the moment the upload finishes to the moment the preview can be viewed. This shall hold for images up to 25 MB and for the first 60 seconds of video up to 500 MB, with 200 uploads happening at the same time. The watermark shall be clearly visible and shall include the reviewing sponsor's account ID, and the original file shall never be reachable through the preview link. |
| **Acceptance Criteria** | **Pass:** A JMeter load test with 200 uploads at once shows 95% of previews ready in 5 seconds or less, no upload fails, every preview carries the sponsor's ID in the watermark, and the preview link never returns an original file. **Fail:** The 5-second target is missed, an upload fails without telling the creator, or an un-watermarked file is served during the test. |
| **Rationale** | Slow previews hold up the milestone for both users. Watermarking is also the step most likely to be skipped when the server is under load, and one un-watermarked file leaking would defeat the whole point of using escrow. |

### NFR-002 — Safe and Reliable Money Handling
| Field | Detail |
|---|---|
| **ID** | NFR-002 |
| **Type** | Security & Reliability |
| **Priority** | High |
| **Description** | Every change to escrow shall either finish completely or not happen at all. If the same release request is sent twice — for example after a network timeout — the creator shall be paid only once. Every movement of money shall be written to an audit log that cannot be edited or deleted. Data shall be encrypted using TLS 1.3 while being sent and AES-256 while stored. The escrow service shall be available at least 99.9% of the time each month. |
| **Acceptance Criteria** | **Pass:** If the service is killed in the middle of a release, the totals still balance (escrow + user balances + fee account = money collected) and sending the request again pays the creator exactly once; the audit log has no missing entries; a security test finds no unencrypted payment data. **Fail:** A repeated request pays twice, the totals do not balance after a crash, audit entries can be edited or deleted, or uptime falls below 99.9%. |
| **Rationale** | The platform is holding money that belongs to other people. Timeouts and retries are normal on the internet, so without these rules one network glitch could pay someone twice — and without the audit log the platform would have no way to prove what it did. |

---

## 6. Requirements Traceability Matrix

| Use Case | Requirement(s) Covered | How It Is Tested |
|---|---|---|
| UC-01 Create Contract & Define Milestones | FR-001 | Check the contract only activates after acceptance and the amounts add up |
| UC-02 Fund Milestone Escrow | FR-002, NFR-002 | Payment gateway test, plus a check that the balances still add up |
| UC-03 Submit Draft Deliverable | FR-003, NFR-001 | Upload and versioning test, plus the watermarking load test |
| UC-04 Review Draft Deliverable | FR-004 | Check the decision and comment are saved and the creator is notified in time |
| UC-05 Approve Milestone & Release Payment | FR-005, NFR-002 | End-to-end release test, plus a crash-and-retry test |
| UC-08 Apply Automated Watermark *(«include»)* | FR-003, NFR-001 | Check no original file leaks, and measure the 5-second target |
| UC-09 Process Escrow Transaction *(«include»)* | FR-002, FR-005, NFR-002 | Repeat-request test and audit log check |
| UC-10 Verify Sign-off Authorization *(«include»)* | FR-005, NFR-002 | Check that only an authorised, re-logged-in sponsor can sign off |
| UC-11 Request Revision *(«extend»)* | FR-004 | Check the revision limit and the compulsory comment |
| UC-12 Raise Milestone Dispute *(«extend»)* | FR-005 (dispute part) | Check no money is released while the milestone is `DISPUTED` |
| UC-06 Withdraw Creator Balance | *Supporting* — would be FR-006, kept outside the required five | — |
| UC-07 Track Contract Progress | *Supporting* — a read-only view of the FR-001…FR-005 states; would be FR-007 | — |

> **Scope note.** UC-06 and UC-07 are shown in the use-case diagram because the actors can see them and they complete the picture of the system boundary. They do not add any new behaviour beyond the five required functional requirements, so they are listed here as deferred instead of being quietly left out of the traceability table.
