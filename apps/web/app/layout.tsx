import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";

import "./globals.css";

import { Navbar } from "@/components/layout/Navbar"

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Asty",
  description: "Municipal spending explorer",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
    >
      <body className={`${jetbrainsMono.className}`}>
        <Navbar />

        {children}
      </body>
    </html>
  );
}
