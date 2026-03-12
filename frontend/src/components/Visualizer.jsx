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
import { TrendingUp, PieChart as PieChartIcon } from 'lucide-react';

const COLORS = ['#4ECDC4', '#7ED8CF', '#10b981', '#f59e0b', '#ef4444', '#D4F5ED'];

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white border border-gray-200 p-3 rounded-xl shadow-lg">
                <p className="text-xs text-gray-600 mb-1">{label || payload[0].name}</p>
                <p className="text-lg font-bold text-gray-900">{payload[0].value.toLocaleString()}</p>
            </div>
        );
    }
    return null;
};

export default function Visualizer({ metrics, queryIntent }) {
    const [isReady, setIsReady] = React.useState(false);

    React.useEffect(() => {
        // Small delay to ensure DOM is ready for chart rendering
        const timer = setTimeout(() => setIsReady(true), 100);
        return () => clearTimeout(timer);
    }, []);

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
        <div className="space-y-6 mt-6">
            {/* Metric Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(metrics).map(([key, value], idx) => (
                    <div key={idx} className="group relative overflow-hidden bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 hover:border-teal-400 p-5 rounded-2xl hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 animate-fade-in cursor-pointer">
                        {/* Animated background gradient on hover */}
                        <div className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-teal-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        
                        <div className="relative z-10">
                            <span className="block text-xs text-gray-500 mb-3 capitalize font-medium group-hover:text-teal-600 transition-colors">
                                {key.replace(/_/g, ' ')}
                            </span>
                            <span className={`text-3xl font-bold transform group-hover:scale-110 inline-block transition-transform ${
                                (key.toLowerCase().includes('high') || 
                                 key.toLowerCase().includes('critical') || 
                                 key.toLowerCase().includes('failed') || 
                                 key.toLowerCase().includes('error'))
                                    ? 'text-red-600' 
                                    : 'text-gray-900'
                            }`}>
                                {typeof value === 'number' ? value.toLocaleString() : String(value)}
                            </span>
                        </div>
                        
                        {/* Decorative corner accent */}
                        <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-teal-500/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    </div>
                ))}
            </div>

            {/* Charts */}
            {isComparative && isReady && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Pie Chart */}
                    <div className="group relative overflow-hidden bg-white border-2 border-gray-200 hover:border-teal-300 p-6 rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 animate-scale-in">
                        {/* Background decoration */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-teal-500/5 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        
                        <div className="relative z-10">
                            <div className="flex items-center space-x-3 mb-6">
                                <div className="p-2 bg-teal-500 rounded-lg shadow-lg group-hover:scale-110 transition-transform">
                                    <PieChartIcon className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h4 className="text-base font-bold text-gray-900">Distribution</h4>
                                    <p className="text-xs text-gray-500">Data breakdown analysis</p>
                                </div>
                            </div>
                            <div style={{ width: '100%', height: '280px', minHeight: '280px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={dataForCharts}
                                            innerRadius={60}
                                            outerRadius={90}
                                            paddingAngle={6}
                                            dataKey="value"
                                            animationBegin={0}
                                            animationDuration={1000}
                                        >
                                            {dataForCharts.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip content={<CustomTooltip />} />
                                        <Legend
                                            verticalAlign="bottom"
                                            height={36}
                                            iconType="circle"
                                            formatter={(value) => <span className="text-xs text-gray-600 font-medium">{value}</span>}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Bar Chart */}
                    <div className="group relative overflow-hidden bg-white border-2 border-gray-200 hover:border-teal-300 p-6 rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 animate-scale-in delay-100">
                        {/* Background decoration */}
                        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-teal-500/5 to-transparent rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        
                        <div className="relative z-10">
                            <div className="flex items-center space-x-3 mb-6">
                                <div className="p-2 bg-teal-600 rounded-lg shadow-lg group-hover:scale-110 transition-transform">
                                    <TrendingUp className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h4 className="text-base font-bold text-gray-900">Volume Analysis</h4>
                                    <p className="text-xs text-gray-500">Comparative metrics view</p>
                                </div>
                            </div>
                            <div style={{ width: '100%', height: '280px', minHeight: '280px' }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={dataForCharts} margin={{ top: 10, right: 10, left: -20, bottom: 10 }}>
                                        <defs>
                                            <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="#4ECDC4" stopOpacity={0.9} />
                                                <stop offset="100%" stopColor="#7ED8CF" stopOpacity={0.6} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                        <XAxis
                                            dataKey="name"
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
                                        />
                                        <YAxis
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 11, fill: '#6b7280', fontWeight: 500 }}
                                        />
                                        <Tooltip cursor={{ fill: 'rgba(78, 205, 196, 0.1)' }} content={<CustomTooltip />} />
                                        <Bar
                                            dataKey="value"
                                            fill="url(#colorBar)"
                                            radius={[10, 10, 0, 0]}
                                            animationBegin={0}
                                            animationDuration={1000}
                                        />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
