import fs from "fs/promises"
import path from "path"

import { SpendRow } from "@/lib/lanus/types"

export async function getSpendData(
  year: number,
  quarter: number
): Promise<SpendRow[]> {

  const filePath = path.join(
    process.cwd(),
    "public",
    "data",
    "lanus",
    `spend_${year}_Q${quarter}.json`
  )

  const fileContents = await fs.readFile(
    filePath,
    "utf-8"
  )

  return JSON.parse(fileContents)
}
