export interface SpendRow {
  row_id: string
  year: number
  quarter: number
  period: string

  finalidad: string
  funcion: string

  finalidad_code: string
  funcion_code: string

  credito_vigente: number
  pagado: number
}
