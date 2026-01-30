import React, { useState, useEffect, useRef } from 'react';
import { Send, Terminal, Loader2, Shield, Activity, FileText, AlertTriangle, ShieldCheck } from 'lucide-react';
import { sendMessage } from '../services/api';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import Visualizer from './Visualizer';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId] = useState(() => Math.random().toString(36).substring(7));
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await sendMessage(sessionId, userMsg.content);
            const assistantMsg = {
                role: 'assistant',
                content: response.data.response_text,
                metrics: response.data.data, // Optional metrics
                dsl: response.data.dsl_query
            };
            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to SIEM Interface.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-background text-foreground">
            {/* Header */}
            <header className="flex items-center px-8 py-5 border-b border-white/5 glass top-0 z-30 sticky shadow-2xl">
                <div className="flex items-center group cursor-pointer">
                    <div className="bg-blue-500/10 p-2.5 rounded-2xl mr-4 group-hover:bg-blue-500/20 transition-all duration-500 neon-border">
                        <Shield className="w-6 h-6 text-blue-400 animate-pulse" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black tracking-[0.15em] text-white">
                            SIEM<span className="text-blue-500 ml-1">SPEAK</span>
                        </h1>
                        <div className="flex items-center space-x-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <p className="text-[9px] text-slate-400 font-bold tracking-[0.3em] uppercase">Neural Security Intelligence</p>
                        </div>
                    </div>
                </div>

                <div className="ml-auto hidden lg:flex items-center space-x-8">
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Network Bridge</span>
                        <div className="flex items-center bg-emerald-500/5 px-3 py-1 rounded-full border border-emerald-500/20">
                            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-tighter">Encrypted Connection</span>
                        </div>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Global Threat Status</span>
                        <span className="text-xs font-black text-blue-400 tracking-wider">NOMINAL_STATE_01</span>
                    </div>
                    <div className="h-10 w-[1px] bg-white/5 mx-4" />
                    <button className="relative group overflow-hidden bg-slate-900 border border-white/10 px-6 py-2 rounded-xl transition-all hover:border-blue-500/50">
                        <span className="relative z-10 text-[11px] font-black uppercase tracking-[0.2em] text-slate-400 group-hover:text-blue-400 transition-colors">Core_Diagnostics</span>
                        <div className="absolute inset-0 bg-blue-500/5 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
                    </button>
                </div>
            </header>

            <div className="flex flex-1 overflow-hidden cyber-grid">
                {/* Left Sidebar - Creative Feature */}
                <aside className="hidden xl:flex flex-col w-72 border-r border-white/5 glass p-6 space-y-8">
                    <div className="space-y-4">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em]">Active_Sessions</h3>
                        <div className="space-y-2">
                            <div className="p-3 bg-blue-500/5 border border-blue-500/20 rounded-xl flex items-center group cursor-pointer">
                                <Activity className="w-4 h-4 text-blue-400 mr-3" />
                                <span className="text-xs font-bold text-slate-200">Main_Investigation</span>
                            </div>
                        </div>
                    </div>

                    <div className="mt-auto p-4 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/5">
                        <ShieldCheck className="w-6 h-6 text-blue-400 mb-3" />
                        <h4 className="text-xs font-black text-white mb-1 uppercase tracking-wider">Secure Node</h4>
                        <p className="text-[10px] text-slate-400 leading-relaxed font-medium">All queries are processed through a local neural bridge to ensure data sovereignty.</p>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 flex flex-col relative">
                    {/* Chat Area - Wide Layout */}
                    <div className="flex-1 overflow-y-auto p-8 space-y-10 text-slate-100">
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto text-center space-y-10">
                                <div className="relative group">
                                    <div className="absolute inset-0 bg-blue-500/20 blur-[80px] rounded-full group-hover:bg-blue-500/30 transition-all duration-1000" />
                                    <div className="relative z-10 p-8 glass rounded-[40px] border-blue-500/30 neon-border animate-glow">
                                        <Terminal className="w-20 h-20 text-blue-400" />
                                    </div>
                                </div>
                                <div className="space-y-6">
                                    <h2 className="text-5xl font-black text-white tracking-tighter sm:text-6xl">
                                        BRIDGE_OPENED.
                                    </h2>
                                    <p className="text-slate-400 font-bold text-lg max-w-xl mx-auto leading-relaxed tracking-tight uppercase opacity-60">
                                        Speak to your SIEM. Analyze millions of logs in seconds.
                                        Autonomous threat discovery is online.
                                    </p>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full max-w-4xl">
                                    <button
                                        onClick={() => setInput("Show security event distribution by type")}
                                        className="group relative p-6 glass rounded-3xl hover:border-blue-500/50 transition-all text-left overflow-hidden"
                                    >
                                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 group-hover:rotate-12 transition-all duration-500">
                                            <Activity className="w-12 h-12" />
                                        </div>
                                        <span className="block text-[10px] uppercase tracking-[0.3em] text-blue-400 font-black mb-2">INIT_INV_01</span>
                                        <span className="text-md font-bold text-slate-200 group-hover:text-white transition-colors">Show event distribution...</span>
                                    </button>
                                    <button
                                        onClick={() => setInput("Find all failed login attempts in last hour")}
                                        className="group relative p-6 glass rounded-3xl hover:border-red-500/50 transition-all text-left overflow-hidden"
                                    >
                                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 group-hover:rotate-12 transition-all duration-500">
                                            <AlertTriangle className="w-12 h-12" />
                                        </div>
                                        <span className="block text-[10px] uppercase tracking-[0.3em] text-red-500 font-black mb-2">THREAT_HUNT_X</span>
                                        <span className="text-md font-bold text-slate-200 group-hover:text-white transition-colors">Find failed logins...</span>
                                    </button>
                                </div>
                            </div>
                        )}

                        {messages.map((msg, idx) => (
                            <div key={idx} className={cn("flex w-full group py-2", msg.role === 'user' ? "justify-end" : "justify-start")}>
                                <div className={cn(
                                    "relative max-w-[90%] xl:max-w-6xl p-6 rounded-[2rem] transition-all",
                                    msg.role === 'user'
                                        ? "bg-blue-600/20 border border-blue-500/30 text-blue-50 shadow-[0_0_30px_rgba(59,130,246,0.1)]"
                                        : "glass border-white/5 shadow-2xl"
                                )}>
                                    <div className="flex items-center space-x-3 mb-4 opacity-40 group-hover:opacity-100 transition-opacity">
                                        <div className={cn("w-2 h-2 rounded-full", msg.role === 'user' ? "bg-blue-400" : "bg-purple-400")} />
                                        <span className="text-[10px] font-black uppercase tracking-[0.4em]">
                                            {msg.role === 'user' ? 'AUTH_USER_SOURCE' : 'NEURAL_PROCESSOR_0.9'}
                                        </span>
                                    </div>
                                    <div className="prose prose-invert prose-slate max-w-none text-md font-medium text-slate-200 leading-relaxed">
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    </div>

                                    {msg.dsl && (
                                        <div className="mt-6 p-4 bg-slate-950/50 border border-white/5 rounded-2xl overflow-hidden group/dsl">
                                            <div className="flex items-center mb-3 text-slate-500">
                                                <Terminal className="w-3 h-3 mr-2 text-blue-400" />
                                                <span className="text-[10px] font-black uppercase tracking-[0.2em]">Generated_DSL_Query</span>
                                            </div>
                                            <pre className="text-[11px] font-mono text-blue-300/80 overflow-x-auto whitespace-pre-wrap leading-tight">
                                                {JSON.stringify(msg.dsl, null, 2)}
                                            </pre>
                                        </div>
                                    )}

                                    {msg.role === 'assistant' && msg.metrics && (
                                        <Visualizer metrics={msg.metrics} />
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start py-4">
                                <div className="glass border-white/5 rounded-3xl p-6 flex items-center space-x-4">
                                    <div className="relative">
                                        <div className="absolute inset-0 bg-blue-500/30 blur-lg rounded-full animate-pulse" />
                                        <Loader2 className="w-5 h-5 animate-spin text-blue-400 relative z-10" />
                                    </div>
                                    <span className="text-xs font-black text-slate-400 uppercase tracking-[0.3em]">Processing_Data_Stream...</span>
                                </div>
                            </div>
                        )}
                        <div ref={scrollRef} />
                    </div>

                    {/* Wide Input Area */}
                    <div className="p-8 border-t border-white/5 glass mt-auto">
                        <div className="max-w-6xl mx-auto flex space-x-4 relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-[2rem] opacity-20 blur group-within:opacity-40 transition duration-1000"></div>
                            <input
                                type="text"
                                className="relative flex-1 bg-slate-950/80 text-white px-8 py-5 rounded-[1.5rem] border border-white/10 focus:outline-none focus:border-blue-500/50 transition-all text-sm font-bold tracking-tight placeholder:text-slate-600"
                                placeholder="Transmit security inquiry to SIEM Speak..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                disabled={loading}
                            />
                            <button
                                onClick={handleSend}
                                disabled={loading || !input.trim()}
                                className="relative bg-blue-600 text-white px-8 rounded-[1.5rem] hover:bg-blue-500 hover:shadow-[0_0_20px_rgba(59,130,246,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed group/btn"
                            >
                                <Send className="w-5 h-5 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                            </button>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
