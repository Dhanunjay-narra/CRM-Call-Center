'use client';

import React, { useState } from 'react';
import { 
  Award, Plus, CheckCircle2, XCircle, 
  HelpCircle, User, Phone, Sparkles 
} from 'lucide-react';

export default function QAPage() {
  const [evaluations, setEvaluations] = useState([
    {
      id: 'eval-1',
      agent_name: 'Sarah Connor',
      call_id: 'CALL-89412',
      score: 94.0,
      passed: true,
      evaluator: 'Dhanunjay (QA Lead)',
      coaching_required: false,
      notes: 'Excellent active listening, empathy, and complete identity verification.'
    },
    {
      id: 'eval-2',
      agent_name: 'Alex Mercer',
      call_id: 'CALL-89304',
      score: 72.0,
      passed: false,
      evaluator: 'QA Analyst',
      coaching_required: true,
      notes: 'Missed mandatory compliance disclosure. Scheduled coaching on privacy regulations.'
    }
  ]);

  const scorecardSections = [
    { name: 'Greeting & Caller Verification', weight: 20, desc: 'Professional greeting and verification' },
    { name: 'Communication & Empathy', weight: 15, desc: 'Active listening and helpful tone' },
    { name: 'Product Knowledge', weight: 15, desc: 'Accurate technical and pricing details' },
    { name: 'Problem Resolution & FCR', weight: 20, desc: 'Effective troubleshooting steps' },
    { name: 'Compliance & Security', weight: 15, desc: 'Mandatory disclosures and data privacy' },
    { name: 'Closing & Survey Mention', weight: 15, desc: 'Recap and polite survey invitation' }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Quality Assurance &amp; Agent Coaching</h2>
          <p className="text-xs text-slate-500 mt-0.5">100-point call evaluation scorecards, section criteria &amp; supervisor coaching plans</p>
        </div>
      </div>

      {/* 2-Column QA Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: 100-Point Scorecard Criteria (5 cols) */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Standard 100-Point Scorecard</h3>
            <span className="px-2.5 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-bold">Pass: &ge; 80%</span>
          </div>

          <div className="space-y-3 pt-2">
            {scorecardSections.map((sec, idx) => (
              <div key={idx} className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-slate-900">{sec.name}</p>
                  <p className="text-[11px] text-slate-500">{sec.desc}</p>
                </div>
                <span className="font-mono font-bold text-indigo-600 px-2 py-1 bg-white border border-slate-200 rounded-lg">
                  {sec.weight} pts
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Completed Call Evaluations (7 cols) */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Recent Call Evaluations</h3>

          <div className="space-y-3">
            {evaluations.map((ev) => (
              <div key={ev.id} className="p-4 bg-slate-50/50 border border-slate-200 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 text-sm">{ev.agent_name}</span>
                    <span className="text-[11px] text-slate-500 font-mono">({ev.call_id})</span>
                  </div>

                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase flex items-center gap-1 ${
                    ev.passed
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}>
                    {ev.passed ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    Score: {ev.score}%
                  </span>
                </div>

                <p className="text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200 text-[11px]">
                  {ev.notes}
                </p>

                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                  <span>Evaluated by: {ev.evaluator}</span>
                  {ev.coaching_required && (
                    <span className="text-amber-600 font-bold uppercase">Coaching Assigned</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
