import logging

from pathlib import Path
import yaml


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


# Define project paths
PIPELINE_DIR = Path(__file__).parent.parent.parent

DATA_DIR = PIPELINE_DIR / "data"

RAW_DIR = DATA_DIR / "raw" / "lanus"

INTERIM_DIR = DATA_DIR / "interim" / "lanus"

PROCESSED_DIR = DATA_DIR / "processed" / "lanus"

WEB_DATA_DIR = (
    PIPELINE_DIR.parent
    / "apps"
    / "web"
    / "public"
    / "data"
    / "lanus"
)

MANIFEST_PATH = (
    PIPELINE_DIR
    / "asty_pipeline"
    / "lanus"
    / "manifest.yml"
)


def ensure_dirs():

    logger.info("(START) ensuring pipeline directories...")

    for d in [
        RAW_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        WEB_DATA_DIR
    ]:
        d.mkdir(
            parents=True,
            exist_ok=True
        )

    logger.info("(OK) pipeline directories ensured")


def load_manifest() -> dict:

    logger.info("(START) loading manifest...")

    with open(MANIFEST_PATH, "r") as f:
        manifest = yaml.safe_load(f)

    logger.info("(OK) manifest loaded")

    return manifest
