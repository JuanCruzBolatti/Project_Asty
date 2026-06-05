import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_pdf(url: str, output_path: Path, force: bool = False) -> bool:
    """
    Download a PDF file from a URL.

    Args:
        url: PDF URL
        output_path: Destination file path
        force: If True, download even if the file already exists

    Returns:
        True if the file was downloaded, False if it already existed
    """
    if output_path.exists() and not force:
        logger.info(f"(OK) PDF already exists: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"(START) downloading PDF from URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(
            f"(OK) PDF downloaded successfully: {output_path} "
            f"({len(response.content) / 1024 / 1024:.2f} MB)"
        )
        return True

    except Exception as e:
        logger.error(f"(ERROR) failed to download PDF from {url}: {e}")
        raise