"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Microscope,
    FileText,
    GitCompare,
    Settings,
    LogOut,
    Hexagon
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const navItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/" },
    { icon: Microscope, label: "Analyze", href: "/analyze" },
    { icon: FileText, label: "Reports", href: "/reports" },
    { icon: GitCompare, label: "Compare", href: "/compare" },
    { icon: Settings, label: "Settings", href: "/settings" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 glass-nav flex flex-col z-50">
            <div className="p-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl scientific-gradient flex items-center justify-center glow-accent">
                    <Hexagon className="text-white w-6 h-6" />
                </div>
                <span className="text-xl font-bold tracking-tight text-white/90">
                    Micro<span className="text-brand-accent">AI</span>
                </span>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative",
                                isActive
                                    ? "bg-brand-accent/10 text-brand-accent"
                                    : "text-white/50 hover:text-white/80 hover:bg-white/5"
                            )}
                        >
                            <item.icon className={cn(
                                "w-5 h-5 transition-transform duration-200",
                                isActive ? "scale-110" : "group-hover:scale-110"
                            )} />
                            <span className="font-medium">{item.label}</span>

                            {isActive && (
                                <motion.div
                                    layoutId="active-pill"
                                    className="absolute left-0 w-1 h-6 bg-brand-accent rounded-r-full"
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-white/5">
                <button className="w-full flex items-center gap-3 px-4 py-3 text-white/40 hover:text-red-400 hover:bg-red-400/5 rounded-xl transition-all duration-200 group">
                    <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </aside>
    );
}
