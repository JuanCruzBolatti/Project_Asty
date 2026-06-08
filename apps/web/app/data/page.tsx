import { getSpendData } from "@/lib/lanus/data"

export default async function DataPage() {

  const rows = await getSpendData(
    2026,
    1
  )

  return (
    <main>
      <h1>Lanús Spending Dashboard</h1>

      <p>
        Total rows: {rows.length}
      </p>

      <hr />

      <h2>Functions</h2>

      <ul>
        {rows.map((row) => (
          <li key={row.row_id}>
            {row.funcion_name} — {row.pagado}
          </li>
        ))}
      </ul>
    </main>
  )
}
