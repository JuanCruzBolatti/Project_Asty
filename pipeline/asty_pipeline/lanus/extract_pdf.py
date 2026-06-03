import pdfplumber
from pathlib import Path
from typing import List
import pandas as pd
import logging
import re

from pandas import DataFrame

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extrae datos de ejecución de gastos de Lanús (sin bordes de tabla)."""

    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF no encontrado: {self.pdf_path}")

    def extract_text_lines(self) -> List[str]:
        """Extrae todas las líneas de texto del PDF."""
        lines = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                logger.info(f"PDF abierto: {self.pdf_path} ({len(pdf.pages)} páginas)")

                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_lines = text.split('\n')
                        logger.debug(f"  Página {page_num}: {len(page_lines)} líneas")
                        lines.extend(page_lines)
        except Exception as e:
            logger.error(f"Error extrayendo PDF: {e}")
            raise

        return lines

    def parse_spend_rows(self, lines: List[str]) -> List[dict]:
        """
        Parsea líneas de texto y extrae filas de gasto.
        """
        rows = []
        current_finalidad = None
        current_funcion = None
        last_row_hash = None

        for i, line in enumerate(lines):
            line = line.strip()

            if not line:
                continue

            # SKIP: cabeceras y metadata
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

            # SKIP: líneas que empiezan con "TOTAL"
            if re.match(r'^TOTAL\s', line):
                continue

            # Estrategia: detectar por patrón del inicio
            # 1) Línea que empieza con dígito.dígito.dígito (3 niveles) - función de 3 niveles
            if re.match(r'^\d+\.\d+\.\d+\s*-', line):
                match = re.match(r'^(\d+\.\d+\.\d+\s*-\s[^0-9,]+)', line)
                if match:
                    current_funcion = match.group(1).strip()

                    # Si tiene números al lado, parsear
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

            # 2) Línea que empieza con dígito.dígito (2 niveles) - función de 2 niveles
            if re.match(r'^\d+\.\d+\s*-', line):
                match = re.match(r'^(\d+\.\d+\s*-\s[^0-9,]+)', line)
                if match:
                    current_funcion = match.group(1).strip()

                    # Si tiene números al lado, parsear
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

            # 3) Línea que empieza con dígito (sin punto) - finalidad
            if re.match(r'^\d+\s*-', line) and not re.match(r'^\d+\.', line):

                match = re.match(r'^(\d+\s*-\s[^0-9]+)', line)

                if match:
                    current_finalidad = match.group(1).strip()
                    current_funcion = None

                    # IMPORTANTE:
                    # si la línea también tiene montos, parsearla
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

            # 4) Línea que empieza con "-" - datos puros
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
        Parsea una línea de datos e intenta extraer los montos.
        """
        line = line.strip()

        # Remover el "-" inicial si existe
        if line.startswith('-'):
            line = line[1:].strip()

        # ELIMINAR encabezado textual
        line = re.sub(
            r'^\d+(?:\.\d+)*\s*-\s*[^0-9]+', '', line
        ).strip()

        # Extraer todos los números (con coma o punto)
        numbers = re.findall(r'-?[\d.,]+', line)

        if len(numbers) < 4:  # Reducido de 8 a 4 porque algunos datos tienen menos columnas
            return None

        # Convertir strings a floats
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

        # Si alguno de los primeros 4 falla, descarta
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

        # Caso completo con "modificaciones"
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
            # TODO: Este hay que hacer algo porque no son siempre las mismas 4
            (
                row["credito_aprobado"],
                row["credito_vigente"],
                row["credito_disponible"],
                row["credito_vig_devengado"],
            ) = amounts
        else:
            logger.warning(f"Cantidad inesperada de columnas ({n}): {line}")
            return None

        return row

    def extract_spend_data(self) -> tuple[DataFrame, DataFrame]:
        """
        Extrae y parsea datos de ejecución de gastos.
        """
        lines = self.extract_text_lines()

        if not lines:
            raise ValueError("No se encontró texto en el PDF")

        rows = self.parse_spend_rows(lines)

        if not rows:
            raise ValueError("No se encontraron filas de datos en el PDF")

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

        logger.info(f"DataFrame extraído: {df.shape[0]} filas, {df.shape[1]} columnas")
        logger.debug(f"Primeras filas:\n{df.head()}")

        return df, df_totals