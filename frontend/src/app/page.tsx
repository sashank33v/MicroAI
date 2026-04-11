"use client";

import { motion } from "framer-motion";
import {
    ArrowUpRight,
    ArrowDownRight,
    Plus,
    ChevronRight,
    Search,
    Filter,
    Activity,
    Zap
} from "lucide-react";
import { dashboardStats, mockAnalyses } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import Link from "next/link";

export default function Dashboard() {
    return (
        <div className="space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                        Engineering <span className="scientific-gradient">Dashboard</span>
                    </h1>
                    <p className="text-white/40 text-sm">
                        Welcome back, Chief Metallurgist. System status: <span className="text-brand-accent font-medium">Nominal</span>
                    </p>
                </div>
                <Link
                    href="/analyze"
                    className="bg-brand-accent hover:bg-brand-accent/90 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all glow-accent"
                >
                    <Plus className="w-5 h-5" />
                    New Analysis
                </Link>
            </div>

            {/* AI Insights Banner */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 rounded-2xl glass-card relative overflow-hidden group"
            >
                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform duration-500">
                    <Zap className="w-32 h-32 text-brand-accent" />
                </div>
                <div className="relative z-10 flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-brand-accent/20 flex items-center justify-center">
                        <Activity className="w-6 h-6 text-brand-accent" />
                    </div>
                    <div className="flex-1">
                        <h3 className="text-lg font-bold text-white mb-1">AI System Insight</h3>
                        <p className="text-white/60 leading-relaxed max-w-2xl">
                            Detected a 12% shift in the average grain size of high-carbon steel batches over the last 48 hours. This suggests a potential variance in the induction hardening process. Recommend reviewing heat treatment settings.
                        </p>
                    </div>
                    <button className="text-brand-accent font-semibold flex items-center gap-1 hover:gap-2 transition-all">
                        Review Variance <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {dashboardStats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-6 rounded-2xl glass-card flex flex-col gap-2 group hover:border-brand-accent/30 transition-colors"
                    >
                        <span className="text-white/40 text-sm font-medium">{stat.label}</span>
                        <div className="flex items-baseline justify-between mt-1">
                            <span className="text-2xl font-bold text-white tracking-tight">{stat.value}</span>
                            <div className={cn(
                                "flex items-center text-xs font-bold px-2 py-1 rounded-lg",
                                stat.trend === "up" ? "bg-emerald-500/10 text-emerald-400" : "bg-blue-500/10 text-blue-400"
                            )}>
                                {stat.trend === "up" ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                                {stat.change}
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Recent Activity */}
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-bold text-white tracking-tight">Recent Metallurgical Analyses</h2>
                    <div className="flex gap-2">
                        <button className="p-2 text-white/40 hover:text-white transition-colors"><Search className="w-5 h-5" /></button>
                        <button className="p-2 text-white/40 hover:text-white transition-colors"><Filter className="w-5 h-5" /></button>
                    </div>
                </div>

                <div className="grid gap-4">
                    {mockAnalyses.map((analysis, i) => (
                        <motion.div
                            key={analysis.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="p-4 rounded-xl glass-card hover:bg-white/5 transition-all group flex items-center justify-between cursor-pointer"
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-16 h-16 rounded-lg bg-zinc-800 border border-white/5 overflow-hidden flex items-center justify-center text-white/10 italic text-[8px] relative">
                                    PHOTO
                                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-1 font-sans font-bold">
                                        #{analysis.id.slice(-4)}
                                    </div>
                                </div>
                                <div>
                                    <h4 className="font-bold text-white group-hover:text-brand-accent transition-colors">
                                        {analysis.name}
                                    </h4>
                                    <div className="flex gap-4 mt-1">
                                        <span className="text-white/30 text-xs">{analysis.type}</span>
                                        <span className="text-white/30 text-xs">•</span>
                                        <span className="text-white/30 text-xs">{analysis.date}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-8">
                                <div className="text-right">
                                    <div className="text-white font-bold text-sm tracking-tight">{analysis.grainSize} μm</div>
                                    <div className="text-white/20 text-[10px] uppercase font-bold">Grain size</div>
                                </div>
                                <div className="text-right">
                                    <div className={cn(
                                        "font-bold text-sm tracking-tight",
                                        analysis.defects > 5 ? "text-blue-400" : "text-brand-accent"
                                    )}>{analysis.defects}</div>
                                    <div className="text-white/20 text-[10px] uppercase font-bold">Defects</div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-white/20 group-hover:text-white group-hover:translate-x-1 transition-all" />
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
