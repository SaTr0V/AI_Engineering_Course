# Project data

> This folder contains the project data.

The training set consists of 800 DIV2K images and 100 FFHQ images. 10 samples for both datasets are also provided here in `div2k_samples` and `ffhq_samples`.

## Raw datasets download

To download datasets, use following commands from the project's directory:

**If you use `uv`:**
```bash
uv run download-datasets
```

**Otherwise just run:**
```bash
python src/dataset/download.py
```

When `"All tasks finished"` message is shown, you may interrupt the process using `CTRL+C`.

