# Dev set review (answer key)

Labels and expectations for C-01 to C-10, exactly as stored in `data/test_cases.json`. Review against `dev_review_blind.md`.

| Case | Email | Category | True label | Expected verdict | Decision |
| --- | --- | --- | --- | --- | --- |
| C-01 | E-001 | clear_phish | phishing | phishing | approve |
| C-02 | E-002 | clear_phish | phishing | phishing | reject |
| C-03 | E-003 | clear_legit | legitimate | legitimate | not asked |
| C-04 | E-004 | clear_phish | phishing | phishing | approve |
| C-05 | E-005 | clear_phish | phishing | phishing | reject |
| C-06 | E-006 | clear_phish | phishing | phishing | reject |
| C-07 | E-007 | clear_legit | legitimate | legitimate | not asked |
| C-08 | E-008 | clear_legit | legitimate | legitimate | not asked |
| C-09 | E-009 | borderline | legitimate | suspicious | reject |
| C-10 | E-010 | borderline | phishing | suspicious | approve |

## C-01 · E-001

- **note:** Demo case A. Fake Microsoft 365 password-expiry notice with a blocklisted link.
- **true_label:** phishing
- **expected_verdict:** phishing
- **red_flags:** blocklisted link; newly registered sender domain; 24-hour password deadline
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-02 · E-002

- **note:** Demo case B. Bank-detail change from a one-character lookalike of Dana's real vendor. Simulation flag on.
- **true_label:** phishing
- **expected_verdict:** phishing
- **red_flags:** lookalike sender domain; reply-to differs from sender; bank detail change request
- **user_decision:** reject
- **user_reason:** That's Apex, we pay them every month.
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url

## C-03 · E-003

- **note:** Demo case C. Real invoice from Dana's real vendor with a clean portal link.
- **true_label:** legitimate
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None (not asked)
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-04 · E-004

- **note:** Payroll diversion to HR from a lookalike of the company domain. Simulation flag on.
- **true_label:** phishing
- **expected_verdict:** phishing
- **red_flags:** lookalike of company domain; direct deposit change request; urgency before payroll
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url

## C-05 · E-005

- **note:** Executive gift-card request from personal webmail: the classic CEO-fraud pattern. Clean domain, but content signals are clear.
- **true_label:** phishing
- **expected_verdict:** phishing
- **red_flags:** executive request from personal webmail; gift card purchase with codes by email; secrecy and urgency
- **user_decision:** reject
- **user_reason:** Elena emails from her personal account when she travels.
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url

## C-06 · E-006

- **note:** Failed-delivery notice with a blocklisted link and a small payment demand.
- **true_label:** phishing
- **expected_verdict:** phishing
- **red_flags:** blocklisted link; malicious sender domain; payment demand with 48-hour deadline
- **user_decision:** reject
- **user_reason:** I'm expecting samples from a supplier this week.
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-07 · E-007

- **note:** Real benefits vendor, known to Marcus, clean portal link, no request for money or data.
- **true_label:** legitimate
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None (not asked)
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-08 · E-008

- **note:** Internal meeting agenda from a coworker on the company domain with a clean intranet link.
- **true_label:** legitimate
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None (not asked)
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-09 · E-009

- **note:** First-contact vendor with an unknown domain asking for billing details. Truly legitimate, risky-looking.
- **true_label:** legitimate
- **expected_verdict:** suspicious
- **red_flags:** unknown sender domain; request for billing details from a first-contact vendor
- **user_decision:** reject
- **user_reason:** We met them at the expo last month and I asked for the catalog.
- **required_tools:** classify_email_text, check_sender_domain, check_url, get_user_profile
- **forbidden_tools:** none

## C-10 · E-010

- **note:** Known vendor's real domain sends an odd bank-change request. Truly phishing (compromised mailbox), clean sender evidence.
- **true_label:** phishing
- **expected_verdict:** suspicious
- **red_flags:** bank detail change request; no verification path offered
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url
