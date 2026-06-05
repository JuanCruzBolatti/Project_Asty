import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_pdf(
    url: str,
    output_path: Path,
    force: bool = False
) -> bool:
    """
    Download a PDF file from a URL.

    Args:
        url: PDF URL
        output_path: Destination file path
        force: If True, download even if file exists

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

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "application/pdf,"
            "application/octet-stream,"
            "*/*"
        ),
        "Accept-Language": (
            "en-US,en;q=0.9"
        ),
        "Referer": (
            "https://www.lanus.gob.ar/"
        ),
        "Connection": "keep-alive",
    }

    try:

        logger.info(
            f"(START) downloading PDF from: "
            f"{url}"
        )

        session = requests.Session()

        session.headers.update(headers)

        # Warm-up request
        logger.debug(
            "(START) performing warm-up request..."
        )

        warmup_response = session.get(
            "https://www.lanus.gob.ar/",
            timeout=30,
            allow_redirects=True,
        )

        warmup_response.raise_for_status()

        logger.debug(
            "(OK) warm-up request completed"
        )

        # Download PDF
        response = session.get(
            url,
            timeout=60,
            stream=True,
            allow_redirects=True,
        )

        response.raise_for_status()

        with open(output_path, "wb") as f:

            for chunk in response.iter_content(
                chunk_size=8192
            ):

                if chunk:
                    f.write(chunk)

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

    except Exception as e:

        logger.error(
            f"(ERROR) failed to download PDF "
            f"from {url}: {e}"
        )

        raise