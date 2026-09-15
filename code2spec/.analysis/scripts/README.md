# Helper scripts used by the code2spec W1/W2 runs (hand-written by the coding agent)

- `w2_module_contract.md` — the document contract given to each W2 module agent (Design Card + FR structure, deep-link rules).
- `w2_post.py <module>…` — W2 post-processing: validate the two module docs, mark the module done, run `spec-update` for every module file, rebuild `modules/README.md` and `functional-requirements/index.md`. `--index-only` just rebuilds the indexes.
- `validate_w1.py` — W1 output checks (required files, H1 + Relevant-source-files block, no absolute source URLs).
- `gen_ch09.py` — regenerates `09-ipc-enum-catalog.md` from `.analysis/llm-extraction/*.json`.

Paths inside the scripts are absolute to /home/hwang/work/D/starfish_; adjust if the checkout moves.
