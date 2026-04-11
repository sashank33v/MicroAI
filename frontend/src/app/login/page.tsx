"use client";

import { motion } from "framer-motion";
import {
    Hexagon,
    Mail,
    Lock,
    ArrowRight,
    Fingerprint,
    ShieldCheck
} from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
    return (
        <div className="fixed inset-0 bg-brand-dark flex items-center justify-center p-6 z-[100] overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[60%] rounded-full bg-brand-accent/5 blur-[120px]" />
            <div className="absolute bottom-[-10%] left-[-5%] w-[40%] h-[50%] rounded-full bg-blue-500/5 blur-[100px]" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-md w-full p-8 rounded-[2.5rem] glass-card relative z-10 border-white/10"
            >
                <div className="flex flex-col items-center text-center space-y-6">
                    <div className="w-16 h-16 rounded-2xl scientific-gradient flex items-center justify-center glow-accent">
                        <Hexagon className="text-white w-8 h-8" />
                    </div>

                    <div>
                        <h1 className="text-2xl font-bold text-white tracking-tight">System Authentication</h1>
                        <p className="text-white/40 text-sm mt-1">Authorized personnel restricted access only.</p>
                    </div>

                    <div className="w-full space-y-4">
                        <div className="space-y-2 text-left">
                            <label className="text-[10px] uppercase font-bold text-white/40 tracking-widest pl-2">Credential ID</label>
                            <div className="relative group">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-brand-accent transition-colors" />
                                <input
                                    type="email"
                                    defaultValue="sashank@microai.labs"
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 text-white text-sm focus:outline-none focus:border-brand-accent/50 transition-all"
                                    placeholder="name@organization.com"
                                />
                            </div>
                        </div>

                        <div className="space-y-2 text-left">
                            <label className="text-[10px] uppercase font-bold text-white/40 tracking-widest pl-2">Access Protocol</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 group-focus-within:text-brand-accent transition-colors" />
                                <input
                                    type="password"
                                    defaultValue="••••••••"
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-4 py-4 text-white text-sm focus:outline-none focus:border-brand-accent/50 transition-all"
                                    placeholder="Enter protocol password"
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between px-2 text-xs font-medium">
                            <label className="flex items-center gap-2 text-white/40 hover:text-white/60 cursor-pointer transition-colors">
                                <div className="w-4 h-4 rounded border border-white/10 flex items-center justify-center bg-white/5">
                                    <div className="w-2 h-2 rounded-full bg-brand-accent" />
                                </div>
                                Stay Authenticated
                            </label>
                            <button className="text-brand-accent hover:underline">Forgot Protocol?</button>
                        </div>

                        <Link
                            href="/"
                            className="w-full scientific-gradient text-white py-4 rounded-2xl font-bold flex items-center justify-center gap-2 glow-accent hover:scale-[1.02] transition-transform mt-2 group"
                        >
                            Initialize Session
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </div>

                    <div className="pt-6 border-t border-white/5 w-full flex justify-center gap-6">
                        <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/30 hover:text-white/60 transition-colors">
                            <Fingerprint className="w-4 h-4" />
                            Biometric
                        </button>
                        <button className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-white/30 hover:text-white/60 transition-colors">
                            <ShieldCheck className="w-4 h-4" />
                            SAML 2.0
                        </button>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
