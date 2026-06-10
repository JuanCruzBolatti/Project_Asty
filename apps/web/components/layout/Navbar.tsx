import Link from "next/link";

export function Navbar() {
    return (
        <nav className="fixed top-0 left-0 z-50 w-full px-5 py-4">

            <div className="flex items-end gap-2">

                <Link href="/" className="text-lg leading-none">
                    asty.
                </Link>

                <div
                    className="
                        mb-[3px]
                        h-[2px]
                        flex-1
                        bg-[#f2efff]

                        md:flex-none
                        md:w-32
                    "
                />

            </div>

        </nav>
    )
}