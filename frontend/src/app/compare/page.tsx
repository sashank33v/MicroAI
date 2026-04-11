"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
    GitCompare,
    ChevronRight,
    Search,
    Layers,
    TrendingUp,
    AlertCircle,
    CircleDot
} from "lucide-react";
import { mockAnalyses } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

export default function ComparePage() {
    const [leftId, setLeftId] = useState(mockAnalyses[0].id);
    const [rightId, setRightId] = useState(mockAnalyses[1].id);

    const left = mockAnalyses.find(a => a.id === leftId)!;
    const right = mockAnalyses.find(a => a.id === rightId)!;

    return (
        <div className="space-y-8 max-w-7xl mx-auto pb-12">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                        Analysis <span className="scientific-gradient">Comparison</span>
                    </h1>
                    <p className="text-white/40 text-sm">
                        Side-by-side evaluation of structural variances and phase distributions.
                    </p>
                </div>
                <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-brand-accent/10 border border-brand-accent/20 text-brand-accent text-xs font-bold uppercase tracking-wider">
                    <GitCompare className="w-4 h-4" />
                    Delta tracking active
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
                {/* Comparison Line */}
                <div className="hidden lg:block absolute left-1/2 top-0 bottom-0 w-px bg-white/5 z-0" />

                {/* Left Selection */}
                <div className="space-y-6 relative z-10">
                    <select
                        value={leftId}
                        onChange={(e) => setLeftId(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:border-brand-accent/50 transition-all appearance-none cursor-pointer"
                    >
                        {mockAnalyses.map(a => <option key={a.id} value={a.id}>{a.name} ({a.id})</option>)}
                    </select>

                    <div className="rounded-3xl glass-card overflow-hidden aspect-video bg-zinc-900 border-white/5 flex items-center justify-center text-[10px] text-white/10 italic">
                        [Micrograph: {left.id}]
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-2xl glass-card bg-white/5">
                            <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest mb-1">ASTM Grain Size</p>
                            <p className="text-xl font-black text-white">{left.grainSize}</p>
                        </div>
                        <div className="p-4 rounded-2xl glass-card bg-white/5">
                            <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest mb-1">Defects</p>
                            <p className="text-xl font-black text-white">{left.defects}</p>
                        </div>
                    </div>
                </div>

                {/* Right Selection */}
                <div className="space-y-6 relative z-10">
                    <select
                        value={rightId}
                        onChange={(e) => setRightId(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:border-brand-accent/50 transition-all appearance-none cursor-pointer"
                    >
                        {mockAnalyses.map(a => <option key={a.id} value={a.id}>{a.name} ({a.id})</option>)}
                    </select>

                    <div className="rounded-3xl glass-card overflow-hidden aspect-video bg-zinc-900 border-white/5 flex items-center justify-center text-[10px] text-white/10 italic">
                        [Micrograph: {right.id}]
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-2xl glass-card bg-white/5">
                            <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest mb-1">ASTM Grain Size</p>
                            <p className="text-xl font-black text-white">{right.grainSize}</p>
                        </div>
                        <div className="p-4 rounded-2xl glass-card bg-white/5">
                            <p className="text-white/30 text-[9px] uppercase font-bold tracking-widest mb-1">Defects</p>
                            <p className="text-xl font-black text-white">{right.defects}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Comparison Table */}
            <div className="rounded-3xl glass-card overflow-hidden">
                <div className="p-6 border-b border-white/5 bg-white/5">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Layers className="w-5 h-5 text-brand-accent" />
                        Structural Variance Matrix
                    </h3>
                </div>
                <table className="w-full text-left">
                    <thead>
                        <tr className="border-b border-white/5">
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-white/30">Property</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-white/30">{left.id}</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-white/30">{right.id}</th>
                            <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-widest text-white/30">Variance</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {[
                            { label: "Grain Size (μm)", l: left.grainSize, r: right.grainSize },
                            { label: "Defect Count", l: left.defects, r: right.defects },
                            { label: "Primary Phase %", l: left.phases[0].percentage, r: right.phases[0].percentage },
                            { label: "Secondary Phase %", l: left.phases[1]?.percentage || 0, r: right.phases[1]?.percentage || 0 },
                        ].map((row) => {
                            const diff = row.r - row.l;
                            const percentDiff = row.l !== 0 ? ((diff / row.l) * 100).toFixed(1) : "0";
                            return (
                                <tr key={row.label} className="group hover:bg-white/5 transition-colors">
                                    <td className="px-6 py-4 text-sm font-medium text-white/60">{row.label}</td>
                                    <td className="px-6 py-4 text-sm font-bold text-white">{row.l}</td>
                                    <td className="px-6 py-4 text-sm font-bold text-white">{row.r}</td>
                                    <td className={cn(
                                        "px-6 py-4 text-sm font-bold",
                                        Number(percentDiff) > 0 ? "text-blue-400" : "text-brand-accent"
                                    )}>
                                        {Number(percentDiff) > 0 ? "+" : ""}{percentDiff}%
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Comparison Insights */}
            <div className="p-8 rounded-3xl glass-card border-brand-accent/20 bg-brand-accent/5 flex items-start gap-6">
                <div className="w-12 h-12 rounded-2xl bg-brand-accent/20 flex items-center justify-center shrink-0">
                    <TrendingUp className="w-6 h-6 text-brand-accent" />
                </div>
                <div className="space-y-2">
                    <h3 className="text-xl font-bold text-white">Comparative AI Synthesis</h3>
                    <p className="text-white/60 leading-relaxed text-sm">
                        Sample <span className="text-white font-bold">{right.id}</span> shows a significantly more refined grain
                        structure (Variance: {(left.grainSize - right.grainSize).toFixed(1)} μm) compared to <span className="text-white font-bold">{left.id}</span>.
                        This indicates that the {right.type} underwent a more controlled thermal cycle or possesses a higher concentration
                        of grain-refining elements such as Vanadium or Titanium.
                    </p>
                </div>
            </div>
        </div>
    );
}
