# Review notes: C-11 to C-30

Reasoning behind every `expected_verdict` and `red_flags` entry for the 20 cases added on 2026-10-05, for review before the first full evaluation run. The dev set (C-01 to C-10) is unchanged; its review is in `dev_review_key.md`.

"Classifier" is `phish_clf.joblib` on subject + body at the 0.5 threshold. It was run offline, with no API calls, only to inform these notes. No case was labeled from it.

## Totals across all 30

| | clear_phish | clear_legit | borderline | All |
| --- | --- | --- | --- | --- |
| Cases | 10 | 10 | 10 | 30 |
| Approve / reject / not asked | 5 / 5 / 0 | 0 / 0 / 10 | 5 / 5 / 0 | 10 / 10 / 10 |
| Simulations | 4 (E-002, E-004, E-014, E-015) | 0 | 0 | 4 |
| Borderline truth | | | 5 phishing (C-10, C-23 to C-26), 5 legitimate (C-09, C-27 to C-30) | |

Phishing types across the set: credential harvest (E-001), bank-detail change (E-002, E-010), payroll diversion (E-004), executive gift cards (E-005), delivery notice (E-006), MFA reset (E-014), voicemail notice (E-015), shared document (E-023), executive payment request (E-024), contact-data harvest (E-025), and resume malware lure (E-026). The three Kaggle phishing rows are bulk spam (pharmacy and word salad); see the caveat below.

## How I applied the borderline rule

A case is labeled `suspicious` only if, under Guard's own DECIDE rule, nothing in the data is decisive:

- Decisive for phishing: a lookalike or malicious domain, a blocklisted link, or a reply-to mismatch combined with a money or credential request.
- Decisive for legitimate: clean sender and clean links, with no risky request.

Every borderline case was built to have neither, so all eight new ones are `suspicious`. Where the content itself is a clear signal (for example, gift cards with secrecy, as in C-05), the case went to clear_phish instead. I removed one such signal while drafting: E-026 originally said "enable editing", a strong macro-malware cue, and I cut it so the case stays truly ambiguous.

Two pairs share the same evidence shape on purpose and have opposite truths: E-025 (phishing) and E-030 (legitimate), and E-026 (phishing) and E-009 (legitimate). Within each pair `suspicious` is the only verdict the data supports, and that is the honest borderline test.

## Kaggle rows (C-11 to C-13, C-16 to C-18)

The body is the exact `text` field from `data/kaggle_holdout.json`, which the splice script checked for equality. The subject is `""`, so the classifier input matches the holdout. The scores reproduce the stored `classifier_prob` exactly (0.987, 0.987, 0.655, 0.023, 0.002, 0.119). Each email has a synthetic `.example` From address and `links: []`. The bodies contain mangled host strings with their dots stripped by preprocessing, such as `traditionstreetcom` and `pythonorg`. These are not domains or links, so they get no threat-intel rows.

**Caveat on the phishing rows.** The Kaggle corpus labels spam as phishing (PLAN.md notes it mixes the two). All three rows are bulk spam, not targeted phishing. Their `expected_verdict: phishing` rests on the sender row I assigned: a malicious domain, 4 to 15 days old. That is a design choice, not something in the original data. If you'd rather not invent a reputation for them, the alternative is an unknown domain, which by the rule above would make C-13 (word salad, 0.655) `suspicious` and move it to borderline.

## Per-case reasoning

### C-11 · E-011 · clear_phish · approve
- **Verdict phishing:** the sender domain `rx-bestprice.example` is malicious, which is decisive under the DECIDE rule. The classifier agrees at 0.987.
- `malicious sender domain`: threat-intel row reputation malicious.
- `newly registered sender domain`: age_days 4.
- `unsolicited pharmacy offer`: the body advertises cialis with fast shipping and special prices, and the recipient (Priya, Sales) has no reason to get it.

### C-12 · E-012 · clear_phish · reject
- **Verdict phishing:** `pharma-fastship.example` is malicious, and the classifier gives 0.987.
- `malicious sender domain`: reputation malicious.
- `newly registered sender domain`: age_days 7.
- `unsolicited pharmacy offer`: the body offers "reliable chemists", a cure, and fast delivery.
- **User reason:** Marcus (HR) mistakes it for a benefits-provider pharmacy discount. That is plausible for his role and gives Coach a role-tied lesson.

### C-13 · E-013 · clear_phish · approve
- **Verdict phishing:** `bulkmail-relay.example` is malicious. The classifier is only 0.655, so the sender row is what makes this case clear (see the caveat above).
- `malicious sender domain`: reputation malicious.
- `newly registered sender domain`: age_days 15.
- `meaningless word-salad text`: the body is a list of unrelated words, a filter-evasion pattern with no business content.

