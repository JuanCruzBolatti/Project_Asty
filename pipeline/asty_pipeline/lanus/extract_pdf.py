import pdfplumber
from pathlib import Path
from typing import List
import pandas as pd
import logging
import re

from pandas import DataFrame

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extract spend execution data from Lanús PDFs (without table borders).
    """

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")

    def extract_text_lines(self) -> List[str]:
        """
        Extract all text lines from the PDF.
        """
        lines = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                logger.info(
                    f"PDF opened: {self.pdf_path} "
                    f"({len(pdf.pages)} pages)"
                )

                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_lines = text.split('\n')
                        logger.debug(
                            f"Page {page_num}: "
                            f"{len(page_lines)} lines extracted"
                        )
                        lines.extend(page_lines)
        except Exception as e:
            logger.error(f"(ERROR) failed to extract PDF text: {e}")
            raise

        return lines

    def parse_spend_rows(self, lines: List[str]) -> List[dict]:
        """
        Parse text lines and extract spend rows.
        """
        rows = []
        current_finalidad = None
        current_funcion = None
        last_row_hash = None

        for i, line in enumerate(lines):
            line = line.strip()

            if not line:
                continue

            # Skip headers and metadata
            if any(keyword in line for keyword in [
                "Jurisdicción",
                "Finalidad y Función",
                "Crédito Aprobado",
                "Crédito Vigente",
                "Fechas:",
                "Municipalidad de",
                "Desde",
                "Hasta",
                "Presupuesto:",
                "Página:",
                "Hora:",
                "ESTADO DE EJECUCION",
                "POR FINALIDAD Y FUNCIÓN",
                "Consolidado",
                "Todas",
                "TOTALES GENERALES"
            ]):
                continue

            # Skip lines starting with "TOTAL"
            if re.match(r'^TOTAL\s', line):
                continue

            # Strategy: detect patterns from line prefix
            # 1) Line starting with digit.digit.digit (3 levels)
            if re.match(r'^\d+\.\d+\.\d+\s*-', line):
                match = re.match(r'^(\d+\.\d+\.\d+\s*-\s[^0-9,]+)', line)
                if match:
                    current_funcion = match.group(1).strip()

                    if re.search(r'\d+[.,]\d+', line):
                        try:
                            row = self.parse_data_line(line, current_finalidad, current_funcion)
                            if row:
                                row_hash = (row['finalidad'], row['funcion'], row['pagado'])
                                if row_hash != last_row_hash:
                                    rows.append(row)
                                    last_row_hash = row_hash
                        except Exception as e:
                            pass
                continue

            # 2) Line starting with digit.digit (2 levels)
            if re.match(r'^\d+\.\d+\s*-', line):
                match = re.match(r'^(\d+\.\d+\s*-\s[^0-9,]+)', line)
                if match:
                    current_funcion = match.group(1).strip()

                    if re.search(r'\d+[.,]\d+', line):
                        try:
                            row = self.parse_data_line(line, current_finalidad, current_funcion)
                            if row:
                                row_hash = (row['finalidad'], row['funcion'], row['pagado'])
                                if row_hash != last_row_hash:
                                    rows.append(row)
                                    last_row_hash = row_hash
                        except Exception as e:
                            pass
                continue

            # 3) Line starting with digit (without dot) - finalidad
            if re.match(r'^\d+\s*-', line) and not re.match(r'^\d+\.', line):

                match = re.match(r'^(\d+\s*-\s[^0-9]+)', line)

                if match:
                    current_finalidad = match.group(1).strip()
                    current_funcion = None

                    if re.search(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', line):
                        try:
                            row = self.parse_data_line(
                                line,
                                current_finalidad,
                                current_finalidad
                            )

                            if row:
                                row_hash = (
                                    row['finalidad'],
                                    row['funcion'],
                                    row['pagado']
                                )

                                if row_hash != last_row_hash:
                                    rows.append(row)
                                    last_row_hash = row_hash

                        except Exception as e:
                            logger.debug(f"Error parseando finalidad: {e}")

                continue

            # 4) Line starting with "-" - raw data
            if line.startswith('-'):
                try:
                    funcion_to_use = current_funcion if current_funcion else current_finalidad
                    row = self.parse_data_line(line, current_finalidad, funcion_to_use)
                    if row:
                        row_hash = (row['finalidad'], row['funcion'], row['pagado'])
                        if row_hash != last_row_hash:
                            rows.append(row)
                            last_row_hash = row_hash
                except Exception as e:
                    pass
                continue

        return rows

    def parse_data_line(self, line: str, finalidad: str, funcion: str) -> dict | None:
        """
        Parse a data line and extract numeric amounts.
        """
        line = line.strip()

        # Remove leading "-" if present
        if line.startswith('-'):
            line = line[1:].strip()

        # Remove textual header
        line = re.sub(
            r'^\d+(?:\.\d+)*\s*-\s*[^0-9]+', '', line
        ).strip()

        # Extract all numeric values
        numbers = re.findall(r'-?[\d.,]+', line)

        if len(numbers) < 4:
            return None

        # Convert strings to floats
        def parse_number(s):
            if s.count('.') == 1 and s.count(',') > 0:
                s = s.replace(',', '')
            elif s.count(',') >= 1 and s.count('.') == 0:
                s = s.replace(',', '.')
            try:
                return float(s)
            except:
                return None

        amounts = [parse_number(n) for n in numbers]

        amounts = [a for a in amounts if a is not None]

        n = len(amounts)

        # Discard row if one of the first 4 values is invalid
        if None in amounts[:4]:
            return None

        row = {
            "finalidad": finalidad or "N/A",
            "funcion": funcion or "N/A",
            "credito_aprobado": None,
            "modificaciones": None,
            "credito_vigente": None,
            "preventivo": None,
            "compromiso": None,
            "devengado": None,
            "pagado": None,
            "credito_disponible": None,
            "credito_vig_devengado": None,
            "devengado_no_pagado": None,
        }

        # Full case with "modificaciones"
        if n == 10:
            (
                row["credito_aprobado"],
                row["modificaciones"],
                row["credito_vigente"],
                row["preventivo"],
                row["compromiso"],
                row["devengado"],
                row["pagado"],
                row["credito_disponible"],
                row["credito_vig_devengado"],
                row["devengado_no_pagado"],
            ) = amounts
        elif n == 9:
            (
                row["credito_aprobado"],
                row["credito_vigente"],
                row["preventivo"],
                row["compromiso"],
                row["devengado"],
                row["pagado"],
                row["credito_disponible"],
                row["credito_vig_devengado"],
                row["devengado_no_pagado"],
            ) = amounts
        elif n == 8:
            (
                row["credito_aprobado"],
                row["credito_vigente"],
                row["compromiso"],
                row["devengado"],
                row["pagado"],
                row["credito_disponible"],
                row["credito_vig_devengado"],
                row["devengado_no_pagado"],
            ) = amounts
        elif n == 4:
            # TODO: handle dynamic 4-column cases properly
            (
                row["credito_aprobado"],
                row["credito_vigente"],
                row["credito_disponible"],
                row["credito_vig_devengado"],
            ) = amounts
        else:
            logger.warning(
                f"Unexpected number of columns ({n}): {line}"
            )
            return None

        return row

    def extract_spend_data(self) -> tuple[DataFrame, DataFrame]:
        """
        Extract and parse spend execution data.
        """
        lines = self.extract_text_lines()

        if not lines:
            raise ValueError("No text found in PDF")

        rows = self.parse_spend_rows(lines)

        if not rows:
            raise ValueError(
                "No data rows found in PDF"
            )

        df = pd.DataFrame(rows)

        numeric_columns = [
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

        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df_totals = (
            df.groupby("finalidad")[numeric_columns]
            .sum().reset_index()
        )

        total_final = {"finalidad": "TOTAL GENERAL"}

        for col in numeric_columns:
            total_final[col] = df[col].sum()

        df_totals = pd.concat([df_totals, pd.DataFrame([total_final])], ignore_index=True)

        df_totals[numeric_columns] = (
            df_totals[numeric_columns].round(2)
        )

        logger.info(
            f"(OK) dataframe extracted successfully: "
            f"{df.shape[0]} rows, {df.shape[1]} columns"
        )

        logger.debug(f"Dataframe preview:\n{df.head()}")

        return df, df_totals