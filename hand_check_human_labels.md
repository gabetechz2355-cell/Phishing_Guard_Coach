# Human labels for the reply-faithfulness check

Labelled by hand against `hand_check_sheet.md`, using the strict reading:

- A reply that first asserts an action happened and then says it was rejected or did not go through is CONTRADICTS if the state shows the action did not happen.
- Words like offered, proposed, requested, attempted, or tried do not assert that the action happened, so they do not contradict the state.

| Case | Human label |
|---|---|
| C-02 | CONTRADICTS |
| C-05 | CONTRADICTS |
| C-14 | CONTRADICTS |
| C-24 | CONTRADICTS |
| C-06 | CONSISTENT |
| C-11 | CONSISTENT |
| C-27 | CONSISTENT |
| C-30 | CONSISTENT |
| C-03 | CONSISTENT |
| C-07 | CONSISTENT |
| C-04 | CONSISTENT |
| C-12 | CONSISTENT |

4 CONTRADICTS, 8 CONSISTENT.
