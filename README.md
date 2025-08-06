# lris2-drp

`lris2-drp` is a data reduction pipeline for LRIS2 flat-field images.  
It performs flat-field normalization, correction, slit tracing, and QA visualization using a Prefect-based workflow engine.

## Table of Contents

1. Installation  
2. Setting Up Your Package  
3. Running the DRP  
4. Output Files  
5. Configuration Tips

---

## 1. Installation

### Requirements

- Python 3.10 or higher  
- `pip`  
- `setuptools` >= 42  
- FITS images from LRIS2

### Clone the Repository

```bash
git clone https://github.com/caltech/lris2-drp.git
cd lris2-drp
```

### Create and Activate Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install the Package

```bash
pip install --upgrade pip setuptools wheel
pip install -e .[dev]
```

---

## 2. Setting Up Your Package

This package is built using [PEP 517/518](https://www.python.org/dev/peps/pep-0517/) with `pyproject.toml`.

To install only the core dependencies:

```bash
pip install -e .
```

Optional developer tools (like `black`, `flake8`, `pytest`) can be installed via:

```bash
pip install -e .[dev]
```

---

## 3. Running the DRP

To batch-process a folder of flat-field FITS files:

```python
from lris2_drp.flows import batch_process_all_flats

batch_process_all_flats(
    input_dir="/path/to/flats",
    output_dir="/path/to/results",
)
```

This will process up to 2 files in parallel (configurable) using Prefect’s `ConcurrentTaskRunner`.

Each file goes through:

- Normalization  
- Flat-field correction  
- Slit tracing  
- QA plot generation  
- FITS header augmentation

---

## 4. Output Files

For each input FITS file, the following will be written to the output directory:

```
<filename>/
├── flat_corrected.fits     # Flat-field corrected image
├── flat_norm_qa.png        # QA plot of normalized flat
└── slit_trace.txt          # Slit trace positions
```

The corrected FITS file includes a `FLATCOR` keyword in the header:

```
FLATCOR = 'True' / Flat-field correction applied
```

Additional keywords track reduction steps (optional to expand).

---

## 5. Configuration Tips

### Adjust Parallelism

To change the number of files processed in parallel, set `max_workers` in `ConcurrentTaskRunner`:

```python
@flow(task_runner=ConcurrentTaskRunner(max_workers=4))
def batch_process_all_flats(...):
```

### Customize Output Paths

Output filenames and directory structure can be customized in:

- `save_trace_solution()`
- `save_corrected_fits()`
- `generate_qa_plot()`

---
