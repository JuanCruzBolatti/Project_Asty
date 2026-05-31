# Pipeline del proyecto

### Estructura:
```commandline
pyproject.toml           # deps python (pandas, pdfplumber/camelot, etc.)
README.md                # cómo correr el pipeline
asty_pipeline/
  __init__.py
  cli.py                 # CLI: python -m asty_pipeline.cli build-lanus ...

  lanus/
    manifest.yml         # lista controlada (MVP) de PDFs por periodo + URLs
    sources.py           # (opcional) discovery automático desde la web
    download.py          # descarga + cache de PDFs
    extract_pdf.py       # extracción de tablas desde PDF
    transform.py         # limpieza/normalización/mapping de categorías
    validate.py          # validaciones (schema, nulos, etc.)
    build.py             # orq:raw->interim->processed->public/data/lanus
    utils.py             # helpers (paths, logging, parse ARS, etc.)

data/                    # datos de trabajo del pipeline
  raw/
    lanus/
      2026_Q1/           # PDFs descargados (cache)
        ejec_gastos_finfun_Q1_2026.pdf

  interim/
    lanus/
      2026_Q1/       # extracción “sucia” para debug (csvs temporales, etc.)

  processed/
    lanus/
      spend.parquet      # dataset limpio para procesamiento eficiente
      spend.csv          # dataset limpio para inspección/descarga
      spend.json         # dataset limpio base para generar artefactos
```