### C-14 · E-014 · clear_phish · reject · simulation
- **Verdict phishing:** `harb0rfoods.example` is a lookalike of the company domain, with zero in place of the letter o (`lookalike_of: harborfoods.example`, suspicious, 5 days old). A lookalike is decisive. The classifier gives a weak 0.596.
- `lookalike of company domain`: the From domain row.
- `link to lookalike domain`: the link sits on the same lookalike host, and its URL row has lookalike_of harborfoods.example. It is not blocklisted, so this case tests lookalike detection without a blocklist hit.
- `asks for password and MFA code`: "Re-enroll here with your current password and the code from your authenticator app."
- `same-day lockout threat`: "Accounts not re-enrolled by 5pm today will be locked out."
- **Tools:** the required tools are classify, sender, and url. `get_user_profile` is not required, matching C-01, the other credential-harvest case. This depends on the open question about C-01 in PROGRESS.md, so decide both together.

### C-15 · E-015 · clear_phish · approve · simulation
- **Verdict phishing:** the link is blocklisted and the sender domain is malicious. Either is decisive. The classifier gives 0.72.
- `blocklisted link`: URL row on_blocklist true.
- `malicious sender domain`: `voicemail-notify.example`, malicious, 8 days old.
- `voicemail requires Microsoft 365 sign-in`: "To listen, sign in with your Microsoft 365 account." A voicemail doesn't need an account sign-in.

### C-16 · E-016 · clear_legit
- **Verdict legitimate:** the sender is a coworker on `harborfoods.example` (clean, 5840 days). There are no links and no request, just a vacation notice. The classifier gives 0.023. No red flags.
- The sender name Aimee matches the sign-off "let know aimee" in the original text.

### C-17 · E-017 · clear_legit
- **Verdict legitimate:** the sender is `lists.devforum.example` (clean, 5100 days, a new row). The body is a technical mailing-list post about a CSV module. There is no request and no link. The classifier gives 0.002. No red flags.
- The domain isn't in Priya's known_domains. A clean, long-standing domain with no request is still decisive for legitimate under the rule, so it was not made borderline.

### C-18 · E-018 · clear_legit
- **Verdict legitimate:** the sender is a coworker on `harborfoods.example`. It is an internal note about valuation reserves with no request and no link. The classifier gives 0.119. No red flags.
- The content is energy-trading text (Enron) that doesn't fit a food distributor. I kept it because you asked for the original text unchanged.

### C-19 · E-019 · clear_legit
- **Verdict legitimate:** `paywell.example` is clean and in Marcus's known_domains. The link `portal.paywell.example/calendar/2026-q4` is clean (new row). The email says "there is nothing you need to do today." The classifier gives 0.098. No red flags.

### C-20 · E-020 · clear_legit
- **Verdict legitimate:** `coastalfreight.example` is clean and in Dana's known_domains, and the tracking link is clean (new row). It is a delivery confirmation with no payment or action requested, the legitimate counterpart to E-006. No red flags.
- **Classifier false positive:** 0.54, probably from delivery and tracking wording. That's a useful finding: the agent should clear an email the classifier alone would flag.

### C-21 · E-021 · clear_legit
- **Verdict legitimate:** `northstar-grocers.example` is clean and in Priya's known_domains. Asking for a quote is a normal sales request, not money, credentials, or sensitive data, and the email offers a phone call. The classifier gives 0.066. No red flags.

### C-22 · E-022 · clear_legit
- **Verdict legitimate:** the sender is `harborfoods.example`. There are no links and no request ("You do not need to do anything"). It is the legitimate counterpart to E-014. The classifier gives 0.047. No red flags.

### C-23 · E-023 · borderline · truly phishing · approve
- **Verdict suspicious:** the sender `metrodeli.example` is clean and in Priya's known_domains. That points to legitimate but doesn't prove it, because the ground truth is a compromised mailbox. The link `filedrop-share.example` has no row, so it is unknown. The body asks for nothing beyond opening a file. No phishing rule fires and the evidence isn't fully clean, so the case is mixed.
- `unknown file-sharing link`: no threat-intel row, deliberately.
- `shared document from an external sender`: a shared-document notice is the lure type, even from a known contact.
- The classifier gives 0.199, so the classifier alone would miss it.

### C-24 · E-024 · borderline · truly phishing · reject
- **Verdict suspicious:** the sender is the CFO's real address on `harborfoods.example`, which is clean. There are no links, no reply-to mismatch, and no secrecy. The ground truth is a compromised mailbox.
- `payment to a payee not in vendor records`: Gulf Coast Events LLC is not in Dana's known_domains, and the email says "They aren't set up as a vendor yet."
- `request to skip vendor setup`: "could you add them directly". This is a real business-email-compromise indicator, but executives do make this request legitimately.
- `deadline tied to the payment run`: "include this in Thursday's payment run... They need it before the event." This is mild urgency, not a threat.
- **This is the closest call of the eight.** Someone could argue clean sender evidence makes it `legitimate`. I chose `suspicious` because a new payee that bypasses vendor onboarding is exactly the mixed evidence the DECIDE rule describes. Please check this one.

