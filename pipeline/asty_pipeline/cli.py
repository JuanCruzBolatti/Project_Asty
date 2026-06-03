import sys
import logging
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import yaml
from asty_pipeline.lanus.extract_pdf import PDFExtractor
from asty_pipeline.lanus.download import download_pdf

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
PIPELINE_DIR = Path(__file__).parent.parent
DATA_DIR = PIPELINE_DIR / "data"
RAW_DIR = DATA_DIR / "raw" / "lanus"
INTERIM_DIR = DATA_DIR / "interim" / "lanus"
PROCESSED_DIR = DATA_DIR / "processed" / "lanus"
WEB_DATA_DIR = Path(PIPELINE_DIR).parent / "apps" / "web" / "public" / "data" / "lanus"
MANIFEST_PATH = PIPELINE_DIR / "asty_pipeline" / "lanus" / "manifest.yml"


def ensure_dirs():
    """Crea directorios si no existen."""
    for d in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, WEB_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    """Carga el manifest de PDFs."""
    with open(MANIFEST_PATH, 'r') as f:
        return yaml.safe_load(f)


def build_lanus(year: int, quarter: int, force_download: bool = False):
    """
    Build dataset para Lanús.
    """
    ensure_dirs()

    logger.info(f"Iniciando build: Lanús {year} Q{quarter}")

    # Cargar manifest
    manifest = load_manifest()

    # Buscar la entrada correspondiente
    source = None
    for s in manifest['sources']:
        if s['year'] == year and s['quarter'] == quarter:
            source = s
            break

    if not source:
        logger.error(f"No encontrado en manifest: {year} Q{quarter}")
        sys.exit(1)

    # Descargar PDF
    pdf_path = RAW_DIR / source['pdf_filename']
    download_pdf(source['pdf_url'], pdf_path, force=force_download)

    # Extraer tablas
    logger.info(f"Extrayendo datos de {source['pdf_filename']}...")
    extractor = PDFExtractor(pdf_path)

    # DEBUG: verificar que el PDF se cargó
    print(f"DEBUG: PDF path: {pdf_path}")
    print(f"DEBUG: PDF existe: {pdf_path.exists()}")

    # Extraer líneas PRIMERO
    lines = extractor.extract_text_lines()
    print(f"DEBUG: Total líneas extraídas: {len(lines)}")

    if len(lines) > 0:
        print(f"DEBUG: Primera línea: {lines[0][:60]}")
        print(f"DEBUG: Última línea: {lines[-1][:60]}")

    # Guardar debug de líneas
    with open(INTERIM_DIR / "debug_all_lines.txt", "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            f.write(f"{i}: {repr(line)}\n")
    print(f"Guardado debug: {INTERIM_DIR / 'debug_all_lines.txt'}")

    # Ahora parsear
    df, df_totals = extractor.extract_spend_data()

    # Guardar interim (para debug)
    interim_csv = INTERIM_DIR / f"extracted_{year}_Q{quarter}.csv"
    totals_csv = INTERIM_DIR / f"totals_{year}_Q{quarter}.csv"
    df.to_csv(interim_csv, index=False)
    df_totals.to_csv(totals_csv, index=False)
    logger.info(f"Interim CSV guardado: {interim_csv}")
    logger.info(f"Totales CSV guardado: {totals_csv}")

    logger.info("✓ Build completado")

def main():
    """Entry point del CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Asty Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Subcommand: build-lanus
    build_parser = subparsers.add_parser("build-lanus", help="Build dataset Lanús")
    build_parser.add_argument("--year", type=int, required=True, help="Año (ej: 2026)")
    build_parser.add_argument("--quarter", type=int, required=True, choices=[1, 2, 3, 4], help="Trimestre (1-4)")
    build_parser.add_argument("--force-download", action="store_true", help="Fuerza descarga del PDF")

    args = parser.parse_args()

    if args.command == "build-lanus":
        build_lanus(args.year, args.quarter, args.force_download)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()