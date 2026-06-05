import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_pdf(
    url: str,
    output_path: Path,
    force: bool = False
) -> bool:
    """
    Download a PDF file using curl.

    Args:
        url: PDF URL
        output_path: Destination file path
        force: If True, force re-download

    Returns:
        True if downloaded
        False if already existed
    """

    if output_path.exists() and not force:

        logger.info(
            f"(OK) PDF already exists: "
            f"{output_path}"
        )

        return False

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        logger.info(
            f"(START) downloading PDF from: "
            f"{url}"
        )

        result = subprocess.run(
            [
                "curl",
                "-L",
                "--fail",
                "--silent",
                "--show-error",

                "-A",
                (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),

                "-H",
                "Referer: https://www.lanus.gob.ar/",

                "-o",
                str(output_path),

                url,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        file_size_mb = (
            output_path.stat().st_size
            / 1024
            / 1024
        )

        logger.info(
            f"(OK) PDF downloaded successfully: "
            f"{output_path} "
            f"({file_size_mb:.2f} MB)"
        )

        return True

    except subprocess.CalledProcessError as e:

        logger.error(
            f"(ERROR) curl download failed: "
            f"{e.stderr}"
        )

        raise