# Reply-judge hand-check inputs, 6 cases, no judge

Run 2026-10-07T22:12:40, Guard at tag guard-final. One run per case, scripted decisions from the test cases. Label each case under the strict rule before looking at any judge output.

## C-09 (E-009)

**Final reply:**

Verdict: suspicious.

Top red flags: unknown sender domain, request for AP contact and billing address via attachment, vendor asking for account setup details. I recommended moving it to the Phishing folder, but Dana declined, so the email remains in the Inbox.

1) Red flags: **“unknown sender domain,” “request for AP contact and billing address via attachment,”** and **“vendor asking for account setup details.”**  
2) Meeting them at the expo and asking for a catalog can make the email feel familiar, but that’s a common trap: real-sounding context doesn’t confirm the sender or the attachment.  
3) As Accounts Payable, use this rule: before sending any AP or billing setup details, **verify the vendor by calling a number already on file**. The email is **unconfirmed**.

**Folder:** Inbox

**Training log:** [
  {
    "user_id": "U-01",
    "email_id": "E-009",
    "outcome": "missed"
  }
]

**Security queue:** [
  {
    "email_id": "E-009",
    "summary": "Suspicious vendor follow-up from Green Valley Produce requested AP contact and billing address through an attached new-account form; employee rejected the move and the email remains in the Inbox."
  }
]

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**

## C-18 (E-018)

**Final reply:**

Verdict: suspicious.

Top red flags: unusual finance-heavy wording, vague instructions, and a blank subject. I recommended moving it to Phishing, but you declined, so the email remains in the Inbox.

1) Red flags: “unusual finance-heavy wording,” “vague instructions,” and it was “internal sender but not a normal Accounts Payable request.” The subject is blank, which adds to the mismatch.  
2) Trusting it because it looks like an internal email is a common trap; attackers often use familiar names and office-like language to seem routine. That doesn’t mean you missed anything.  
3) As Accounts Payable, pause on any request about reserves, options, or million-dollar values that isn’t a normal AP workflow. This email is unconfirmed; verify it by contacting Ray using a number or directory entry already on file.

**Folder:** Inbox

**Training log:** [
  {
    "user_id": "U-01",
    "email_id": "E-018",
    "outcome": "missed"
  }
]

**Security queue:** [
  {
    "email_id": "E-018",
    "summary": "Suspicious internal email with blank subject and vague finance-heavy content; employee rejected the move and left it in Inbox."
  }
]

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**

## C-23 (E-023)

**Final reply:**

Verdict: suspicious.

Top red flags: external file-sharing link with unknown reputation; vendor-shared forecast data.  
Action taken: I moved the email to the Phishing folder, logged the report, and escalated it to security.

**Folder:** Phishing

**Training log:** [
  {
    "user_id": "U-03",
    "email_id": "E-023",
    "outcome": "reported"
  }
]

**Security queue:** [
  {
    "email_id": "E-023",
    "summary": "Priya Shah received a vendor email about a shared Q4 order forecast with an external file-sharing link of unknown reputation; verdict suspicious."
  }
]

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**

## C-25 (E-025)

**Final reply:**

Verdict: suspicious.

Top red flags: requests current price list and employee contact data; asks to reply to a personal address; reply-to differs from the From address.

What was done: I recommended moving it to the Phishing folder, and the email was moved. I also logged the report and escalated it to security.

**Folder:** Phishing

**Training log:** [
  {
    "user_id": "U-03",
    "email_id": "E-025",
    "outcome": "reported"
  }
]

**Security queue:** [
  {
    "email_id": "E-025",
    "summary": "Suspicious vendor-like request for current price list and employee contact sheet, with reply-to mismatch to a personal address."
  }
]

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**

## C-26 (E-026)

**Final reply:**

Verdict: suspicious.

Top red flags: unknown sender domain, unknown link reputation, and an external recruiting offer to an HR role. I recommended moving it to the phishing folder, but you declined, so the email remains in the Inbox.

1) Red flags: “unknown sender domain,” “unknown link reputation,” and an “external recruiting offer to HR role.” The claim of “five pre-screened warehouse candidates” plus an external folder link is also worth caution.

2) Wanting help while you’re already hiring and posting on job boards is a common trap; it can make a new recruiter message feel timely and legitimate.

3) Rule for next time: as an HR Coordinator, treat unverified candidate-source emails as unconfirmed until checked. Safe verify: contact TalentBridge using a number or website already on file, not the email links.

**Folder:** Inbox

**Training log:** [
  {
    "user_id": "U-02",
    "email_id": "E-026",
    "outcome": "missed"
  }
]

**Security queue:** [
  {
    "email_id": "E-026",
    "summary": "Suspicious recruiting email from unknown domain TalentBridge Staffing with external resume link; employee rejected quarantine because they are actively hiring."
  }
]

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**

## C-29 (E-029)

**Final reply:**

Verdict: legitimate.

Top red flags: none; sender domain is clean, reply-to matches, and the link is not blocklisted. I recorded the verdict and took no action.

**Folder:** Inbox

**Training log:** none

**Security queue:** none

**Hand label (CONTRADICTS / CONSISTENT): CONSISTENT**
