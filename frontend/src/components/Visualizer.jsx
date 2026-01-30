import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend
} from 'recharts';
import { Activity, AlertTriangle, ShieldCheck, Database } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-slate-950/95 border border-blue-500/30 p-4 rounded-2xl shadow-[0_0_30px_rgba(59,130,246,0.2)] backdrop-blur-xl">
                <p className="text-[9px] uppercase tracking-[0.2em] text-blue-400 font-black mb-1">{label || payload[0].name}</p>
                <p className="text-lg font-black text-white tracking-tighter">{payload[0].value.toLocaleString()}</p>
            </div>
        );
    }
    return null;
};

export default function Visualizer({ metrics, queryIntent }) {
    if (!metrics || Object.keys(metrics).length === 0) return null;

    // Transform metrics for different chart types
    const dataForCharts = Object.entries(metrics)
        .map(([key, value]) => ({
            name: key.replace(/_/g, ' '),
            value: typeof value === 'number' ? value : parseFloat(value)
        }))
        .filter(item => !isNaN(item.value));

    const isComparative = dataForCharts.length > 1;

    return (
        <div className="space-y-6 mt-8">
            {/* Metric Cards - Ultra Premium */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(metrics).map(([key, value], idx) => (
                    <div key={idx} className="relative group overflow-hidden glass border-white/5 p-5 rounded-[2rem] transition-all hover:border-blue-500/40 hover:shadow-[0_0_40px_rgba(59,130,246,0.1)]">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-all duration-700">
                            {idx % 2 === 0 ? <Activity className="w-10 h-10 text-blue-400" /> : <ShieldCheck className="w-10 h-10 text-purple-400" />}
                        </div>
                        <span className="block text-[9px] uppercase tracking-[0.3em] text-slate-500 font-black mb-3 group-hover:text-blue-400/70 transition-colors">
                            {key.replace(/_/g, ' ')}
                        </span>
                        <span className={cn(
                            "text-2xl font-black tracking-tighter break-words",
                            (key.toLowerCase().includes('high') || key.toLowerCase().includes('critical') || key.toLowerCase().includes('failed') || key.toLowerCase().includes('error'))
                                ? "text-red-500" : "text-white"
                        )}>
                            {typeof value === 'number' ? value.toLocaleString() : String(value)}
                        </span>
                    </div>
                ))}
            </div>

            {/* Charts Layout - Wide & Creative */}
            {isComparative && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="glass border-white/5 p-8 rounded-[2.5rem] h-[350px] relative group overflow-hidden">
                        <div className="absolute -top-24 -left-24 w-48 h-48 bg-blue-500/10 blur-[80px] rounded-full group-hover:bg-blue-500/20 transition-all duration-1000" />
                        <h4 className="relative z-10 text-[10px] font-black mb-8 text-slate-400 uppercase tracking-[0.4em] flex items-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mr-3 shadow-[0_0_10px_rgba(59,130,246,1)]" />
                            Impact_Distribution_Map
                        </h4>
                        <ResponsiveContainer width="100%" height="85%">
                            <PieChart>
                                <Pie
                                    data={dataForCharts}
                                    innerRadius={80}
                                    outerRadius={105}
                                    paddingAngle={10}
                                    dataKey="value"
                                    animationBegin={200}
                                    animationDuration={1500}
                                    stroke="none"
                                >
                                    {dataForCharts.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} className="outline-none" />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomTooltip />} />
                                <Legend
                                    verticalAlign="middle"
                                    align="right"
                                    layout="vertical"
                                    iconType="circle"
                                    formatter={(value) => <span className="text-[10px] text-slate-400 font-black uppercase tracking-widest ml-2">{value}</span>}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="glass border-white/5 p-8 rounded-[2.5rem] h-[350px] relative group overflow-hidden">
                        <div className="absolute -top-24 -right-24 w-48 h-48 bg-purple-500/10 blur-[80px] rounded-full group-hover:bg-purple-500/20 transition-all duration-1000" />
                        <h4 className="relative z-10 text-[10px] font-black mb-8 text-slate-400 uppercase tracking-[0.4em] flex items-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mr-3 shadow-[0_0_10px_rgba(168,85,247,1)]" />
                            Intelligence_Volume_Analysis
                        </h4>
                        <ResponsiveContainer width="100%" height="85%">
                            <BarChart data={dataForCharts} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="cyberGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.9} />
                                        <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fill: '#64748b', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em' }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fontSize: 9, fill: '#64748b', fontWeight: 800 }}
                                />
                                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.03)' }} content={<CustomTooltip />} />
                                <Bar
                                    dataKey="value"
                                    fill="url(#cyberGradient)"
                                    radius={[10, 10, 0, 0]}
                                    animationBegin={400}
                                    animationDuration={1500}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
}
