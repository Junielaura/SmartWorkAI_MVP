import type { Metadata } from "next"
import { Inter, Manrope } from "next/font/google"
import "./globals.css"
import AppShell from "@/components/app-shell"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
})

export const metadata: Metadata = {
  title: "SmartWork AI",
  description: "Plateforme intelligente d'automatisation documentaire et de production de livrables professionnels",
}

const themeInitScript = `
(() => {
  try {
    const stored = localStorage.getItem('sw-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = stored ? stored === 'dark' : prefersDark;
    document.documentElement.classList.toggle('dark', dark);
  } catch (_) {}
})();
`

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className={`${inter.variable} ${manrope.variable} min-h-screen bg-background text-text-primary antialiased`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  )
}
