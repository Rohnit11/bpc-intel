import type { Metadata } from "next";
import { Geist, Geist_Mono, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import { NavBar } from "@/components/nav-bar";
import { SiteFooter } from "@/components/site-footer";
import { TooltipProvider } from "@/components/ui/tooltip";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const displaySerif = Source_Serif_4({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["600", "700"],
});

export const metadata: Metadata = {
  title: "bpc-intel | South Korea x India Beauty & Personal Care",
  description:
    "Market intelligence dashboard: South Korea x India Beauty & Personal Care, with full evidence provenance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${displaySerif.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[var(--page-plane)] text-[var(--text-primary)] font-sans">
        <TooltipProvider>
          <NavBar />
          <main className="flex-1 w-full max-w-6xl mx-auto px-4 sm:px-6 py-8">
            {children}
          </main>
          <SiteFooter />
        </TooltipProvider>
      </body>
    </html>
  );
}
