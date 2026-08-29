import React, { useState } from 'react';
import { Layers, Database, RefreshCw, Filter, ArrowUpRight } from 'lucide-react';

export interface DataPanelProps_171 {
  panelName?: string;
  rowCount?: number;
}

export const DataPanel_171: React.FC<DataPanelProps_171> = ({
  panelName = "Enterprise Pipeline Feed 171",
  rowCount = 12
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div className="p-4 bg-slate-50/50 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-slate-500" />
          <h5 className="text-xs font-bold text-slate-800">{panelName}</h5>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
      <div className="p-4 space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-600 py-1 border-b border-slate-50">
          <span>Active Data Streams</span>
          <span className="font-mono font-bold text-slate-900">{rowCount} Nodes</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-600 py-1 border-b border-slate-50">
          <span>Health Status</span>
          <span className="font-semibold text-emerald-600">Operational</span>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-600 py-1">
          <span>Sync Interval</span>
          <span className="font-mono text-slate-700">1000ms</span>
        </div>
      </div>
    </div>
  );
};
