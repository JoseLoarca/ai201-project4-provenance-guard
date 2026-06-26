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
