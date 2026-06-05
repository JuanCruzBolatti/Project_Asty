import json
from datetime import datetime
import logging
from pathlib import Path

import pandas as pd


logger = logging.getLogger(__name__)


def export_spend_json(
    df: pd.DataFrame,
    output_path: Path,
):
    """
    Export spend dataset to JSON.
    """

    logger.info("(START) exporting spend JSON...")

    records = df.to_dict(orient="records")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        f"(OK) spend JSON exported: {output_path}"
    )


def export_totals_json(
    df_totals: pd.DataFrame,
    output_path: Path,
):
    """
    Export totals dataset to JSON.
    """

    logger.info("(START) exporting totals JSON...")

    records = df_totals.to_dict(orient="records")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        f"(OK) totals JSON exported: {output_path}"
    )


def export_metadata_json(
    *,
    year: int,
    quarter: int,
    row_count: int,
    totals_count: int,
    output_path: Path,
):
    """
    Export metadata JSON.
    """

    logger.info("(START) exporting metadata JSON...")

    metadata = {
        "municipality": "lanus",
        "year": year,
        "quarter": quarter,
        "row_count": row_count,
        "totals_count": totals_count,
        "generated_at": (
            datetime.utcnow().isoformat()
        ),
        "currency": "ARS",
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        f"(OK) metadata JSON exported: {output_path}"
    )
