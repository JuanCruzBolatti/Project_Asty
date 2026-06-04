
import pandas as pd


NUMERIC_COLUMNS = [
    "credito_aprobado",
    "modificaciones",
    "credito_vigente",
    "preventivo",
    "compromiso",
    "devengado",
    "pagado",
    "credito_disponible",
    "credito_vig_devengado",
    "devengado_no_pagado",
]


def transform_spend_data(
    df: pd.DataFrame,
    year: int,
    quarter: int
) -> pd.DataFrame:
    """
    Limpia y normaliza dataset de gastos.
    """

    df = df.copy()

    # Metadata temporal
    df["year"] = year
    df["quarter"] = quarter

    # Separar códigos y nombres
    df["finalidad_code"] = (
        df["finalidad"]
        .str.extract(r'^(\d+)')[0]
    )

    df["finalidad_name"] = (
        df["finalidad"]
        .str.replace(r'^\d+\s*-\s*', '', regex=True)
        .str.strip()
    )

    df["funcion_code"] = (
        df["funcion"]
        .str.extract(r'^([\d\.]+)')[0]
    )

    df["funcion_name"] = (
        df["funcion"]
        .str.replace(r'^[\d\.]+\s*-\s*', '', regex=True)
        .str.strip()
    )

    # Convertir columnas numéricas
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).round(2)

    # IDs útiles
    df["period"] = (
        df["year"].astype(str)
        + "_Q"
        + df["quarter"].astype(str)
    )

    df["row_id"] = (
        df["period"]
        + "_"
        + df["funcion_code"].fillna("unknown")
    )

    # Orden de columnas
    ordered_columns = [
        "row_id",
        "year",
        "quarter",
        "period",

        "finalidad_code",
        "finalidad_name",

        "funcion_code",
        "funcion_name",

        "finalidad",
        "funcion",

        *NUMERIC_COLUMNS
    ]

    existing_columns = [
        c for c in ordered_columns
        if c in df.columns
    ]

    df = df[existing_columns]

    return df