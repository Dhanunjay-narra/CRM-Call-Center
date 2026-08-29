'use client';

import React, { useState } from 'react';
import { 
  GitFork, Plus, Play, Sparkles, CheckCircle2, 
  ArrowRight, ShieldCheck, Mail, MessageSquare, Phone 
} from 'lucide-react';

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([
    {
      id: 'wf-1',
      name: 'Hot Lead Instant Task & Supervisor Notification',
      trigger: 'LeadCreated',
      condition: 'score > 70',
      actions: ['CREATE_TASK: Immediate VIP Call Required', 'NOTIFY_SUPERVISOR: High score lead entered'],
      executions: 142,
      is_active: true
    },
    {
      id: 'wf-2',
      name: 'Negative CSAT Immediate Alert & Follow-Up Task',
      trigger: 'FeedbackSubmitted',
      condition: 'score <= 2',
      actions: ['CREATE_TASK: Customer Dissatisfaction Review', 'SEND_EMAIL: Apology & Senior Escalation'],
      executions: 28,
      is_active: true
    },
    {
      id: 'wf-3',
      name: 'Post-Call WhatsApp Quote Confirmation',
      trigger: 'CallCompleted',
      condition: "disposition == 'INTERESTED'",
      actions: ['SEND_WHATSAPP: Dynamic Quotation Template'],
      executions: 312,
      is_active: true
    }
  ]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Event-Driven Workflow Automation</h2>
          <p className="text-xs text-slate-500 mt-0.5">Visual Trigger &rarr; Condition &rarr; Action automated dispatch engine</p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition self-start sm:self-auto">
          <Plus className="h-4 w-4" /> Create Automation
        </button>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {workflows.map((wf) => (
          <div key={wf.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between hover:shadow-md transition">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl">
                  <GitFork className="h-5 w-5" />
                </div>
                <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-[10px] font-bold">
                  Active
                </span>
              </div>

              <h4 className="font-bold text-slate-900 text-sm leading-snug">{wf.name}</h4>

              {/* Trigger & Condition Box */}
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase text-indigo-600">Trigger:</span>
                  <span className="font-semibold text-slate-900 font-mono">{wf.trigger}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase text-amber-600">Condition:</span>
                  <span className="font-semibold text-slate-700 font-mono">{wf.condition}</span>
                </div>
              </div>

              {/* Actions List */}
              <div className="space-y-1.5 text-xs">
                <p className="text-[10px] font-bold uppercase text-slate-400">Actions:</p>
                {wf.actions.map((act, i) => (
                  <div key={i} className="flex items-center gap-2 text-slate-700">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    <span className="truncate">{act}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>{wf.executions} Runs Executed</span>
              <span className="text-indigo-600 font-semibold cursor-pointer hover:underline">View Logs &rarr;</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
