import pandas as pd
import logging

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "row_id",
    "year",
    "quarter",
    "period",
    "finalidad",
    "funcion",
    "finalidad_code",
    "funcion_code",
    "pagado",
    "credito_vigente",
]

def validate_spend_data(df: pd.DataFrame):
    """
    Run validations for processed spend dataset.
    """

    logger.info("---------- spend dataset validation ----------")

    validate_not_empty(df)
    validate_required_columns(df)
    validate_no_duplicate_rows(df)
    validate_no_null_ids(df)
    validate_numeric_columns(df)

    logger.info("---------- spend dataset validation passed ----------")

    return True

def validate_not_empty(df: pd.DataFrame):
    logger.info("(START) validating dataframe is not empty...")

    if df.empty:
        raise ValueError(
            "Dataset Vacio"
        )

    logger.info("(OK) dataframe is not empty")

def validate_required_columns(df: pd.DataFrame):
    logger.info("(START) validating required columns...")

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns {missing} not present"
        )

    logger.info("(OK) required columns validation passed")


def validate_no_duplicate_rows(df: pd.DataFrame):
    logger.info("(START) validating duplicate rows...")

    duplicated = df[
        df["row_id"].duplicated()
    ]

    if not duplicated.empty:
        raise ValueError(
            f"Rows duplicados detectados: {len(duplicated)}"
        )

    logger.info("(OK) duplicate rows validation passed")

def validate_no_null_ids(df: pd.DataFrame):
    logger.info("(START) validating null values in critical columns...")

    critical_columns = [
        "finalidad",
        "funcion",
        "row_id"
    ]

    for col in critical_columns:
        null_count = df[col].isna().sum()

        if null_count > 0:
            raise ValueError(
                f"Columna crítica '{col}' tiene {null_count} nulls"
            )

    logger.info("(OK) critical columns null validation passed")

def validate_numeric_columns(df: pd.DataFrame):
    logger.info("(START) validating numeric columns...")

    numeric_columns = [
        "pagado",
        "credito_vigente",
    ]

    for col in numeric_columns:
        negative_count = (
                df[col] < 0
        ).sum()

        if negative_count > 0:
            raise ValueError(
                f"Columna '{col}' tiene valores negativos"
            )

    logger.info("(OK) numeric columns validation passed")