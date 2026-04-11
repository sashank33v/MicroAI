"use client";

import { motion } from "framer-motion";
import {
    FileText,
    Search,
    Filter,
    Download,
    MoreVertical,
    Calendar,
    Layers,
    Trash2
} from "lucide-react";
import { mockAnalyses } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import Link from "next/link";

export default function ReportsPage() {
    return (
        <div className="space-y-8 max-w-7xl mx-auto">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                        Analysis <span className="scientific-gradient">Reports</span>
                    </h1>
                    <p className="text-white/40 text-sm">
                        Access and manage your complete historical database of metallurgical evaluations.
                    </p>
                </div>
                <div className="flex gap-4">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 group-focus-within:text-brand-accent transition-colors" />
                        <input
                            type="text"
                            placeholder="Search reports..."
                            className="bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-brand-accent/50 transition-all w-64"
                        />
                    </div>
                    <button className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:text-white transition-all">
                        <Filter className="w-5 h-5" />
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockAnalyses.map((analysis, i) => (
                    <motion.div
                        key={analysis.id}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="rounded-3xl glass-card overflow-hidden group flex flex-col"
                    >
                        <div className="aspect-video bg-zinc-900 relative border-b border-white/5 overflow-hidden flex items-center justify-center text-[10px] text-white/5 italic">
                            [Micrograph Thumnail: {analysis.id}]
                            <div className="absolute top-4 right-4 px-2 py-1 rounded-md bg-black/60 backdrop-blur-md border border-white/10 text-[10px] font-bold text-white/60 z-10">
                                {analysis.type}
                            </div>
                        </div>

                        <div className="p-6 space-y-4 flex-1">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-white font-bold transition-colors group-hover:text-brand-accent">
                                        {analysis.name}
                                    </h3>
                                    <div className="flex items-center gap-2 mt-1 text-white/40 text-xs">
                                        <Calendar className="w-3 h-3" />
                                        {analysis.date}
                                    </div>
                                </div>
                                <button className="p-1 text-white/20 hover:text-white transition-colors">
                                    <MoreVertical className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                                    <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest">Grain Size</p>
                                    <p className="text-white font-bold">{analysis.grainSize} μm</p>
                                </div>
                                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                                    <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest">Defects</p>
                                    <p className="text-white font-bold">{analysis.defects}</p>
                                </div>
                            </div>

                            <div className="flex gap-2 pt-2">
                                <Link
                                    href={`/analysis/${analysis.id}`}
                                    className="flex-1 bg-white/5 hover:bg-white/10 text-white font-bold py-3 rounded-xl text-center text-xs transition-all border border-white/5"
                                >
                                    View Details
                                </Link>
                                <button className="p-3 rounded-xl bg-white/5 border border-white/5 text-white/30 hover:text-white hover:bg-white/10 transition-all">
                                    <Download className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </motion.div>
                ))}

                {/* Empty State / Add New Card */}
                <Link
                    href="/analyze"
                    className="rounded-3xl border-2 border-dashed border-white/5 hover:border-brand-accent/20 hover:bg-brand-accent/5 transition-all flex flex-col items-center justify-center p-12 text-center group"
                >
                    <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        <FileText className="w-8 h-8 text-white/20 group-hover:text-brand-accent" />
                    </div>
                    <h3 className="text-white/40 font-bold group-hover:text-white transition-colors">Generate New Report</h3>
                    <p className="text-white/20 text-xs mt-1">Upload files to begin analysis</p>
                </Link>
            </div>
        </div>
    );
}
