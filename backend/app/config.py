"""Application configuration and environment loading.

The LangGraph nodes in ``app/nodes`` write files using paths relative to the
current working directory (``images/`` and ``<slug>.md``). To keep those files
in a predictable place without touching the graph code, we change the working
directory to ``backend/outputs`` at import time.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent

OUTPUTS_DIR = BACKEND_DIR / "outputs"
IMAGES_DIR = OUTPUTS_DIR / "images"
DB_PATH = BACKEND_DIR / "blog.db"

# Load the shared root .env first, then an optional backend-local override.
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

LLM_MODEL = os.environ.get("BLOG_LLM_MODEL", "gpt-5.4-mini")
OPENAI_IMAGE_MODEL = os.environ.get("BLOG_OPENAI_IMAGE_MODEL", "gpt-image-1-mini")

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# The LangGraph image node uses relative "images/" and the merge node writes
# "<slug>.md" relative to cwd. Anchor both inside backend/outputs.
os.chdir(OUTPUTS_DIR)
