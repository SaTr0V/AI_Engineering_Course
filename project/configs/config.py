from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"

DIV2K_DIR = DATA_DIR / "div2k"
FFHQ_DIR = DATA_DIR / "ffhq"

# Hugging Face token (check your .env)
HF_TOKEN = os.getenv("HF_TOKEN")

# Datasets to load
DIV2K_DATASET = "yangtao9009/DIV2K"
FFHQ_DATASET = "bitmind/ffhq-256"

# Dataset parameters
PATCH_SIZE = 24
UPSCALE_FACTOR = 4
BATCH_SIZE = 16

# Reproducibility
SEED = 42