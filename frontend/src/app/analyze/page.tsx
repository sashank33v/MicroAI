"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Upload,
    FileImage,
    X,
    CheckCircle2,
    Settings2,
    Cpu,
    Search,
    AlertCircle
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function AnalyzePage() {
    const [file, setFile] = useState<File | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleUpload = () => {
        if (!file) return;
        setIsUploading(true);
        // Simulate upload progress
        const interval = setInterval(() => {
            setProgress((prev) => {
                if (prev >= 100) {
                    clearInterval(interval);
                    return 100;
                }
                return prev + 5;
            });
        }, 100);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                    New <span className="scientific-gradient">Analysis</span>
                </h1>
                <p className="text-white/40 text-sm">
                    Upload a high-resolution micrograph for ASTM-compliant grain and phase analysis.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                    {/* Upload Zone */}
                    <div
                        className={cn(
                            "border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center transition-all duration-300 relative overflow-hidden",
                            file ? "border-brand-accent/50 bg-brand-accent/5" : "border-white/10 hover:border-white/20 hover:bg-white/5",
                            isUploading && "pointer-events-none"
                        )}
                    >
                        <AnimatePresence mode="wait">
                            {!file ? (
                                <motion.div
                                    key="empty"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="flex flex-col items-center text-center space-y-4"
                                >
                                    <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center">
                                        <Upload className="w-8 h-8 text-white/40" />
                                    </div>
                                    <div>
                                        <p className="text-white font-semibold">Drop your micrograph here</p>
                                        <p className="text-white/30 text-sm mt-1">Supports PNG, JPG (Max 50MB)</p>
                                    </div>
                                    <button className="bg-white/10 hover:bg-white/20 text-white px-6 py-2 rounded-xl text-sm font-medium transition-colors">
                                        Browse Files
                                    </button>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="selected"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className="w-full space-y-6"
                                >
                                    <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/10">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-xl bg-brand-accent/20 flex items-center justify-center">
                                                <FileImage className="w-6 h-6 text-brand-accent" />
                                            </div>
                                            <div className="text-left">
                                                <p className="text-white font-medium truncate max-w-[200px]">{file.name || "Micrograph_Sample_01.jpg"}</p>
                                                <p className="text-white/30 text-xs">2.4 MB • Ready to process</p>
                                            </div>
                                        </div>
                                        {!isUploading && (
                                            <button
                                                onClick={() => setFile(null)}
                                                className="p-2 text-white/20 hover:text-red-400 transition-colors"
                                            >
                                                <X className="w-5 h-5" />
                                            </button>
                                        )}
                                    </div>

                                    {isUploading && (
                                        <div className="space-y-3">
                                            <div className="flex justify-between text-xs font-bold uppercase tracking-wider">
                                                <span className="text-white/40">Analyzing structures...</span>
                                                <span className="text-brand-accent">{progress}%</span>
                                            </div>
                                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${progress}%` }}
                                                    className="h-full scientific-gradient shadow-[0_0_15px_rgba(16,185,129,0.5)]"
                                                />
                                            </div>
                                            <div className="grid grid-cols-2 gap-2">
                                                <div className="flex items-center gap-2 text-[10px] text-white/40">
                                                    <CheckCircle2 className={cn("w-3 h-3", progress > 20 ? "text-brand-accent" : "text-white/10")} />
                                                    Pre-processing
                                                </div>
                                                <div className="flex items-center gap-2 text-[10px] text-white/40">
                                                    <CheckCircle2 className={cn("w-3 h-3", progress > 50 ? "text-brand-accent" : "text-white/10")} />
                                                    Grain Detection
                                                </div>
                                                <div className="flex items-center gap-2 text-[10px] text-white/40">
                                                    <CheckCircle2 className={cn("w-3 h-3", progress > 80 ? "text-brand-accent" : "text-white/10")} />
                                                    Phase Estimation
                                                </div>
                                                <div className="flex items-center gap-2 text-[10px] text-white/40">
                                                    <CheckCircle2 className={cn("w-3 h-3", progress === 100 ? "text-brand-accent" : "text-white/10")} />
                                                    Report Generation
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {!isUploading && (
                                        <button
                                            onClick={handleUpload}
                                            className="w-full scientific-gradient text-white py-4 rounded-2xl font-bold flex items-center justify-center gap-2 glow-accent hover:scale-[1.02] transition-transform"
                                        >
                                            <Cpu className="w-5 h-5" />
                                            Execute Analysis
                                        </button>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Hidden Input for demo */}
                        <input
                            type="file"
                            className="absolute inset-0 opacity-0 cursor-pointer"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            disabled={isUploading}
                        />
                    </div>

                    <div className="p-6 rounded-3xl glass-card flex items-start gap-4 border-blue-500/20 bg-blue-500/5">
                        <AlertCircle className="w-6 h-6 text-blue-400 shrink-0" />
                        <div className="space-y-1">
                            <h4 className="text-blue-400 font-bold text-sm uppercase tracking-wider">Analysis Tip</h4>
                            <p className="text-white/60 text-sm leading-relaxed">
                                For best results with martensitic structures, ensure consistent etching and use a magnification of at least 500x.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="p-6 rounded-3xl glass-card space-y-4">
                        <h3 className="text-white font-bold flex items-center gap-2">
                            <Settings2 className="w-5 h-5 text-brand-accent" />
                            Parameters
                        </h3>
                        <div className="space-y-4 pt-2">
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-white/40 tracking-widest">Magnification</label>
                                <select className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-accent/50">
                                    <option>100x</option>
                                    <option selected>500x</option>
                                    <option>1000x</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] uppercase font-bold text-white/40 tracking-widest">Material Type</label>
                                <select className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-accent/50">
                                    <option>Carbon Steel</option>
                                    <option>Stainless Steel</option>
                                    <option>Cast Iron</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 rounded-3xl glass-card space-y-4">
                        <h3 className="text-white font-bold flex items-center gap-2">
                            <Search className="w-5 h-5 text-blue-400" />
                            Capabilities
                        </h3>
                        <ul className="space-y-3 text-sm text-white/60">
                            <li className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                                ASTM E112 Grain Sizing
                            </li>
                            <li className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                                Phase Area Fraction
                            </li>
                            <li className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                                Non-metallic Inclusions
                            </li>
                            <li className="flex items-center gap-3">
                                <div className="w-1.5 h-1.5 rounded-full bg-brand-accent" />
                                Defect Classification
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}
