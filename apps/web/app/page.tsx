import { getSpendData } from "@/lib/lanus/data"

export default async function HomePage() {

  const data = await getSpendData(
    2026,
    1
  )

  return (
    <main>
      <h1>Asty</h1>

      <pre>
        {JSON.stringify(data[0], null, 2)}
      </pre>
    </main>
  )
}