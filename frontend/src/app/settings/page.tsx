"use client";

import { motion } from "framer-motion";
import {
    Settings,
    User,
    Bell,
    Shield,
    Database,
    Cpu,
    Save,
    ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";

const sections = [
    { id: "profile", icon: User, label: "Professional Profile" },
    { id: "notifications", icon: Bell, label: "Alert Configuration" },
    { id: "security", icon: Shield, label: "Data Protection" },
    { id: "engine", icon: Cpu, label: "AI Analysis Engine" },
    { id: "database", icon: Database, label: "Export & Storage" },
];

export default function SettingsPage() {
    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-12">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                    System <span className="scientific-gradient">Settings</span>
                </h1>
                <p className="text-white/40 text-sm">
                    Configure your metallurgical analysis preferences and security protocols.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <aside className="md:col-span-1 space-y-2">
                    {sections.map(section => (
                        <button
                            key={section.id}
                            className={cn(
                                "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-sm font-medium",
                                section.id === "profile"
                                    ? "bg-brand-accent/10 text-brand-accent"
                                    : "text-white/40 hover:text-white/70 hover:bg-white/5"
                            )}
                        >
                            <section.icon className="w-4 h-4" />
                            {section.label}
                        </button>
                    ))}
                </aside>

                <div className="md:col-span-3 space-y-6">
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="p-8 rounded-3xl glass-card space-y-8"
                    >
                        <div className="space-y-6">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2 pb-4 border-b border-white/5">
                                <User className="w-5 h-5 text-brand-accent" />
                                Profile Information
                            </h3>

                            <div className="grid grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold uppercase tracking-widest text-white/30">Display Name</label>
                                    <input type="text" defaultValue="Sashank" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-accent/50" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold uppercase tracking-widest text-white/30">Organization</label>
                                    <input type="text" defaultValue="Master Craft Labs" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-accent/50" />
                                </div>
                                <div className="col-span-2 space-y-2">
                                    <label className="text-[10px] font-bold uppercase tracking-widest text-white/30">Professional Email</label>
                                    <input type="email" defaultValue="sashank@microai.labs" className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-brand-accent/50" />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6 pt-4">
                            <h3 className="text-lg font-bold text-white flex items-center gap-2 pb-4 border-b border-white/5">
                                <Cpu className="w-5 h-5 text-blue-400" />
                                AI Analysis Preferences
                            </h3>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 rounded-2xl bg-white/2 border border-white/5">
                                    <div>
                                        <p className="text-white font-bold text-sm">Enhanced Grain Sensitivity</p>
                                        <p className="text-white/40 text-xs">Improve detection for fine martensitic needles</p>
                                    </div>
                                    <div className="w-12 h-6 rounded-full bg-brand-accent/20 relative cursor-pointer">
                                        <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-brand-accent shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                                    </div>
                                </div>
                                <div className="flex items-center justify-between p-4 rounded-2xl bg-white/2 border border-white/5">
                                    <div>
                                        <p className="text-white font-bold text-sm">Auto-generate AI Briefing</p>
                                        <p className="text-white/40 text-xs">Summarize results using technical LLM after every scan</p>
                                    </div>
                                    <div className="w-12 h-6 rounded-full bg-brand-accent/20 relative cursor-pointer">
                                        <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-brand-accent shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="pt-8 flex justify-end">
                            <button className="bg-brand-accent hover:bg-brand-accent/90 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all glow-accent">
                                <Save className="w-4 h-4" />
                                Save Changes
                            </button>
                        </div>
                    </motion.div>
                </div>
            </div>
        </div>
    );
}
