// components/ui/background-glow.tsx

import { ReactNode } from "react";

type Glow = {
    className: string;
};

type BackgroundGlowProps = {
    glows: Glow[];
    children?: ReactNode;
};

export function BackgroundGlow({
                                   glows,
                                   children,
                               }: BackgroundGlowProps) {
    return (
        <div className="absolute inset-0 pointer-events-none">

            {glows.map((glow, index) => (
                <div
                    key={index}
                    className={`absolute rounded-full blur-[160px] ${glow.className}`}
                />
            ))}

            <div
                className="
                  absolute inset-0
                  bg-[url('/images/white-noise.png')]
                  opacity-60
                  mix-blend-soft-light
                "
            />

            {children}
        </div>
    );
}