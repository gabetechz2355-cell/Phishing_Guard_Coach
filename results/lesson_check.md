# Lesson judge vs hand labels, 10 reject cases

One judge call per lesson from results/lesson_check_inputs.md, inputs rebuilt from the mailbox, the answer key, and the pass1 replies; the judge saw only the email, the labeled red flags, the employee's reason, the role, the lesson, and the computed word count — no hand labels and no notes. Criteria order: FLAGS (names the labeled red flags), RULE (gives a usable rule), INVENTS_NOTHING, UNDER_120.

## Per case

| Case | Hand | Judge | Agreement |
|---|---|---|---|
| C-02 | FLAGS=NO RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 3/4 |
| C-05 | FLAGS=YES RULE=YES INVENTS_NOTHING=NO UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=NO UNDER_120=YES | 4/4 |
| C-06 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-09 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-12 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-14 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-24 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-26 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-28 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |
| C-29 | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | FLAGS=YES RULE=YES INVENTS_NOTHING=YES UNDER_120=YES | 4/4 |

## Agreement

- FLAGS (names the labeled red flags): 9 of 10
- RULE (gives a usable rule): 10 of 10
- INVENTS_NOTHING (invents nothing): 10 of 10
- UNDER_120 (120 words or fewer): 10 of 10
- **Overall: 39 of 40**

Of the two real failures in my hand labels, the judge caught one (C-05 invented detail) and missed one (C-02 missing red flag, where it matched "reply confirmation" to the reply-to flag by wording, not meaning). It raised no false alarms on the 38 boxes I marked YES. So it is reliable at passing good lessons and partly reliable at catching bad ones.

## Disagreements

### C-02, FLAGS (names the labeled red flags)

**Hand label:** NO — note: missing "reply-to differs from sender".

**Judge answer:** YES

**Judge reason:** The lesson names the lookalike sender domain, the bank-detail change request, and the reply-confirmation request, which covers all three labeled red flags. It gives a usable rule for AP: verify any bank change against records and use the vendor contact already on file. It does not invent facts; it only describes the visible sender and asks for confirmation, which are in the email, plus general caution. The word count is 84, so it is under 120.

## Notes

1. C-28 and C-29 are true-legitimate emails where the scripted employee rejected a cautious move, so Coach taught distrust of a real email. The lessons can still pass all four criteria; the criteria measure lesson quality, not verdict quality.
2. The judge does not see Guard's tool evidence, only the email, the labeled red flags, the reason, and the role. That matters for INVENTS_NOTHING: a lesson detail drawn from tool output (C-09's "link reputation unknown") is unverifiable from the judge's inputs. In this run the judge let it pass, matching the hand label, but a stricter judge could mark such a detail invented; only the hand labels had the tool evidence in view.
3. Some lessons put quotation marks around paraphrases rather than exact email text (C-05, C-24). The criteria judge grounding by meaning, so this is not an invention by itself, but it can read like a fabricated quote.
