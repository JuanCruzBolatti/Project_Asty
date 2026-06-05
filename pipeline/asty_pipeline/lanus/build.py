import sys
import logging

from asty_pipeline.lanus.download import download_pdf
from asty_pipeline.lanus.extract_pdf import PDFExtractor
from asty_pipeline.lanus.transform import transform_spend_data
from asty_pipeline.lanus.validate import validate_spend_data
from asty_pipeline.lanus.export import ( export_spend_json, export_totals_json, export_metadata_json, )

from asty_pipeline.lanus.utils import (
    logger,
    ensure_dirs,
    load_manifest,
    RAW_DIR,
    INTERIM_DIR,
    PROCESSED_DIR,
    WEB_DATA_DIR,
)


def build_lanus(
    year: int,
    quarter: int,
    force_download: bool = False
):

    ensure_dirs()

    logger.info(
        f"========== building Lanús dataset "
        f"for {year} Q{quarter} =========="
    )

    manifest = load_manifest()

    source = None

    for s in manifest["sources"]:

        if (
            s["year"] == year
            and s["quarter"] == quarter
        ):
            source = s
            break

    if not source:

        logger.error(
            f"Manifest entry not found "
            f"for {year} Q{quarter}"
        )

        sys.exit(1)

    # Download PDF
    pdf_path = RAW_DIR / source["pdf_filename"]

    download_pdf(
        source["pdf_url"],
        pdf_path,
        force=force_download
    )

    # Extract
    extractor = PDFExtractor(pdf_path)

    lines = extractor.extract_text_lines()

    # Save debug lines
    debug_path = (
        INTERIM_DIR / "debug_all_lines.txt"
    )

    with open(
        debug_path,
        "w",
        encoding="utf-8"
    ) as f:

        for i, line in enumerate(lines):
            f.write(f"{i}: {repr(line)}\n")

    logger.debug(
        f"Debug lines saved to: {debug_path}"
    )

    # Parse
    df, df_totals = (
        extractor.extract_spend_data()
    )

    # Save interim
    interim_csv = (
        INTERIM_DIR
        / f"extracted_{year}_Q{quarter}.csv"
    )

    totals_csv = (
        INTERIM_DIR
        / f"totals_{year}_Q{quarter}.csv"
    )

    df.to_csv(interim_csv, index=False)

    df_totals.to_csv(
        totals_csv,
        index=False
    )

    logger.info(
        f"(OK) interim CSV saved: {interim_csv}"
    )

    logger.info(
        f"(OK) totals CSV saved: {totals_csv}"
    )

    # Transform
    df_processed = transform_spend_data(
        df,
        year=year,
        quarter=quarter
    )

    # Totals metadata
    df_totals["year"] = year
    df_totals["quarter"] = quarter

    df_totals["period"] = (
        df_totals["year"].astype(str)
        + "_Q"
        + df_totals["quarter"].astype(str)
    )

    # Validate
    validate_spend_data(df_processed)

    # Save processed
    processed_csv = (
        PROCESSED_DIR
        / f"spend_{year}_Q{quarter}.csv"
    )

    processed_parquet = (
        PROCESSED_DIR
        / f"spend_{year}_Q{quarter}.parquet"
    )

    totals_processed_csv = (
        PROCESSED_DIR
        / f"totals_{year}_Q{quarter}.csv"
    )

    totals_processed_parquet = (
        PROCESSED_DIR
        / f"totals_{year}_Q{quarter}.parquet"
    )

    df_processed.to_csv(
        processed_csv,
        index=False
    )

    df_processed.to_parquet(
        processed_parquet,
        index=False
    )

    df_totals.to_csv(
        totals_processed_csv,
        index=False
    )

    df_totals.to_parquet(
        totals_processed_parquet,
        index=False
    )

    logger.info(
        f"(OK) processed CSV saved: "
        f"{processed_csv}"
    )

    logger.info(
        f"(OK) processed parquet saved: "
        f"{processed_parquet}"
    )

    logger.info(
        f"(OK) totals CSV saved: "
        f"{totals_processed_csv}"
    )

    logger.info(
        f"(OK) totals parquet saved: "
        f"{totals_processed_parquet}"
    )

    # Export web artifacts
    spend_json_path = (
            WEB_DATA_DIR
            / f"spend_{year}_Q{quarter}.json"
    )

    totals_json_path = (
            WEB_DATA_DIR
            / f"totals_{year}_Q{quarter}.json"
    )

    meta_json_path = (
            WEB_DATA_DIR
            / f"meta_{year}_Q{quarter}.json"
    )

    export_spend_json(
        df_processed,
        spend_json_path
    )

    export_totals_json(
        df_totals,
        totals_json_path
    )

    export_metadata_json(
        year=year,
        quarter=quarter,
        row_count=len(df_processed),
        totals_count=len(df_totals),
        output_path=meta_json_path,
    )

    logger.info(
        "========== build completed =========="
    )
