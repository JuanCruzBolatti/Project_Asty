import sys
import logging
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import yaml
from asty_pipeline.lanus.extract_pdf import PDFExtractor
from asty_pipeline.lanus.download import download_pdf
from asty_pipeline.lanus.transform import transform_spend_data
from asty_pipeline.lanus.validate import validate_spend_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define project paths
PIPELINE_DIR = Path(__file__).parent.parent
DATA_DIR = PIPELINE_DIR / "data"

RAW_DIR = DATA_DIR / "raw" / "lanus"
INTERIM_DIR = DATA_DIR / "interim" / "lanus"
PROCESSED_DIR = DATA_DIR / "processed" / "lanus"
WEB_DATA_DIR = (
        Path(PIPELINE_DIR).parent
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
    """Create directories if they do not exist."""
    for d in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, WEB_DATA_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def load_manifest() -> dict:
    """Load PDF manifest."""
    with open(MANIFEST_PATH, 'r') as f:
        return yaml.safe_load(f)


def build_lanus(year: int, quarter: int, force_download: bool = False):
    """
    Build Lanús dataset.
    """
    ensure_dirs()

    logger.info(f"========== building Lanús dataset for {year} Q{quarter} ==========")

    # Load manifest
    manifest = load_manifest()

    # Find matching source entry
    source = None
    for s in manifest['sources']:
        if s['year'] == year and s['quarter'] == quarter:
            source = s
            break

    if not source:
        logger.error(f"No encontrado en manifest: {year} Q{quarter}")
        sys.exit(1)

    # Download PDF
    pdf_path = RAW_DIR / source['pdf_filename']
    download_pdf(source['pdf_url'], pdf_path, force=force_download)

    # Extract tables
    logger.info(
        f"(START) extracting data from "
        f"{source['pdf_filename']}..."
    )
    extractor = PDFExtractor(pdf_path)

    # Debug PDF loading
    logger.debug(f"PDF path: {pdf_path}")
    logger.debug(f"PDF exists: {pdf_path.exists()}")

    # Extraer líneas PRIMERO
    lines = extractor.extract_text_lines()
    logger.debug(
        f"Total extracted lines: {len(lines)}"
    )

    if len(lines) > 0:
        logger.debug(
            f"First line preview: {lines[0][:60]}"
        )
        logger.debug(
            f"Last line preview: {lines[-1][:60]}"
        )

    # Save extracted lines for debugging
    with open(INTERIM_DIR / "debug_all_lines.txt", "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            f.write(f"{i}: {repr(line)}\n")
    logger.debug(
        f"Debug lines saved to: "
        f"{INTERIM_DIR / 'debug_all_lines.txt'}"
    )

    # Parse extracted data
    df, df_totals = extractor.extract_spend_data()

    # Save interim datasets
    interim_csv = INTERIM_DIR / f"extracted_{year}_Q{quarter}.csv"
    totals_csv = INTERIM_DIR / f"totals_{year}_Q{quarter}.csv"
    df.to_csv(interim_csv, index=False)
    df_totals.to_csv(totals_csv, index=False)
    logger.info(
        f"(OK) interim CSV saved: {interim_csv}"
    )
    logger.info(
        f"(OK) totals CSV saved: {totals_csv}"
    )

    # Transform datasets
    df_processed = transform_spend_data(
        df, year=year, quarter=quarter
    )

    df_totals["year"] = year
    df_totals["quarter"] = quarter

    df_totals["period"] = (
            df_totals["year"].astype(str)
            + "_Q"
            + df_totals["quarter"].astype(str)
    )

    processed_csv = (PROCESSED_DIR / f"spend_{year}_Q{quarter}.csv")
    processed_parquet = (PROCESSED_DIR / f"spend_{year}_Q{quarter}.parquet")
    totals_processed_csv = (PROCESSED_DIR / f"totals_{year}_Q{quarter}.csv")
    totals_processed_parquet = (PROCESSED_DIR / f"totals_{year}_Q{quarter}.parquet")

    df_processed.to_csv(processed_csv, index=False)
    df_processed.to_parquet(processed_parquet, index=False)
    df_totals.to_csv(totals_processed_csv, index=False)
    df_totals.to_parquet(totals_processed_parquet, index=False)


    logger.info(
        f"(OK) processed CSV saved: {processed_csv}"
    )
    logger.info(
        f"(OK) processed parquet saved: "
        f"{processed_parquet}"
    )
    logger.info(
        f"(OK) processed totals CSV saved: "
        f"{totals_processed_csv}"
    )
    logger.info(
        f"(OK) processed totals parquet saved: "
        f"{totals_processed_parquet}"
    )

    # Validate datasets
    validate_spend_data(df_processed)

    logger.info("========== Build completado ==========")

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