import { BackgroundGlow } from "@/components/ui/background-glow"
import { RECAP_GLOWS } from "@/lib/theme/glows"

export default function HomePage() {
    return (
        <main className="max-w-5xl mx-auto px-6 py-16">

            <BackgroundGlow glows={RECAP_GLOWS} />

            <section className="mb-20">
                <h1 className="text-5xl font-bold mb-6">
                    Asty
                </h1>

                <p className="text-xl max-w-2xl">
                    Explore how municipalities spend public money through
                    interactive recaps and open datasets.
                </p>
            </section>

            <section className="grid gap-6 md:grid-cols-2 mb-20">

                <div className="border rounded-xl p-8">
                    <h2 className="text-2xl font-semibold mb-4">
                        Recap
                    </h2>

                    <p className="mb-6">
                        Narrative summaries that explain where public money
                        was spent during each quarter.
                    </p>

                    <div className="text-sm text-gray-500">
                        Latest available
                    </div>

                    <div className="font-medium">
                        Lanús · Q1 2026
                    </div>
                </div>

                <div className="border rounded-xl p-8">
                    <h2 className="text-2xl font-semibold mb-4">
                        Data
                    </h2>

                    <p className="mb-6">
                        Access the underlying datasets, classifications,
                        and budget execution details.
                    </p>

                    <div className="text-sm text-gray-500">
                        Available records
                    </div>

                    <div className="font-medium">
                        26 spending functions
                    </div>
                </div>

            </section>

            <section className="border rounded-xl p-8">

                <div className="text-sm text-gray-500 mb-2">
                    Featured recap
                </div>

                <h2 className="text-3xl font-bold mb-4">
                    How Lanús spent public funds during Q1 2026
                </h2>

                <p className="mb-6 max-w-3xl">
                    During the first quarter of 2026, municipal spending
                    was concentrated in urban services, health, and
                    government administration. Explore the complete recap
                    to understand where resources were allocated.
                </p>

                <div className="text-sm text-gray-500">
                    Municipality: Lanús
                </div>

            </section>

            {/* PAGE TEST CONTENT */}

            <section className="min-h-screen mt-50">
                <h1>Data</h1>

                <div className="text-green">
                    hola
                </div>

            </section>


        </main>
    )
}