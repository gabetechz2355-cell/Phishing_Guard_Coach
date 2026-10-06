Note: before this review I had read the session summary, which said all 8 new borderline cases were labeled suspicious.

Note: the verdicts below were written before I opened the answer key. This file was committed after the key-lock commit (the PROGRESS.md entry), so git history alone does not prove that order. PROGRESS.md and this note record it.

---

I completed a blind first-pass human review of cases E-011 through E-030 before comparing against the answer key. Please preserve these original judgments as my human first-pass baseline. Do not overwrite them with the answer key.

My review used three verdicts: phishing, suspicious, legitimate. I also considered which Guard checks should be run:

- C = Content
- S = Sender
- L = Link
- P = Profile/context

## Important note about my first-pass assumptions

During the blind review, I interpreted phishing somewhat narrowly. I was looking for recognizable phishing behavior such as credential theft, impersonation, malicious links, financial requests, MFA theft, or another clear social-engineering objective.

That caused an ambiguity around cases like E-011 through E-013. Their sender infrastructure was clearly malicious and the messages resembled malicious/spam content, but because they did not contain a traditional phishing lure, I treated them as suspicious rather than phishing.

In other words, I was mentally distinguishing:

malicious spam → suspicious
from
traditional phishing/social engineering → phishing

The answer key appears to use phishing as the broader malicious-email class, so that assumption explains several mismatches.

I also treated malformed, gibberish-like, or badly normalized email content as enough reason to escalate a message to suspicious even when the sender infrastructure was clean. The answer key treats E-016 through E-018 as legitimate, indicating that I gave unusual formatting/content too much weight when there were no other meaningful malicious indicators.

These are calibration issues in my first-pass rubric, not random labeling errors. Keep them in mind when analyzing the differences and when we later refine the Guard agent's decision rules.

## First-pass human verdicts vs. answer-key expected verdicts

| Case | My first-pass verdict | Expected verdict | Match? | Main reason for mismatch |
| --- | --- | --- | --- | --- |
| E-011 | Suspicious | Phishing | ❌ | I treated malicious/pharmacy spam without a traditional phishing lure as suspicious rather than phishing. |
| E-012 | Suspicious | Phishing | ❌ | Same narrow interpretation of phishing vs. malicious spam. |
| E-013 | Suspicious | Phishing | ❌ | Malicious/new sender plus word-salad content looked malicious, but I stopped at suspicious because there was no obvious phishing action. |
| E-014 | Phishing | Phishing | ✅ | |
| E-015 | Phishing | Phishing | ✅ | |
| E-016 | Suspicious | Legitimate | ❌ | I over-weighted the malformed/gibberish-looking body despite the clean established internal sender and lack of malicious action. |
| E-017 | Suspicious | Legitimate | ❌ | I treated mangled mailing-list content and URL-like text as suspicious even though sender infrastructure was clean. |
| E-018 | Suspicious | Legitimate | ❌ | I over-weighted the unusual/no-subject body despite clean internal sender/context. |
| E-019 | Legitimate | Legitimate | ✅ | |
| E-020 | Legitimate | Legitimate | ✅ | |
| E-021 | Legitimate | Legitimate | ✅ | |
| E-022 | Legitimate | Legitimate | ✅ | |
| E-023 | Suspicious | Suspicious | ✅ | |
| E-024 | Suspicious | Suspicious | ✅ | |
| E-025 | Suspicious | Suspicious | ✅ | |
| E-026 | Suspicious | Suspicious | ✅ | |
| E-027 | Suspicious | Suspicious | ✅ | |
| E-028 | Suspicious | Suspicious | ✅ | |
| E-029 | Legitimate | Suspicious | ❌ | I gave the clean internal sender and prior-announcement context enough weight to accept it despite the unknown third-party signup link. |
| E-030 | Suspicious | Suspicious | ✅ | |

## First-pass result

13/20 expected verdicts matched = 65%

My distribution:

- Phishing: 2
- Suspicious: 13
- Legitimate: 5

Expected distribution:

- Phishing: 5
- Suspicious: 8
- Legitimate: 7

## Mismatch pattern

There are 7 mismatches, but they fall into three clear groups:

1. Under-classifying clear malicious email as phishing
   - E-011
   - E-012
   - E-013

   I used a narrower definition of phishing than the dataset.

2. Over-escalating strange-looking but benign email
   - E-016
   - E-017
   - E-018

   I treated malformed text/no subject/gibberish as stronger security indicators than the dataset does.

3. Under-escalating one borderline case
   - E-029

   I considered the trusted internal sender and business context sufficient for legitimate, while the expected Guard behavior is to remain suspicious because the third-party account-creation link is unknown and time-bound.

One notable result: I matched 7 of the 8 borderline cases E-023 through E-030. So most of the disagreement came from how I defined the boundaries of clear phishing and clear legitimate, rather than from recognizing genuinely ambiguous cases.

For now, treat this as a first-pass comparison only. Do not modify the agent, prompts, labels, or evaluation rules yet. I want to use these mismatches to determine which decision criteria need clarification before making changes.
