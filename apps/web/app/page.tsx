import { getSpendData } from "@/lib/lanus/data"
import Link from "next/link"
import { linkPrimary } from "@/lib/utils/utils"
import { BackgroundGlow } from "@/components/ui/background-glow"
import { HOME_GLOWS } from "@/lib/theme/glows"

export default async function HomePage() {
    const data = await getSpendData(2026, 1)

    return (
        <main className="relative overflow-x-hidden">

            {/* Hero and Background Glow */}
            <BackgroundGlow glows={HOME_GLOWS} />

            {/* HERO */}
            <section className="relative z-20 mt-[35vh] md:mt-[25vh]">
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

            {/* PAGE TEST CONTENT */}
            <div className="relative z-10">

                <section className="min-h-screen mt-50">
                    <h1>Asty</h1>

                    <div className="text-green">
                        hola
                    </div>

                    <pre>
                        {JSON.stringify(data[0], null, 2)}
                    </pre>
                </section>

                <section className="min-h-screen">
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Doloribus, ipsa maxime quidem quos reiciendis rerum sunt ut velit veritatis vitae? A, alias consectetur, deleniti, dolor dolore doloremque eaque fugiat impedit laborum magnam nostrum nulla numquam quaerat quam qui quisquam repellat ullam. Aliquam amet autem commodi deleniti dignissimos eos eum excepturi, impedit libero nihil quidem totam! Illo nulla perspiciatis quas recusandae similique. A ab accusamus ad adipisci aspernatur aut beatae commodi culpa deserunt dicta ea eaque error est eum harum illo impedit magnam minus modi natus nemo neque, nesciunt nihil non possimus praesentium quos reiciendis sint unde voluptas. Amet at dignissimos eligendi excepturi, ipsa maiores mollitia nemo nostrum officiis omnis perferendis quas quasi repudiandae ut veritatis. Aut cupiditate ducimus eaque exercitationem sequi sit. Aperiam beatae culpa cum deserunt eos est harum, libero nulla omnis, optio quae qui, repellendus similique suscipit tempore ut voluptatem? Accusamus adipisci amet animi aperiam blanditiis consectetur consequatur delectus dolor dolores ea esse eveniet ex illo, itaque iure molestiae pariatur placeat quae quo quos reiciendis sequi soluta veritatis? A aliquam consequuntur culpa, dicta eaque eligendi ex laborum non numquam pariatur quis voluptas. Ab adipisci commodi cum dolor error est fugiat id in magni necessitatibus nesciunt obcaecati omnis optio placeat praesentium, quam quo quos repellendus unde veritatis? Doloribus maxime necessitatibus quasi. Corporis earum facere iusto maiores minima odio quod voluptatibus! A animi cumque dolorum necessitatibus odit, quae voluptates. A aspernatur assumenda at aut commodi consequuntur cumque dignissimos ducimus eos error esse et excepturi illum labore libero maiores minima modi necessitatibus obcaecati perspiciatis quia quibusdam quis quod repellat, reprehenderit similique tenetur ullam ut veritatis voluptatum! Architecto at cum cumque cupiditate, dolores, explicabo incidunt iste libero magnam necessitatibus nesciunt nobis quam soluta tempora voluptatum? Adipisci alias aspernatur consequuntur corporis cupiditate dolorem doloribus eius excepturi expedita fugit ipsa itaque molestiae necessitatibus nemo odit omnis, optio quae quasi qui quo rem repudiandae sunt tempore temporibus totam? Architecto aspernatur at corporis cum, delectus dignissimos ducimus eaque earum eos exercitationem explicabo facere illo illum iusto maiores maxime minus mollitia nam natus necessitatibus nesciunt nisi non nulla numquam odit porro quaerat quas quis quos repellat repudiandae saepe similique sit tenetur vitae voluptas voluptatibus? Ducimus itaque labore magni rem vel? Ad consequuntur culpa dicta eos ipsum itaque libero maxime nihil. Alias doloribus, eligendi enim eum quisquam repellendus rerum sint? Ab, aliquam aspernatur consectetur cupiditate debitis dolores esse incidunt ipsum laboriosam, numquam quam quasi repellat repellendus, voluptate voluptatem.
                </section>

            </div>

        </main>
    )
}