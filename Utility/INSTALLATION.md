# Installation Guide

## Local Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source .venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Google Colab
[Notebook - 1st cell] Add the below code snippet at the top of the notebook and run it once after uncommenting it. after run again comment it.
```python
# #====== COLAB SETUP - Library Installation ======
# #Uncomment ONLY when environment is not ready

# from google.colab import userdata

# user = userdata.get("GITHUB_USER") # add your github username in colab secrets
# token = userdata.get("GITHUB_TOKEN") # add your github token in colab secrets

# assert user is not None, "GITHUB_USER secret not found"
# assert token is not None, "GITHUB_TOKEN secret not found"

# # Use it if you need your branch's requirements.txt
# # !git clone -b vikash https://{user}:{token}@github.com/IIITH-2025-27/NLP_Project.git

# !git clone https://{user}:{token}@github.com/IIITH-2025-27/NLP_Project.git

# !pip install -r NLP_Project/requirements.txt

# #==================================================


```
## Set Dataset Path
[Notebook - 2nd cell] Add the below code in 3rd cell of the notebook.
```python
from pathlib import Path

# For Local
# PROJECT_ROOT = Path.cwd().parents[1] # Adjust according to the current file's location
# DATASET_PATH = PROJECT_ROOT/ "Datasets" / "FER_data.csv" #dataset path

# For Colab
DATASET_PATH = Path.cwd()/"FER_data.csv" #dataset path

#check
if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found at {DATASET_PATH}\n"
        "Please upload FER_data.csv into the Datasets folder."
    )
print("Dataset found successfully")
```

## Verify Installation
[Notebook - 3rd cell]
```python
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

> **Note:** For GPU support, ensure you have CUDA-compatible PyTorch installed.
