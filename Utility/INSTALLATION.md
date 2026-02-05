# Installation Guide

## Local Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Google Colab
Add the below code snippet at the top of the notebook and run it once after uncommenting it. after run again comment it.
```python
# Clone repo
# # ====== COLAB SETUP ======
# #Uncomment this cell ONLY when environment is not ready

# !git clone https://github.com/IIITH-2025-27/NLP_Project.git
# %cd NLP_Project
# !pip install -r requirements.txt

# # ========================

```

## Verify Installation

```python
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

> **Note:** For GPU support, ensure you have CUDA-compatible PyTorch installed.
