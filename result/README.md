Every subfolder here contains the output from the specific LLM (defined in `models.json`). Within each folder, at least one run exists with 4 files each.
A run output set consists of
- `res-ID.json` the full JSON output structure, as returned from OpenRouter
- `res-ID.txt` the plain output text
- `res-ID-review.json` the structured review in JSON format
- `res-ID-manual-review.json` the humen review in JSON format.

## review

Two types of reviews have been done. The first is the question to a critique-LLM. The ask is to rate then original answer on a scale from 0 to 10 regarding
- how much prose it contains
- how much symbolic notation it contains

```
Rate the following block regarding the following aspects:

 does it purely contain symblic, math notation (x/10)
 how much prose does it contain (y/10)

\`\`\`
"""
                        + prompt + """
\`\`\`

output in JSON ONLY, matching the following pattern:

{
    "symbolic_rating": ###,
    "prose_rating": ###
}
"""
```

The ask is not to rate the quality of the original answer in terms of correctness etc. 

The second review is the human review of the completeness and correctness of the answers regarding all three questions.

Both types are orthogonal. An answer might contain only symbolic notation, but might also be incorrect. 
A lengthy prose answer might contain little symbolic notation, but still be correct.

From research perspective, the ideal response is a combination of both where only symbolic notation is present and all three 
questions have been answered completely and correctly.

### LLM-based review of the results

All reviews have been done by `anthropic/claude-opus-4.5`.

- `symbolic_rating` 0=contains no symbolic notation, 9=only symbolic notation (good)
- `prose_rating` 0=contains no prose, 9=only prose (bad)

### Human review

- completeness/x for x=1,2,3 rates the completeness of the answer for question #x:
    - 0: the question was not answered or answered incorrectly
    - 5: the question was answered partially and correctly
    - 9: the question was answered completely and correctly

