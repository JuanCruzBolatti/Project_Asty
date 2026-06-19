import { getSpendData } from "@/lib/lanus/data"
import Link from "next/link"
import { linkPrimary } from "@/lib/utils/utils"
import { BackgroundGlow } from "@/components/ui/background-glow"
import { HOME_GLOWS } from "@/lib/theme/glows"

export default async function HomePage() {
    const data = await getSpendData(2026, 1)

    return (
        <main className="relative h-dvh overflow-x-hidden">

            {/* Hero and Background Glow */}
            <BackgroundGlow glows={HOME_GLOWS} />

            {/* HERO */}
            <section className="relative z-20 h-full flex items-center justify-center">
                <div className="flex flex-col justify-center items-center w-[90%] mx-auto md:w-fit">

                    <h1 className="w-full italic text-6xl md:text-8xl leading-none">lanús</h1>

                    <div className="w-full flex flex-row gap-2 items-start">
                        <Link href="/recap/2026/q1" className={`${linkPrimary} flex items-center justify-center w-fit px-4 py-2 mt-[1vw] h-[20vw] md:mt-3 md:h-[9rem] md:px-6`}>
                            V
                        </Link>

                        <h2 className="text-[25vw] leading-[0.9] font-extrabold md:text-[12rem]">RECAP</h2>
                    </div>

                    <div className="w-full flex flex-col gap-1 items-end">
                        <p className="w-full text-[4.6vw] italic leading-[0.9]">gastos de la muni pero con onda</p>
                        <Link href="/" className={`${linkPrimary} px-5 py-2 text-xl mr-1 mt-1 md:text-2xl md:px-7 md:py-3`}>ver recap --</Link>
                    </div>

                </div>
            </section>

            <Link href="" className={`${linkPrimary} absolute bottom-5 left-5 z-30 px-5 py-3`}>
                Data
            </Link>

        </main>
    )
}