### C-25 · E-025 · borderline · truly phishing · approve
- **Verdict suspicious:** the sender `freshmarket-co.example` is clean and in Priya's known_domains, but the reply-to is personal webmail on `quickmail.example` (clean). The phishing rule needs a reply-to mismatch plus a money or credential request. This email asks for data (a price list and staff contacts), so the rule doesn't fire, and the data is still mixed.
- `reply-to differs from sender`: From is `nora.whitley@freshmarket-co.example` and Reply-To is `nora.whitley.fm@quickmail.example`.
- `reply-to is personal webmail`: `quickmail.example` is the personal webmail domain already used in E-005.
- `request for staff contact details`: names, direct lines, and emails for the sales and AP teams. That is reconnaissance for invoice fraud.

### C-26 · E-026 · borderline · truly phishing · reject
- **Verdict suspicious:** both the sender domain and the link are unknown (no rows, deliberately). The email is an unsolicited first contact with a file to open. A legitimate recruiter cold email looks the same, and E-009 has the same evidence shape with a legitimate truth, so nothing here is decisive.
- `unknown sender domain`: `talentbridge-staffing.example`, no row.
- `unknown link`: no row.
- `unsolicited first contact with files to open`: "Their resumes are in this folder." The ground truth is a malware-hosting lure.

### C-27 · E-027 · borderline · truly legitimate · approve
- **Verdict suspicious:** the sender and link are unknown, the email asks for $1,950, and it has a 48-hour countdown. That leans risky, but the expo is real (E-009 refers to it) and the domain isn't malicious or a lookalike. This is PLAN.md's "real marketing email with countdown urgency" example.
- `unknown sender domain`: `midwestfoodexpo.example`, no row, deliberately.
- `unknown link`: no row.
- `payment request with 48-hour countdown`: "Early-bird pricing ... ends in 48 hours. Reserve your booth now for $1,950."

### C-28 · E-028 · borderline · truly legitimate · reject
- **Verdict suspicious:** the sender `paywell.example` is clean and in Marcus's known_domains, and the email gives a safe verification path ("call your service team at the number in your PayWell contract"). Against that, it asks for a sign-in with a deadline on a link with no row. The signals point both ways.
- `unknown link on a vendor subdomain`: `verify.paywell.example` has no URL row, even though the parent domain is clean.
- `sign-in request with an access-pause deadline`: "sign in and confirm your administrator role by October 15, or your admin access will be paused".

### C-29 · E-029 · borderline · truly legitimate · reject
- **Verdict suspicious:** the sender is `harborfoods.example` (clean). The email asks staff to create an account on an unknown third-party domain by Friday and says old-style reports won't be reimbursed. There is no lookalike and no blocklist hit, but the link is unknown and it's a credential-creation request.
- `unknown third-party sign-up link`: `harborfoods.tallyline.example`, no row. The domain `tallyline.example` appears only in this link.
- `account creation with a deadline`: "create your account by Friday".

### C-30 · E-030 · borderline · truly legitimate · approve
- **Verdict suspicious:** the evidence matches C-25 (known customer domain, personal-webmail reply-to, data request), and the truth is the opposite. The email gives a believable reason (a mail migration) but no way to verify it.
- `reply-to differs from sender`: From is `maya.torres@northstar-grocers.example` and Reply-To is `maya.torres.work@quickmail.example`.
- `reply-to is personal webmail`: `quickmail.example`.
- `request to send business data to a personal address`: the November delivery schedule.

## Things to check

1. **Defanged links.** The new links use the same plain `https://...example` form as E-001 to E-010, not `hxxps://` or `[.]`. `.example` is a reserved TLD that can't resolve. Defanging only the new 20 would also give Guard and the classifier a signal the dev set doesn't have. `check_world.py` requires `.example` in each link, and `check_url` matches exact text. If you want all 30 defanged, that's one consistent change, but it touches the tuned dev emails.
2. **C-24's verdict** (the closest call, see above) and **the Kaggle sender reputations** (see the caveat above).
3. **`get_user_profile` requirements.** I required it where the profile changes the reading of the email (C-23 to C-26, C-28, C-30), following C-09 and C-10. I left it optional where the case is settled without it (C-14, C-15, C-27, C-29, and every clear_legit case), following C-01, C-03, C-07, and C-08.
4. **Classifier alone on the 20 new emails:** it flags E-011 to E-015 (all clear phish) and E-020 (legitimate, 0.54). It misses all four borderline phishing cases (E-023 to E-026, between 0.15 and 0.27).

## Files changed

- `data/emails.json`: E-011 to E-030 appended. E-001 to E-010 untouched.
- `data/test_cases.json`: C-11 to C-30 appended. C-01 to C-10 untouched.
- `data/threat_intel.json`: 6 domain rows and 4 URL rows added, and the `_comment` list of deliberately unknown items extended.
- `scripts/check_world.py`: only the two deliberately-unknown sets were extended (2 domains, 5 URLs). Every check is unchanged. Result: `world OK`, 30 emails, 10/10/10, 10 approve / 10 reject / 10 not asked, 4 simulations.
