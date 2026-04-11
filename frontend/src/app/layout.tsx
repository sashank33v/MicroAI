import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "MicroAI | Master Craft Metallurgical Engine",
    description: "Advanced AI-powered metallurgical microstructure analysis platform",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <div className="flex bg-brand-dark min-h-screen">
                    <Sidebar />
                    <main className="flex-1 ml-64 p-8 min-h-screen">
                        {children}
                    </main>
                </div>
            </body>
        </html>
    );
}
