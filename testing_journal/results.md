**2026-06-26 - Initial Run**

These results are from my manual testing of the LLM-based classification function.

| # | Content              | Ground Truth | Score | Result           |
|---|----------------------|--------------|-------|------------------|
| 1 | Sonnet               | AI (GPT-5.5) | 0.8   | ✅ Correct        |
| 2 | Cat story            | AI (GPT-5.5) | 0.2   | ❌ False negative |
| 3 | Gym blog post        | AI (GPT-5.5) | 0.7   | ✅ Correct        |
| 4 | "Bella Notte" poem   | Human        | 0.7   | ❌ False positive |
| 5 | Perimenopause story  | Human        | 0.2   | ✅ Correct        |
| 6 | Masters lifters post | Human        | 0.8   | ❌ False positive |

**2026-06-27 - LLM + Stylometrics**

These results are from my manual testing of the stylometrics heuristics evaluation. I'm showing the stylometrics results
next to the LLM-based evaluation results to compare them and see how/where both signals agree or disagree.

I used the same examples I used in my initial run, and this time I added two examples provided by CodePath.

| # | Content           | Ground Truth             | LLM   | Stylometrics | Both correct? |
|---|-------------------|--------------------------|-------|--------------|---------------|
| 1 | Sonnet            | AI (GPT-5.5)             | 0.8 ✅ | 0.824 ✅      | ✅             |
| 2 | Cat story         | AI (GPT-5.5)             | 0.2 ❌ | 0.731 ✅      | ⚠️            |
| 3 | Gym blog          | AI (GPT-5.5)             | 0.7 ✅ | 0.488 ⚠️     | ⚠️            |
| 4 | AI about AI       | AI (CodePath example)    | 0.8 ✅ | 0.665 ✅      | ✅             |
| 5 | Bella Notte poem  | Human                    | 0.7 ❌ | 0.697 ❌      | ❌             |
| 6 | Perimenopause     | Human                    | 0.2 ✅ | 0.158 ✅      | ✅             |
| 7 | Masters lifters   | Human                    | 0.8 ❌ | 0.666 ❌      | ❌             |
| 8 | Restaurant review | Human (CodePath example) | 0.2 ✅ | 0.200 ✅      | ✅             |

**2026-06-28 - Full pipeline**

Results from running the full pipeline (getting a final score that generates a label).

| # | Content           | Ground Truth | Label        | Correct? |
|---|-------------------|--------------|--------------|----------|
| 1 | Sonnet            | AI           | likely AI    | ✅        |
| 2 | Cat story         | AI           | uncertain    | ⚠️       |
| 3 | Gym blog          | AI           | uncertain    | ⚠️       |
| 4 | AI about AI       | AI           | likely AI    | ✅        |
| 5 | Bella Notte poem  | Human        | uncertain    | ✅        |
| 6 | Masters lifters   | Human        | likely AI    | ❌        |
| 7 | Perimenopause     | Human        | likely human | ✅        |
| 8 | Restaurant review | Human        | likely human | ✅        |
