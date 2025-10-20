import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "X Algorithm Simulator | Grok-Powered Feed Analysis",
  description: "Discover how X's recommendation algorithm personalizes your feed. Analyze any X username to see topic recommendations powered by xAI's Grok models.",
  keywords: ["X", "Twitter", "Algorithm", "Grok", "AI", "Recommendations", "Feed Analysis"],
  authors: [{ name: "Apple Lamps", url: "https://x.com/lamps_apple" }],
  openGraph: {
    title: "X Algorithm Simulator",
    description: "Analyze X feeds with Grok AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
