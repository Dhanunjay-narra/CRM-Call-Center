'use client';

import React, { useState } from 'react';
import { 
  ShieldCheck, Users, Lock, Key, 
  CheckCircle2, Clock, UserCheck, ShieldAlert 
} from 'lucide-react';

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'roles' | 'audit'>('audit');

  const auditLogs = [
    {
      id: 'aud-1',
      actor: 'dhanunjay@callsphere.com (SUPER_ADMIN)',
      action: 'USER_ROLE_UPDATED',
      entity: 'User (sarah@callsphere.com)',
      diff: 'Role changed from AGENT -> SENIOR_AGENT',
      ip: '192.168.1.104',
      time: '10:45 AM Today'
    },
    {
      id: 'aud-2',
      actor: 'system-sla-engine',
      action: 'TICKET_SLA_AUTO_ESCALATED',
      entity: 'SupportTicket #TIK-94812',
      diff: 'SLAStatus marked BREACHED -> Reassigned to Support Manager',
      ip: '127.0.0.1',
      time: '09:30 AM Today'
    },
    {
      id: 'aud-3',
      actor: 'qa-supervisor@callsphere.com',
      action: 'QA_SCORECARD_PUBLISHED',
      entity: 'Scorecard (Standard 100-Point)',
      diff: 'Criteria updated: Compliance Section max_points: 15',
      ip: '192.168.1.112',
      time: 'Yesterday'
    }
  ];

  const roles = [
    { role: 'SUPER_ADMIN', desc: 'Full tenant system control, billing, database settings & audits' },
    { role: 'ORG_ADMIN', desc: 'Organization setup, team structures, departments, and user provisioning' },
    { role: 'CALL_CENTER_MANAGER', desc: 'Contact center management, routing queues, SLAs, and live telephony' },
    { role: 'SUPERVISOR', desc: 'Live agent monitoring, whisper coaching, call barge-in, QA scoring' },
    { role: 'QA_ANALYST', desc: 'Call recording evaluations, scorecards, and coaching sessions' },
    { role: 'SENIOR_AGENT', desc: 'High priority customer routing, outbound dialer, softphone' },
    { role: 'AGENT', desc: 'Standard softphone inbound/outbound calls, omnichannel inbox, timeline' },
    { role: 'SALES_REP', desc: 'Deals, pipelines, leads, campaigns, customer 360' },
    { role: 'SUPPORT_REP', desc: 'Tickets, SLA resolution, knowledge base guides' },
    { role: 'ANALYST', desc: 'Operational dashboards, KPI reports, analytics export' },
    { role: 'READ_ONLY_USER', desc: 'Read-only access for compliance audit inspection' }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Administration, Security &amp; Compliance</h2>
        <p className="text-xs text-slate-500 mt-0.5">11-tier Role-Based Access Control (RBAC), multi-tenant settings &amp; immutable audit trails</p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('audit')}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
            activeTab === 'audit' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Security Audit Logs
        </button>
        <button
          onClick={() => setActiveTab('roles')}
          className={`px-4 py-2 text-xs font-semibold rounded-xl transition ${
            activeTab === 'roles' ? 'bg-slate-900 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          11-Tier RBAC Roles
        </button>
      </div>

      {/* Tab 1: Immutable Security Audit Logs */}
      {activeTab === 'audit' && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs font-bold text-slate-700 uppercase tracking-wider">
            <span>Immutable Security Audit Log Stream</span>
            <span className="text-[10px] text-emerald-600 font-bold flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5" /> SOC2 / ISO 27001 Compliant
            </span>
          </div>

          {auditLogs.map((log) => (
            <div key={log.id} className="p-4 hover:bg-slate-50 transition space-y-1 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-slate-900 text-white rounded font-mono font-bold text-[10px]">
                    {log.action}
                  </span>
                  <span className="font-bold text-slate-900">{log.entity}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">{log.time}</span>
              </div>

              <p className="text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-100 font-mono text-[11px] mt-1">
                {log.diff}
              </p>

              <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                <span>Actor: {log.actor}</span>
                <span className="font-mono">IP: {log.ip}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: 11-Tier RBAC Role Matrix */}
      {activeTab === 'roles' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {roles.map((r, i) => (
            <div key={i} className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 font-mono text-xs">{r.role}</span>
                <span className="w-6 h-6 rounded-full bg-indigo-50 text-indigo-600 font-bold flex items-center justify-center text-[10px]">
                  {i + 1}
                </span>
              </div>
              <p className="text-slate-500 text-[11px]">{r.desc}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
