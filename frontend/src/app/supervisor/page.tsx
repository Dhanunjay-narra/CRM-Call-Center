'use client';

import React, { useState } from 'react';
import { 
  Activity, Users, PhoneCall, Volume2, Mic, UserCheck, 
  ShieldAlert, AlertTriangle, Clock, TrendingUp, CheckCircle2 
} from 'lucide-react';

interface AgentCard {
  id: string;
  name: string;
  role: string;
  state: 'AVAILABLE' | 'ON_CALL' | 'BREAK' | 'AFTER_CALL_WORK';
  breakType?: string;
  currentCallDuration: string;
  customerName?: string;
  customerPhone?: string;
  queue: string;
  occupancy: number;
}

export default function SupervisorLivePage() {
  const [activeSupervisorAction, setActiveSupervisorAction] = useState<string | null>(null);

  const liveAgents: AgentCard[] = [
    {
      id: 'ag-1',
      name: 'Sarah Connor',
      role: 'Senior Sales Agent',
      state: 'ON_CALL',
      currentCallDuration: '04:12',
      customerName: 'Acme Corp (Ravi K.)',
      customerPhone: '+1 555 019 876',
      queue: 'VIP Sales Queue',
      occupancy: 86
    },
    {
      id: 'ag-2',
      name: 'Alex Mercer',
      role: 'Support Engineer',
      state: 'ON_CALL',
      currentCallDuration: '02:45',
      customerName: 'Apex Networks',
      customerPhone: '+1 555 014 332',
      queue: 'Tier 2 Support',
      occupancy: 79
    },
    {
      id: 'ag-3',
      name: 'Elena Rostova',
      role: 'Customer Success',
      state: 'AVAILABLE',
      currentCallDuration: '00:00',
      queue: 'General Inquiries',
      occupancy: 72
    },
    {
      id: 'ag-4',
      name: 'Marcus Vance',
      role: 'Support Specialist',
      state: 'BREAK',
      breakType: 'LUNCH',
      currentCallDuration: '18:30',
      queue: 'Billing Support',
      occupancy: 68
    },
    {
      id: 'ag-5',
      name: 'Priya Patel',
      role: 'Sales Representative',
      state: 'AVAILABLE',
      currentCallDuration: '00:00',
      queue: 'Inbound Sales',
      occupancy: 81
    },
    {
      id: 'ag-6',
      name: 'David Kim',
      role: 'Technical Lead',
      state: 'AFTER_CALL_WORK',
      currentCallDuration: '00:45',
      queue: 'Tier 2 Support',
      occupancy: 88
    }
  ];

  const handleAction = (type: string, agentName: string) => {
    setActiveSupervisorAction(`${type} active on ${agentName}`);
    setTimeout(() => setActiveSupervisorAction(null), 4000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900">Supervisor Command Center</h2>
            <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-[11px] font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" /> Real-Time Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Live agent monitoring, whisper coaching, call barge-in &amp; queue depth alarms</p>
        </div>

        {/* Live Active Action Toast */}
        {activeSupervisorAction && (
          <div className="px-4 py-2 bg-indigo-900 text-white rounded-xl shadow-lg text-xs font-semibold flex items-center gap-2 animate-bounce">
            <Volume2 className="h-4 w-4 text-indigo-400" />
            <span>{activeSupervisorAction}</span>
          </div>
        )}
      </div>

      {/* Queue Alarms & SLA Alert Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">VIP Sales Queue</p>
            <p className="text-xl font-bold text-slate-900 mt-0.5">2 Waiting • Max 00:14</p>
          </div>
          <span className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl font-bold text-xs">Healthy</span>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Tier 2 Support Queue</p>
            <p className="text-xl font-bold text-slate-900 mt-0.5">3 Waiting • Max 01:20</p>
          </div>
          <span className="p-2.5 bg-amber-50 text-amber-600 rounded-xl font-bold text-xs">Warning</span>
        </div>

        <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Average Speed of Answer (ASA)</p>
            <p className="text-xl font-bold text-slate-900 mt-0.5">8.2 Seconds</p>
          </div>
          <span className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl font-bold text-xs">&le; 20s SLA</span>
        </div>
      </div>

      {/* Live Agent Grid */}
      <div>
        <h3 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-3">Live Agents Telemetry ({liveAgents.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {liveAgents.map((ag) => (
            <div key={ag.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 hover:shadow-md transition">
              {/* Top Agent Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-100 text-slate-700 font-bold flex items-center justify-center text-xs">
                    {ag.name.split(' ').map((n) => n[0]).join('')}
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{ag.name}</h4>
                    <p className="text-[11px] text-slate-500">{ag.role}</p>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase ${
                  ag.state === 'ON_CALL'
                    ? 'bg-rose-50 text-rose-600 border border-rose-200'
                    : ag.state === 'AVAILABLE'
                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  {ag.state} {ag.breakType ? `(${ag.breakType})` : ''}
                </span>
              </div>

              {/* Call Details if On Call */}
              {ag.state === 'ON_CALL' ? (
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Connected Customer:</span>
                    <span className="font-semibold text-slate-900">{ag.customerName}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Call Duration:</span>
                    <span className="font-mono font-bold text-rose-600 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {ag.currentCallDuration}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Queue:</span>
                    <span className="text-indigo-600 font-medium">{ag.queue}</span>
                  </div>
                </div>
              ) : (
                <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs text-slate-500 flex justify-between">
                  <span>Assigned Queue:</span>
                  <span className="font-medium text-slate-700">{ag.queue}</span>
                </div>
              )}

              {/* Supervisor Telephony Intercept Actions */}
              {ag.state === 'ON_CALL' && (
                <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100">
                  <button
                    onClick={() => handleAction('Silent Monitoring', ag.name)}
                    className="p-2 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 rounded-xl text-[11px] font-semibold text-slate-700 flex flex-col items-center gap-1 transition"
                  >
                    <Volume2 className="h-3.5 w-3.5" />
                    <span>Listen</span>
                  </button>
                  <button
                    onClick={() => handleAction('Whisper Coaching', ag.name)}
                    className="p-2 bg-slate-100 hover:bg-amber-50 hover:text-amber-700 rounded-xl text-[11px] font-semibold text-slate-700 flex flex-col items-center gap-1 transition"
                  >
                    <Mic className="h-3.5 w-3.5" />
                    <span>Whisper</span>
                  </button>
                  <button
                    onClick={() => handleAction('Call Barge-In', ag.name)}
                    className="p-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl text-[11px] font-bold flex flex-col items-center gap-1 transition"
                  >
                    <Users className="h-3.5 w-3.5" />
                    <span>Barge</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
