import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, Shield, TrendingUp, Clock, Zap } from 'lucide-react';
import { sendMessage } from '../services/api';
import ReactMarkdown from 'react-markdown';
import Visualizer from './Visualizer';

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
                metrics: response.data.data,
                dsl: response.data.dsl_query
            };
            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error(error);
            const errorDetail = error.response?.data?.detail || 'Error connecting to SIEM Interface.';
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `### ⚠️ Connection Error\n\n${errorDetail}\n\n*Please check your SIEM backend connection.*`
            }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-teal-50/20 via-white to-teal-50/30 overflow-hidden relative">
            {/* Subtle background gradient orbs */}
            <div className="gradient-orb gradient-orb-1"></div>
            <div className="gradient-orb gradient-orb-2"></div>
            <div className="gradient-orb gradient-orb-3"></div>

            {/* Clean Modern Header */}
            <header className="bg-white/70 backdrop-blur-xl border-b border-gray-200/40 shadow-sm animate-fade-in sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    {/* Logo Section */}
                    <div className="flex items-center space-x-3 group cursor-pointer">
                        <div className="relative">
                            <div className="absolute inset-0 bg-teal-500/20 rounded-xl blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
                            <div className="relative bg-gradient-to-br from-teal-500 to-teal-600 p-2.5 rounded-xl transform group-hover:scale-105 transition-transform">
                                <Shield className="w-5 h-5 text-white" />
                            </div>
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">
                                SIEM<span className="text-teal-600">Pro</span>
                            </h1>
                            <p className="text-xs text-gray-500">AI-Powered Analytics</p>
                        </div>
                    </div>

                    {/* Status Indicators */}
                    <div className="hidden md:flex items-center space-x-6">
                        <div className="flex items-center space-x-2 px-4 py-2 bg-green-50 rounded-lg border border-green-200/60">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow"></div>
                            <span className="text-sm font-medium text-green-700">Online</span>
                        </div>
                        <div className="flex items-center space-x-2 px-4 py-2 bg-teal-50 rounded-lg border border-teal-200/60">
                            <Clock className="w-4 h-4 text-teal-600" />
                            <span className="text-sm font-medium text-teal-700">{new Date().toLocaleTimeString()}</span>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Chat Messages Area */}
                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-6">
                    {messages.length === 0 && (
                        <div className="relative flex flex-col items-center justify-center h-full max-w-6xl mx-auto text-center space-y-8 px-4">

                            {/* Doodle decorations – light SVG line art scattered around the hero */}
                            <svg className="pointer-events-none absolute inset-0 w-full h-full overflow-visible opacity-[0.09]" viewBox="0 0 1000 600" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
                                {/* wavy line top-left */}
                                <path d="M60 80 Q100 30 140 80 Q180 130 220 80" fill="none" stroke="#3AAFA9" strokeWidth="3" strokeLinecap="round"/>
                                {/* small circle cluster top-right */}
                                <circle cx="820" cy="72" r="22" fill="none" stroke="#4ECDC4" strokeWidth="2.5"/>
                                <circle cx="855" cy="58" r="10" fill="none" stroke="#4ECDC4" strokeWidth="2"/>
                                <circle cx="800" cy="90" r="6" fill="#4ECDC4" opacity="0.4"/>
                                {/* dotted arc mid-left */}
                                <path d="M30 330 Q90 280 60 230" fill="none" stroke="#3AAFA9" strokeWidth="2.5" strokeDasharray="7 7" strokeLinecap="round"/>
                                {/* zigzag bottom-right */}
                                <polyline points="780,470 820,430 860,470 900,430 940,470" fill="none" stroke="#4ECDC4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                                {/* sparkle star top-centre-left */}
                                <g transform="translate(150,180)" opacity="0.7">
                                    <line x1="0" y1="-10" x2="0" y2="10" stroke="#3AAFA9" strokeWidth="2.5" strokeLinecap="round"/>
                                    <line x1="-10" y1="0" x2="10" y2="0" stroke="#3AAFA9" strokeWidth="2.5" strokeLinecap="round"/>
                                    <line x1="-6" y1="-6" x2="6" y2="6" stroke="#3AAFA9" strokeWidth="1.8" strokeLinecap="round"/>
                                    <line x1="6" y1="-6" x2="-6" y2="6" stroke="#3AAFA9" strokeWidth="1.8" strokeLinecap="round"/>
                                </g>
                                {/* loop / spiral near bottom-left */}
                                <path d="M120 490 Q135 470 155 480 Q175 490 165 510 Q155 530 135 525 Q115 520 120 500" fill="none" stroke="#4ECDC4" strokeWidth="2.5" strokeLinecap="round"/>
                                {/* three dots mid-right */}
                                <circle cx="910" cy="270" r="3.5" fill="#3AAFA9"/>
                                <circle cx="925" cy="270" r="3.5" fill="#3AAFA9"/>
                                <circle cx="940" cy="270" r="3.5" fill="#3AAFA9"/>
                                {/* soft curve underline centre-bottom */}
                                <path d="M350 560 Q500 585 650 560" fill="none" stroke="#4ECDC4" strokeWidth="2.5" strokeLinecap="round"/>
                                {/* small triangle top-centre */}
                                <polygon points="500,35 488,58 512,58" fill="none" stroke="#3AAFA9" strokeWidth="2" strokeLinejoin="round"/>
                                {/* plus sign bottom-right area */}
                                <g transform="translate(750,530)" opacity="0.6">
                                    <line x1="0" y1="-8" x2="0" y2="8" stroke="#4ECDC4" strokeWidth="2.5" strokeLinecap="round"/>
                                    <line x1="-8" y1="0" x2="8" y2="0" stroke="#4ECDC4" strokeWidth="2.5" strokeLinecap="round"/>
                                </g>
                                {/* diamond mid-top-right */}
                                <polygon points="870,160 880,175 870,190 860,175" fill="none" stroke="#3AAFA9" strokeWidth="2" strokeLinejoin="round"/>
                                {/* small wavy squiggle centre-left */}
                                <path d="M60 420 Q75 410 90 420 Q105 430 120 420" fill="none" stroke="#4ECDC4" strokeWidth="2" strokeLinecap="round"/>
                            </svg>

                            {/* Welcome Icon */}
                            <div className="relative animate-scale-in">
                                <div className="absolute inset-0 bg-teal-500/15 blur-3xl rounded-full animate-pulse-slow"></div>
                                <div className="relative bg-gradient-to-br from-teal-500 to-teal-600 p-7 rounded-3xl shadow-xl transform hover:scale-105 transition-transform duration-300">
                                    <Sparkles className="w-14 h-14 text-white" />
                                </div>
                            </div>

                            {/* Welcome Message */}
                            <div className="space-y-3 animate-slide-up delay-100">
                                <h2 className="text-4xl md:text-5xl font-bold text-gray-900 tracking-tight">
                                    Welcome to <span className="text-teal-600">SIEMPro</span>
                                </h2>
                                <p className="text-lg text-gray-500 max-w-xl mx-auto leading-relaxed">
                                    Ask questions about your security logs and get instant insights powered by AI
                                </p>
                            </div>

                            {/* Quick Actions */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 w-full max-w-5xl mt-6">
                                <button
                                    onClick={() => setInput("Show security event distribution by type")}
                                    className="group p-6 bg-white/80 backdrop-blur-sm hover:bg-teal-50/80 border border-gray-200/70 hover:border-teal-400 rounded-2xl text-left transition-all shadow-sm hover:shadow-lg hover:-translate-y-1 animate-slide-up delay-200"
                                >
                                    <TrendingUp className="w-7 h-7 text-teal-600 mb-3 group-hover:scale-110 group-hover:rotate-3 transition-all" />
                                    <h3 className="font-semibold text-gray-900 mb-1">Event Distribution</h3>
                                    <p className="text-sm text-gray-500">View security events by type</p>
                                </button>

                                <button
                                    onClick={() => setInput("Find all failed login attempts in last hour")}
                                    className="group p-6 bg-white/80 backdrop-blur-sm hover:bg-red-50/80 border border-gray-200/70 hover:border-red-400 rounded-2xl text-left transition-all shadow-sm hover:shadow-lg hover:-translate-y-1 animate-slide-up delay-300"
                                >
                                    <Shield className="w-7 h-7 text-red-500 mb-3 group-hover:scale-110 group-hover:rotate-3 transition-all" />
                                    <h3 className="font-semibold text-gray-900 mb-1">Failed Logins</h3>
                                    <p className="text-sm text-gray-500">Detect unauthorized access</p>
                                </button>

                                <button
                                    onClick={() => setInput("Show high severity alerts from today")}
                                    className="group p-6 bg-white/80 backdrop-blur-sm hover:bg-amber-50/80 border border-gray-200/70 hover:border-amber-400 rounded-2xl text-left transition-all shadow-sm hover:shadow-lg hover:-translate-y-1 animate-slide-up delay-400"
                                >
                                    <Zap className="w-7 h-7 text-amber-500 mb-3 group-hover:scale-110 group-hover:rotate-3 transition-all" />
                                    <h3 className="font-semibold text-gray-900 mb-1">High Alerts</h3>
                                    <p className="text-sm text-gray-500">Critical security incidents</p>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Messages */}
                    {messages.map((msg, idx) => (
                        <div key={idx} className="w-full animate-slide-up">
                            <div className={`group relative w-full p-6 lg:p-8 rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 ${
                                msg.role === 'user'
                                    ? 'bg-gradient-to-br from-teal-500 via-teal-600 to-teal-700 text-white'
                                    : 'bg-white border-2 border-gray-200 hover:border-teal-300'
                            }`}>
                                {/* Decorative gradient overlay on hover */}
                                <div className={`absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none ${
                                    msg.role === 'user' 
                                        ? 'bg-gradient-to-br from-teal-400/20 to-teal-600/20' 
                                        : 'bg-gradient-to-br from-teal-50/50 to-teal-100/50'
                                }`}></div>

                                {/* Content */}
                                <div className="relative z-10">
                                    {/* Role Badge */}
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-3">
                                            <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform ${
                                                msg.role === 'user' 
                                                    ? 'bg-white/20 backdrop-blur-sm' 
                                                    : 'bg-gradient-to-br from-teal-500 to-teal-600'
                                            }`}>
                                                {msg.role === 'user' ? (
                                                    <span className="text-white font-bold text-sm">You</span>
                                                ) : (
                                                    <Sparkles className="w-5 h-5 text-white" />
                                                )}
                                            </div>
                                            <div>
                                                <span className={`text-sm font-bold block ${
                                                    msg.role === 'user' ? 'text-white' : 'text-gray-900'
                                                }`}>
                                                    {msg.role === 'user' ? 'You' : 'AI Assistant'}
                                                </span>
                                                <span className={`text-xs ${
                                                    msg.role === 'user' ? 'text-teal-100' : 'text-gray-500'
                                                }`}>
                                                    {new Date().toLocaleTimeString()}
                                                </span>
                                            </div>
                                        </div>
                                        
                                        {/* Interactive dot indicator */}
                                        <div className={`w-2 h-2 rounded-full animate-pulse-slow ${
                                            msg.role === 'user' ? 'bg-white/60' : 'bg-teal-500'
                                        }`}></div>
                                    </div>

                                    {/* Message Content */}
                                    <div className={`prose max-w-none text-base leading-relaxed ${
                                        msg.role === 'user' 
                                            ? 'prose-invert prose-headings:text-white prose-p:text-white prose-strong:text-white prose-a:text-teal-200' 
                                            : 'prose-gray prose-headings:text-gray-900 prose-p:text-gray-700'
                                    }`}>
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                    </div>

                                    {/* DSL Query */}
                                    {msg.dsl && (
                                        <div className="mt-6 p-5 bg-gray-900/10 backdrop-blur-sm border border-gray-300/30 rounded-2xl overflow-hidden group/dsl hover:bg-gray-900/20 transition-all">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center space-x-2">
                                                    <Shield className="w-4 h-4 text-teal-600 group-hover/dsl:rotate-12 transition-transform" />
                                                    <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">Query Details</span>
                                                </div>
                                                <button className="text-xs text-teal-600 hover:text-teal-700 font-medium">Copy</button>
                                            </div>
                                            <pre className="text-xs text-gray-600 overflow-x-auto whitespace-pre-wrap leading-relaxed font-mono">
                                                {JSON.stringify(msg.dsl, null, 2)}
                                            </pre>
                                        </div>
                                    )}

                                    {/* Metrics Visualization */}
                                    {msg.role === 'assistant' && msg.metrics && (
                                        <div className="mt-6">
                                            <Visualizer metrics={msg.metrics} />
                                        </div>
                                    )}
                                </div>

                                {/* Hover effect glow */}
                                <div className={`absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none ${
                                    msg.role === 'user'
                                        ? 'shadow-[0_0_40px_rgba(78,205,196,0.4)]'
                                        : 'shadow-[0_0_40px_rgba(78,205,196,0.2)]'
                                }`}></div>
                            </div>
                        </div>
                    ))}

                    {/* Loading State */}
                    {loading && (
                        <div className="w-full animate-scale-in">
                            <div className="group relative w-full p-8 bg-gradient-to-br from-gray-50 to-teal-50 border-2 border-teal-200 rounded-3xl shadow-lg hover:shadow-2xl transition-all">
                                <div className="flex items-center space-x-4">
                                    <div className="relative">
                                        <div className="absolute inset-0 bg-teal-500/30 blur-xl rounded-full animate-pulse"></div>
                                        <div className="relative w-12 h-12 rounded-full bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center">
                                            <Sparkles className="w-6 h-6 text-white animate-pulse" />
                                        </div>
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce delay-100"></div>
                                            <div className="w-2 h-2 bg-teal-600 rounded-full animate-bounce delay-200"></div>
                                        </div>
                                        <span className="text-sm font-semibold text-gray-700">AI is analyzing your query...</span>
                                        <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div className="h-full bg-gradient-to-r from-teal-500 to-teal-600 rounded-full animate-pulse" style={{width: '60%'}}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={scrollRef} />
                </div>

                {/* Input Area */}
                <div className="relative z-10 border-t border-gray-200/40 bg-white/70 backdrop-blur-xl p-6 lg:p-8 shadow-lg">
                    <div className="max-w-6xl mx-auto">
                        <div className="relative group">
                            {/* Animated gradient border effect */}
                            <div className="absolute -inset-1 bg-gradient-to-r from-teal-500 via-teal-400 to-teal-500 rounded-2xl opacity-0 group-hover:opacity-20 blur transition-all duration-500"></div>
                            
                            <div className="relative flex items-center space-x-3 bg-white/80 rounded-2xl p-2 border-2 border-gray-200/60 focus-within:border-teal-500 focus-within:shadow-lg transition-all">
                                <input
                                    type="text"
                                    className="flex-1 bg-transparent text-gray-900 px-6 py-4 rounded-xl focus:outline-none text-base placeholder:text-gray-400"
                                    placeholder="Ask me anything about your security logs..."
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                    disabled={loading}
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={loading || !input.trim()}
                                    className="group/btn relative overflow-hidden bg-gradient-to-br from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white px-8 py-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:transform-none"
                                >
                                    <div className="relative z-10 flex items-center space-x-2">
                                        <span className="font-semibold">Send</span>
                                        <Send className="w-5 h-5 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform" />
                                    </div>
                                    {/* Button shine effect */}
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover/btn:translate-x-[200%] transition-transform duration-700"></div>
                                </button>
                            </div>
                        </div>
                        <div className="flex items-center justify-center mt-4 space-x-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse-slow"></div>
                            <p className="text-xs text-gray-500">Powered by AI · Secure & Private</p>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
