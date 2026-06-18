# rapidrouge

> ⚠️⚠️⚠️ This repository was build with AI ⚠️⚠️⚠️

**A fast, pure-Python drop-in replacement for [`rouge-score`](https://pypi.org/project/rouge-score/).**

```bash
uv add rapidrouge          # pure-Python, ZERO runtime deps — installs anywhere
```

Optional extras: `rapidrouge[stemmer]` (nltk, for `use_stemmer=True`),
`rapidrouge[aggregate]` (numpy, for `BootstrapAggregator`), or `rapidrouge[full]`.

Same import, same results as `rouge_score` 0.1.2 — ROUGE-L's
LCS length is computed with the **Hyyrö bit-parallel algorithm** ([[1]](https://link.springer.com/content/pdf/10.1007/s00453-004-1108-z.pdf), [[2]](https://www.researchgate.net/profile/Jorma-Tarhio/publication/221314026_String_Matching_with_Stopper_Encoding_and_Code_Splitting/links/544ba6dc0cf2bcc9b1d6bdb5/String-Matching-with-Stopper-Encoding-and-Code-Splitting.pdf#page=211), [[3]](https://d1wqtxts1xzle7.cloudfront.net/39402556/psc02-libre.pdf?1445710147=&response-content-disposition=inline%3B+filename%3DA_Bit_Vector_Algorithm_for_Computing_Lev.pdf&Expires=1781780939&Signature=EUi-oiaBm3ekIV2LX8WIm-mhMh4lcqnq34FcWhGJ7tkWZ-dFYbEuC817~1DLghbEV6KlagJLi1kMUqCZVi0nPR6xzE31CC3QW1v4XwjZ0TMweD9rxbjr2HowUr1Nf6frF-XC6x2Wb674mXbA3FytUfJaTj6y4VQYFZpJgnk5xCOY73JLWmt~AWh8F5uI1K-4q~di-3KJlJEgcF2J03KfYUHuMWdbuc63euL2JglDF-96cxNaElgGiOVykbwL7Kjfbun9AO4J0zhaBhMARD3J4RXP-tNe-IzO70yTegAXdVTXOOvqwApbeMx2ZWYPb4rLuvWDrS2i~MsVIdvRwYXdNg__&Key-Pair-Id=APKAJLOHF5GGSLRBV4ZA)), so it's far faster
on long documents:

```python
from rapidrouge import rouge_scorer
scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=False)
scorer.score("the quick brown fox", "quick brown the fox")["rougeL"].fmeasure  # 0.75
```

## Benchmarks

ROUGE-L is where the bit-parallel kernel pays off, and the win **grows with document length**. From ~10× on a sentence to **~900× on a 35k-token document** (115 ms vs ~104 s), with results identical to `rouge_score`:

![rougeL speedup vs document length](docs/speedup_vs_length.png)

It's a memory win too: the reference fills an O(n·m) DP table (~9.8 GB at 35k tokens), while rapidrouge's LCS is O(n). `rouge1`/
`rouge2` (n-gram counting) and `rougeLsum` (still a DP table) match the reference in both correctness *and* speed (~1×), as expected — only ROUGE-L rides the Hyyrö kernel. 


## License

Apache-2.0. Portions derived from `rouge_score` (Apache-2.0); see `NOTICE`.
