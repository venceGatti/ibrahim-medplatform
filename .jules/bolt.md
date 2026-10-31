
## 2023-10-31 - Optimized Levenshtein Distance for HPO Lookup
**Learning:** The frontend used a dynamic programming matrix for `computeLevenshteinDistance` that was allocating an N x M matrix dynamically. This caused high memory churn and slow execution times when querying the colloquial HPO dictionary.
**Action:** Replaced the full matrix allocation with an optimized approach using two `Int32Array`s, which takes only O(min(N, M)) space and significantly speeds up the computation. This prevents main thread blocking and ensures real-time feedback when searching symptoms.
