"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Download,
    Share2,
    Zap,
    Info,
    Layers,
    Maximize2,
    ChevronLeft,
    CircleDot,
    Hexagon
} from "lucide-react";
import { mockAnalyses } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function AnalysisViewer() {
    const { id } = useParams();
    const analysis = mockAnalyses.find(a => a.id === id) || mockAnalyses[0];
    const [activeTab, setActiveTab] = useState<"overview" | "ai" | "defects">("overview");
    const [showOverlay, setShowOverlay] = useState(true);

    return (
        <div className="space-y-6 max-w-7xl mx-auto pb-12">
            {/* Breadcrumbs & Actions */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <Link href="/" className="p-2 rounded-xl hover:bg-white/5 text-white/40 hover:text-white transition-all">
                        <ChevronLeft className="w-6 h-6" />
                    </Link>
                    <div>
                        <div className="flex items-center gap-2">
                            <h1 className="text-2xl font-bold text-white tracking-tight">{analysis.name}</h1>
                            <span className="px-2 py-0.5 rounded-md bg-brand-accent/10 text-brand-accent text-[10px] font-bold uppercase tracking-wider">
                                {analysis.status}
                            </span>
                        </div>
                        <p className="text-white/40 text-xs mt-0.5">ID: {analysis.id} • Analyzed on {analysis.date}</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button className="p-3 rounded-xl bg-white/5 hover:bg-white/10 text-white/60 hover:text-white transition-all">
                        <Share2 className="w-5 h-5" />
                    </button>
                    <button className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all">
                        <Download className="w-5 h-5" />
                        Export Report
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Image Panel */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="rounded-3xl glass-card overflow-hidden relative group aspect-video bg-zinc-900 border-white/5 flex items-center justify-center">
                        {/* Mock Image Content */}
                        <div className="absolute inset-0 flex items-center justify-center text-white/5 italic text-sm">
                            [Micrograph Preview: {analysis.name}]
                        </div>

                        {/* Simulated Overlays */}
                        {showOverlay && (
                            <svg className="absolute inset-0 w-full h-full opacity-60 mix-blend-screen pointer-events-none">
                                <pattern id="grain-pattern" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                                    <path d="M0 50 Q 25 25, 50 50 T 100 50" fill="none" stroke="#10b981" strokeWidth="0.5" />
                                    <path d="M50 0 Q 25 25, 50 50 T 50 100" fill="none" stroke="#10b981" strokeWidth="0.5" />
                                </pattern>
                                <rect width="100%" height="100%" fill="url(#grain-pattern)" />
                            </svg>
                        )}

                        {/* Overlay Controls */}
                        <div className="absolute top-4 left-4 flex gap-2">
                            <button
                                onClick={() => setShowOverlay(!showOverlay)}
                                className={cn(
                                    "px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border",
                                    showOverlay
                                        ? "bg-brand-accent text-white border-brand-accent glow-accent"
                                        : "bg-black/40 text-white/60 border-white/10 hover:bg-black/60"
                                )}
                            >
                                Grain Overlay
                            </button>
                        </div>

                        <button className="absolute bottom-4 right-4 p-2 rounded-xl bg-black/40 text-white/60 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-md">
                            <Maximize2 className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 rounded-2xl glass-card bg-emerald-500/5 border-emerald-500/10">
                            <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">ASTM Grain Size</p>
                            <p className="text-2xl font-black text-brand-accent">{analysis.grainSize}</p>
                        </div>
                        <div className="p-4 rounded-2xl glass-card bg-blue-500/5 border-blue-500/10">
                            <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">Max Phase</p>
                            <p className="text-2xl font-black text-blue-400">{analysis.phases[0].percentage}%</p>
                        </div>
                        <div className="p-4 rounded-2xl glass-card bg-red-500/5 border-red-500/10">
                            <p className="text-white/40 text-[10px] uppercase font-bold tracking-widest mb-1">Inclusions</p>
                            <p className="text-2xl font-black text-red-400">{analysis.defects}</p>
                        </div>
                    </div>
                </div>

                {/* Results Sidebar */}
                <div className="space-y-6">
                    <div className="rounded-3xl glass-card overflow-hidden flex flex-col h-full">
                        <div className="flex border-b border-white/5 bg-white/20 backdrop-blur-xl">
                            {(["overview", "ai", "defects"] as const).map((tab) => (
                                <button
                                    key={tab}
                                    onClick={() => setActiveTab(tab)}
                                    className={cn(
                                        "flex-1 py-4 text-xs font-bold uppercase tracking-widest transition-all relative capitalize",
                                        activeTab === tab ? "text-white" : "text-white/30 hover:text-white/50"
                                    )}
                                >
                                    {tab}
                                    {activeTab === tab && (
                                        <motion.div layoutId="tab-underline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-accent px-4 mx-auto" />
                                    )}
                                </button>
                            ))}
                        </div>

                        <div className="p-6 flex-1 overflow-y-auto min-h-[400px]">
                            <AnimatePresence mode="wait">
                                {activeTab === "overview" && (
                                    <motion.div
                                        key="overview"
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        className="space-y-6"
                                    >
                                        <div className="space-y-4">
                                            <h4 className="text-xs font-bold text-white/40 uppercase tracking-widest">Phase Distribution</h4>
                                            <div className="space-y-4">
                                                {analysis.phases.map((phase) => (
                                                    <div key={phase.name} className="space-y-2">
                                                        <div className="flex justify-between text-sm">
                                                            <span className="text-white/80">{phase.name}</span>
                                                            <span className="text-white font-bold">{phase.percentage}%</span>
                                                        </div>
                                                        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full bg-brand-accent rounded-full"
                                                                style={{ width: `${phase.percentage}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="pt-4 border-t border-white/5 space-y-4">
                                            <h4 className="text-xs font-bold text-white/40 uppercase tracking-widest">Detailed properties</h4>
                                            <div className="grid grid-cols-2 gap-4">
                                                {[
                                                    { label: "Mean Area", value: "245 μm²" },
                                                    { label: "Aspect Ratio", value: "1.24" },
                                                    { label: "Orientation", value: "Random" },
                                                    { label: "Perimeter", value: "62 μm" },
                                                ].map(prop => (
                                                    <div key={prop.label} className="p-3 rounded-xl bg-white/5 border border-white/5">
                                                        <p className="text-white/30 text-[9px] uppercase font-bold tracking-wider">{prop.label}</p>
                                                        <p className="text-white font-bold">{prop.value}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {activeTab === "ai" && (
                                    <motion.div
                                        key="ai"
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        className="space-y-6"
                                    >
                                        <div className="p-4 rounded-2xl bg-brand-accent/10 border border-brand-accent/20 flex gap-3">
                                            <Zap className="w-5 h-5 text-brand-accent shrink-0" />
                                            <div>
                                                <h4 className="text-brand-accent font-bold text-sm">LLM Technical Briefing</h4>
                                                <p className="text-white/70 text-sm mt-1 leading-relaxed italic">
                                                    "Based on the observed martensitic plates and micro-segregation, this sample exhibits characteristics of rapid cooling. The homogeneity of the grain structure is within acceptable limits for critical aerospace applications."
                                                </p>
                                            </div>
                                        </div>
                                        <div className="space-y-4">
                                            <div className="flex items-start gap-3">
                                                <div className="w-5 h-5 rounded-full bg-brand-accent/20 flex items-center justify-center shrink-0 mt-0.5">
                                                    <CircleDot className="w-3 h-3 text-brand-accent" />
                                                </div>
                                                <p className="text-white/60 text-sm leading-relaxed">
                                                    Primary phase composition consists of acicular ferrite with trace amounts of proeutectoid cementite at grain boundaries.
                                                </p>
                                            </div>
                                            <div className="flex items-start gap-3">
                                                <div className="w-5 h-5 rounded-full bg-brand-accent/20 flex items-center justify-center shrink-0 mt-0.5">
                                                    <CircleDot className="w-3 h-3 text-brand-accent" />
                                                </div>
                                                <p className="text-white/60 text-sm leading-relaxed">
                                                    GMM clustering analysis indicates a high confidence (94.2%) in the identified phase area fractions.
                                                </p>
                                            </div>
                                        </div>
                                    </motion.div>
                                )}

                                {activeTab === "defects" && (
                                    <motion.div
                                        key="defects"
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        exit={{ opacity: 0, x: -10 }}
                                        className="flex flex-col items-center justify-center py-12 text-center space-y-4"
                                    >
                                        <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center">
                                            <Info className="text-white/20 w-8 h-8" />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-bold">Defect Catalog</h4>
                                            <p className="text-white/40 text-sm mt-1">Found {analysis.defects} significant anomalies</p>
                                        </div>
                                        <button className="text-brand-accent text-sm font-bold hover:underline capitalize">
                                            View defect coordinates
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
