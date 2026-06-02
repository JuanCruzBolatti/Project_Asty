import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def download_pdf(url: str, output_path: Path, force: bool = False) -> bool:
    """
    Descarga un PDF desde una URL.

    Args:
        url: URL del PDF
        output_path: Dónde guardarlo
        force: Si True, descarga aunque ya exista

    Returns:
        True si se descargó, False si ya existía
    """
    if output_path.exists() and not force:
        logger.info(f"PDF ya existe: {output_path}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Descargando: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"✓ Descargado: {output_path} ({len(response.content) / 1024 / 1024:.2f} MB)")
        return True

    except Exception as e:
        logger.error(f"Error descargando {url}: {e}")
        raise