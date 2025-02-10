import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import AnimatedTitle from "../components/AnimatedTitle";
import Footer from "../components/Footer";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SnakeBench",
  description: "SnakeBench is a platform for testing and comparing LLMs in a snake arena.",
  icons: {
    icon: '/favicon.ico',
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
        <AnimatedTitle />
        <nav className="flex justify-center items-center gap-4 pt-2 font-mono">
          <Link href="/" className="hover:text-gray-600 transition-colors">Home</Link>
          <span className="text-gray-400">•</span>
          <Link href="/match/ffa06a21-3ba4-429b-a544-6b7d60c533b8" className="hover:text-gray-600 transition-colors">Best Match</Link>
          <span className="text-gray-400">•</span>
          <Link href="/findings" className="hover:text-gray-600 transition-colors">Analysis</Link>
        </nav>
        {children}
        <Footer />
      </body>
    </html>
  );
}
