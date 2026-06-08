export function Navbar() {
    return (
        <nav className="fixed top-0 left-0 z-50 w-full p-6">

            <div className="relative w-full md:w-fit">

                <h1 className="text-2xl font-semibold tracking-tight">
                    Asty
                </h1>

                <div
                    className="
                        absolute -bottom-2 left-[20%]
                        h-px
                        w-60 md:w-8
                        bg-white
                      "
                />

            </div>

        </nav>
    )
}