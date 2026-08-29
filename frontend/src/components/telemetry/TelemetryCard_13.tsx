import React, { useState } from 'react';
import { Activity, Zap, CheckCircle2, TrendingUp, BarChart2 } from 'lucide-react';

export interface TelemetryCardProps_13 {
  title?: string;
  initialValue?: number;
}

export const TelemetryCard_13: React.FC<TelemetryCardProps_13> = ({
  title = "Telemetry Stream Node 13",
  initialValue = 88
}) => {
  const [val, setVal] = useState(initialValue);

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
            <Activity className="h-4 w-4" />
          </div>
          <span className="text-xs font-bold text-slate-800">{title}</span>
        </div>
        <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold">ONLINE</span>
      </div>
      <div className="flex items-baseline justify-between">
        <p className="text-2xl font-black font-mono text-slate-900">{val}%</p>
        <span className="text-xs text-slate-500 font-medium">Throughput</span>
      </div>
      <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
        <div className="bg-indigo-600 h-full rounded-full transition-all duration-300" style={{ width: `${val}%` }} />
      </div>
    </div>
  );
};
