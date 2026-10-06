# New cases review (answer key)

Labels and expectations for C-11 to C-30, exactly as stored in `data/test_cases.json`. Review against `new_review_blind.md`. Reasoning for each label is in `review_notes.md`.

| Case | Email | Category | True label | Expected verdict | Decision |
| --- | --- | --- | --- | --- | --- |
| C-11 | E-011 | clear_phish | phishing | phishing | approve |
| C-12 | E-012 | clear_phish | phishing | phishing | reject |
| C-13 | E-013 | clear_phish | phishing | phishing | approve |
| C-14 | E-014 | clear_phish | phishing | phishing | reject |
| C-15 | E-015 | clear_phish | phishing | phishing | approve |
| C-16 | E-016 | clear_legit | legitimate | legitimate | not asked |
| C-17 | E-017 | clear_legit | legitimate | legitimate | not asked |
| C-18 | E-018 | clear_legit | legitimate | legitimate | not asked |
| C-19 | E-019 | clear_legit | legitimate | legitimate | not asked |
| C-20 | E-020 | clear_legit | legitimate | legitimate | not asked |
| C-21 | E-021 | clear_legit | legitimate | legitimate | not asked |
| C-22 | E-022 | clear_legit | legitimate | legitimate | not asked |
| C-23 | E-023 | borderline | phishing | suspicious | approve |
| C-24 | E-024 | borderline | phishing | suspicious | reject |
| C-25 | E-025 | borderline | phishing | suspicious | approve |
| C-26 | E-026 | borderline | phishing | suspicious | reject |
| C-27 | E-027 | borderline | legitimate | suspicious | approve |
| C-28 | E-028 | borderline | legitimate | suspicious | reject |
| C-29 | E-029 | borderline | legitimate | suspicious | reject |
| C-30 | E-030 | borderline | legitimate | suspicious | approve |

## C-11 · E-011

- **true_label:** phishing
- **category:** clear_phish
- **expected_verdict:** phishing
- **red_flags:** malicious sender domain; newly registered sender domain; unsolicited pharmacy offer
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-12 · E-012

- **true_label:** phishing
- **category:** clear_phish
- **expected_verdict:** phishing
- **red_flags:** malicious sender domain; newly registered sender domain; unsolicited pharmacy offer
- **user_decision:** reject
- **user_reason:** I thought it was one of the pharmacy discount offers we get through our benefits provider.
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-13 · E-013

- **true_label:** phishing
- **category:** clear_phish
- **expected_verdict:** phishing
- **red_flags:** malicious sender domain; newly registered sender domain; meaningless word-salad text
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-14 · E-014

- **true_label:** phishing
- **category:** clear_phish
- **expected_verdict:** phishing
- **red_flags:** lookalike of company domain; link to lookalike domain; asks for password and MFA code; same-day lockout threat
- **user_decision:** reject
- **user_reason:** IT said everyone has to set up MFA again this month.
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-15 · E-015

- **true_label:** phishing
- **category:** clear_phish
- **expected_verdict:** phishing
- **red_flags:** blocklisted link; malicious sender domain; voicemail requires Microsoft 365 sign-in
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-16 · E-016

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-17 · E-017

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-18 · E-018

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-19 · E-019

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-20 · E-020

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-21 · E-021

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-22 · E-022

- **true_label:** legitimate
- **category:** clear_legit
- **expected_verdict:** legitimate
- **red_flags:** none
- **user_decision:** None
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain
- **forbidden_tools:** check_url

## C-23 · E-023

- **true_label:** phishing
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** unknown file-sharing link; shared document from an external sender
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url, get_user_profile
- **forbidden_tools:** none

## C-24 · E-024

- **true_label:** phishing
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** payment to a payee not in vendor records; request to skip vendor setup; deadline tied to the payment run
- **user_decision:** reject
- **user_reason:** Rob is our CFO and he sends me sponsorship invoices to add to the run all the time.
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url

## C-25 · E-025

- **true_label:** phishing
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** reply-to differs from sender; reply-to is personal webmail; request for staff contact details
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url

## C-26 · E-026

- **true_label:** phishing
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** unknown sender domain; unknown link; unsolicited first contact with files to open
- **user_decision:** reject
- **user_reason:** We're hiring for the warehouse and I've been posting on job boards.
- **required_tools:** classify_email_text, check_sender_domain, check_url, get_user_profile
- **forbidden_tools:** none

## C-27 · E-027

- **true_label:** legitimate
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** unknown sender domain; unknown link; payment request with 48-hour countdown
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-28 · E-028

- **true_label:** legitimate
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** unknown link on a vendor subdomain; sign-in request with an access-pause deadline
- **user_decision:** reject
- **user_reason:** PayWell makes us re-verify admin access every year before W-2 season.
- **required_tools:** classify_email_text, check_sender_domain, check_url, get_user_profile
- **forbidden_tools:** none

## C-29 · E-029

- **true_label:** legitimate
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** unknown third-party sign-up link; account creation with a deadline
- **user_decision:** reject
- **user_reason:** Finance announced the new expense tool at the all-hands.
- **required_tools:** classify_email_text, check_sender_domain, check_url
- **forbidden_tools:** none

## C-30 · E-030

- **true_label:** legitimate
- **category:** borderline
- **expected_verdict:** suspicious
- **red_flags:** reply-to differs from sender; reply-to is personal webmail; request to send business data to a personal address
- **user_decision:** approve
- **user_reason:** None
- **required_tools:** classify_email_text, check_sender_domain, get_user_profile
- **forbidden_tools:** check_url
