import pdfplumber
from pathlib import Path
from typing import List
import pandas as pd
import logging
import re

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
                match = re.match(r'^(\d+\s*-\s[^0-9,]+)', line)
                if match:
                    current_finalidad = match.group(1).strip()
                    current_funcion = None  # Reset función
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

        # Si alguno de los primeros 4 falla, descarta
        if None in amounts[:4]:
            return None

        return {
            "finalidad": finalidad or "N/A",
            "funcion": funcion or "N/A",
            "credito_aprobado": amounts[0],
            "credito_vigente": amounts[1],
            "preventivo": amounts[2] if len(amounts) > 2 else None,
            "compromiso": amounts[3] if len(amounts) > 3 else None,
            "devengado": amounts[4] if len(amounts) > 4 else None,
            "pagado": amounts[5] if len(amounts) > 5 else None,
            "credito_disponible": amounts[6] if len(amounts) > 6 else None,
            "credito_vig_devengado": amounts[7] if len(amounts) > 7 else None,
            "devengado_no_pagado": amounts[8] if len(amounts) > 8 else None,
            "modificaciones": amounts[9] if len(amounts) > 9 else None,
        }

    def extract_spend_data(self) -> pd.DataFrame:
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

        logger.info(f"DataFrame extraído: {df.shape[0]} filas, {df.shape[1]} columnas")
        logger.debug(f"Primeras filas:\n{df.head()}")

        return df