# Examples and Anti-Patterns

These examples explain the quality checks open-llm-wiki is designed to enforce.
They are written as reusable patterns, not as claims that every repository user
will see the same numbers or outcomes.

## 1. Missing Hard Numbers

Weak:

```text
The model achieves competitive results across benchmarks.
```

Better:

```text
Transformer base reports 27.3 BLEU on WMT 2014 English-German, compared with
26.1 for the prior recurrent baseline cited in the paper.
```

Lesson: source pages should capture the numbers that make a claim auditable.

## 2. Ambiguous Baselines

Weak:

```text
Method X improves accuracy by 7.2 points.
```

Better:

```text
Method X improves accuracy by 7.2 points over the no-retrieval baseline and
2.1 points over the retrieval baseline.
```

Lesson: every delta needs a named baseline.

## 3. Figure Over-Trust

Figures are useful for intuition, but tables and text usually carry the labels
needed for audit. If a number comes only from a figure, mark it as figure-derived
and avoid over-precise claims.

## 4. Self-Review Replacing QA

Weak:

```text
I wrote the page and checked it, so it is stable.
```

Better:

```text
The page remains in drafts until an independent QA report reaches overall >= 7.0
with verdict: PASS.
```

Lesson: self-check prepares the draft; independent QA gates publication.

## 5. Query Writeback Without Approval

Weak:

```text
The user asked a comparison question, so update three concept pages immediately.
```

Better:

```text
Answer first. Then propose the writeback target and summary. Write only after
the user approves or has pre-authorized automatic wiki growth.
```

Lesson: useful synthesis still needs clear file-side-effect boundaries.

## 6. Silent Contradiction Overwrite

Weak:

```text
Replace the old claim with the new paper's claim.
```

Better:

```text
Keep both claims, cite both sources, and mark the tension with
[CONTRADICTION YYYY-MM-DD].
```

Lesson: contradiction history is knowledge, not clutter.
