import { SpendRow } from "./types"

export async function loadSpendData(): Promise<SpendRow[]> {
  const response = await fetch(
    "http://localhost:3000/data/lanus/spend_2026_Q1.json"
  )

  return response.json()
}