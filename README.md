# Design Creativity Bench

Code and data for
[**Design Creativity Bench: Measuring creativity in LLM-Generated UI**](https://arxiv.org/abs/2610.11539)

> Our work introduces Design Creativity Bench, a benchmark that evaluates diversity and
> appropriateness in UI designs. It measures distinctiveness among models on the same prompt
> (originality), how much a model's designs change between two prompts for the same UI goal in
> different product domains (creative range), and the share of a brief's acceptance criteria each
> design meets (appropriateness).
> — from the paper's abstract

## What is here
This repository includes scripts used to evaluate generated UI designs; data and script to reproduce embedding projection layers; data and script
for perturbation analysis; sample prompts and corresponding LLM generations.

The data is also on Hugging Face:

| Dataset | Contents |
|---|---|
| [`Kombai/design-creativity-bench`](https://huggingface.co/datasets/Kombai/design-creativity-bench) | Prompts, acceptance criteria, the 300 designs, reference scores, ladders |
| [`Kombai/design-creativity-bench-features`](https://huggingface.co/datasets/Kombai/design-creativity-bench-features) | Prepared features of those designs: elements, segment sizes, Gemini and UIClip vectors, colour palette |
| [`Kombai/design-creativity-bench-projection`](https://huggingface.co/datasets/Kombai/design-creativity-bench-projection) | Projection corpus and pair indexes |

| Path | Contents |
|---|---|
| `evaluate_model.py` | Score a model's 20 designs: originality, creative range and diversity |
| `score_two_html.py` | The pair similarity *S* for any two HTML pages |
| `build_reference.py` | Rebuild the panel's reference scores on the public subset from the shipped data (no API calls) |
| `dcbench/` | The pipeline: segment extraction, embeddings, colour system, pair score |
| `assets/` | `segment_centroid.npy`, the segment centroid used by the projection training |
| `data/prompts/` | The 20 public prompts: 10 tasks, each issued as two prompts that keep the goal and archetype but change the product domain |
| `data/criteria.jsonl` | The acceptance criteria of each public prompt |
| `data/samples/<model>/` | The 15 panel models' designs for the 20 public prompts |
| `data/features/<model>/` | Those designs, prepared: measured elements, segment sizes, Gemini and UIClip vectors, colour palette |
| `data/reference/paper_scores.csv` | The paper's published results, panel and human reference |
| `data/reference/subset_scores.csv` | The panel's originality, creative range and diversity on the 20 public prompts, which `evaluate_model.py` ranks a new model against |
| `ladders.py` | Score the 18 controlled ladders of the paper's robustness check |
| `data/ladders/` | The six ladder studies: anchor page, nine variants, and the edit specification of each variant |
| `projection/` | Rebuild the projection dataset from its corpus, train both projections |
| `data/projection/corpus/` | The 385 generated pages the projection dataset is built from, with their briefs and specs |
| `data/projection/original/` | The pair indexes of the dataset the projections were trained on |
| `generation/` | What the panel models were sent: system prompt, user-prompt wrapper, tool schemas, follow-up messages and per-model settings |


### The public subset

| Task | Archetype | Prompts |
|---|---|---|
| 1 | Form flow | `task1_1`, `task1_2` |
| 2 | Detail view | `task2_1`, `task2_2` |
| 3 | Form flow | `task3_1`, `task3_2` |
| 4 | Form flow | `task4_1`, `task4_2` |
| 5 | Landing page | `task5_1`, `task5_2` |
| 6 | Landing page | `task6_1`, `task6_2` |
| 7 | Landing page | `task7_1`, `task7_2` |
| 8 | Landing page | `task8_1`, `task8_2` |
| 9 | Landing page | `task9_1`, `task9_2` |
| 10 | Table workspace | `task10_1`, `task10_2` |

## Setup

```bash
uv sync                              # or: pip install -e .
uv run playwright install chromium
export OPENAI_API_KEY=...            # colour palette (gpt-5.6-luna)
export GEMINI_API_KEY=...            # gemini-embedding-2; or set GOOGLE_GENAI_USE_VERTEXAI=true with
                                     # GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION for Vertex AI
```

UIClip runs in-process on CPU or GPU (the weights download from Hugging Face on first use). A
server with the same `/embed` contract can be used instead with `--uiclip-endpoint`.

## Evaluate a model

Generate one design per public prompt and save each as `<prompt id>.html`:

```
outputs/my-model/
  task1_1.html  task1_2.html  task2_1.html  task2_2.html  ...  task10_1.html  task10_2.html
```

Each file should be one complete, self-contained desktop page (1280px wide) for its prompt. Then:

```bash
uv run python evaluate_model.py outputs/my-model --lab "My Lab"
```

`--lab` names the model's lab: panel models from the same lab are left out of its originality
pairs, as in the paper. The run prints originality, creative range and diversity, and ranks the
model among the panel on the same 20 prompts. Intermediates go to `runs/<model>/`, so an
interrupted run resumes.

Numbers from `evaluate_model.py` are on the 20 public prompts. They compare with
`subset_scores.csv`, not with the paper's results, which are measured on the benchmark's own
prompts.

## Score two pages

```bash
uv run python score_two_html.py a.html b.html
```

Prints *S* on 0-100 with its two parts (`ia_pct`, `cs_pct`) and the distinctiveness 1 − *S*/100.

## Reproduce the projections

The two projections (Gemini and UIClip) are linear maps trained on pairs of element crops captured before
and after in-browser edits that should not change a design (nuisance) or should (structural)
(Appendix, "Projection dataset, training, and metrics"). Rebuild the dataset from the corpus, then
train:

```bash
# pairs, screenshots and embeddings -> data/projection/{gemini,uiclip}/
uv run python projection/build_pairs.py --encoder gemini     # gemini-embedding-2, about $11
uv run python projection/build_pairs.py --encoder uiclip     # UIClip, local (a GPU helps)

uv run python projection/train_projection.py --data data/projection/gemini \
    --out runs/projection.npz --seed 0 --max-invariant-drift 1.1
uv run python projection/train_projection.py --data data/projection/uiclip \
    --out runs/uiclip_projection.npz --seed 0 --max-invariant-drift 1.1
```

## Results

The paper's results (`data/reference/paper_scores.csv`):

| # | Model | Overall | Originality | Creative range | Appropriateness |
|---|---|---|---|---|---|
| 1 | GPT-6 Astra | 65.5 | 0.646 | 0.472 | 99.1% |
| 2 | GPT-6.1 Sol | 63.7 | 0.642 | 0.487 | 98.8% |
| 3 | Grok 4.7 | 62.2 | 0.643 | 0.603 | 97.8% |
| 4 | Gemini 3.8 Flash | 60.6 | 0.637 | 0.628 | 97.5% |
| 5 | Qwen3.8 Max | 58.1 | 0.623 | 0.617 | 97.6% |
| 6 | GPT-5.6 Sol | 51.3 | 0.587 | 0.504 | 98.2% |
| 7 | Claude Opus 5.5 | 51.0 | 0.557 | 0.574 | 99.2% |
| 8 | Claude Fable 5.1 | 48.6 | 0.558 | 0.589 | 98.5% |
| 9 | Muse Spark 1.3 | 47.2 | 0.568 | 0.565 | 97.8% |
| 10 | DeepSeek V4.1 Flash | 43.6 | 0.576 | 0.596 | 96.3% |
| 11 | Grok 4.6 | 43.4 | 0.591 | 0.625 | 95.5% |
| 12 | GLM-5.3 | 41.9 | 0.579 | 0.634 | 95.6% |
| 13 | Kimi K3 | 40.4 | 0.547 | 0.615 | 96.8% |
| 14 | GLM-5.3-Flash | 38.5 | 0.553 | 0.611 | 96.1% |
| 15 | MiniMax M3 | 34.0 | 0.587 | 0.602 | 93.4% |
| — | Human reference | 92.3 | 0.764 | 0.902 | 98.0% |

## Citation

```bibtex
@misc{rusia2026design,
  author    = {Rusia, Aman and Bhole, Abhijit and Gupta, Prashank and Dey, Dipanjan},
  title     = {Design Creativity Bench: Measuring creativity in LLM-Generated UI},
  year      = {2026},
  publisher = {arXiv},
  doi       = {10.48550/ARXIV.2610.11539},
  url       = {https://arxiv.org/abs/2610.11539}
}
```

## License

MIT; see [LICENSE](LICENSE).
