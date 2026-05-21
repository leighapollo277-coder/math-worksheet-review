import os

# Base workspace directory (directory of this config file)
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Subdirectories
RAW_PAGES_DIR = os.path.join(WORKSPACE_DIR, "raw_pages")
RESIZED_DIR = os.path.join(WORKSPACE_DIR, "resized")
IMAGES_DIR = os.path.join(WORKSPACE_DIR, "images")
CACHE_DIR = os.path.join(WORKSPACE_DIR, "analysis_cache")

# File paths
REPORT_PATH = os.path.join(WORKSPACE_DIR, "analysis_report.json")
INDEX_PATH = os.path.join(WORKSPACE_DIR, "index.html")
PREVIEW_PATH = os.path.join(WORKSPACE_DIR, "preview.html")

def ensure_dirs():
    """Ensure all required directories exist."""
    for d in [RAW_PAGES_DIR, RESIZED_DIR, IMAGES_DIR, CACHE_DIR]:
        os.makedirs(d, exist_ok=True)
