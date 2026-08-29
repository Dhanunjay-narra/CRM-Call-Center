'use client';

import React, { useState, useEffect } from 'react';
import { 
  KanbanSquare, Plus, DollarSign, Building2, 
  Calendar, ArrowRight, CheckCircle2, TrendingUp 
} from 'lucide-react';
import { api } from '@/lib/api';

export default function DealsPage() {
  const [stages, setStages] = useState([
    { id: 'stg-1', name: 'Discovery', probability: 20, color: 'border-slate-300' },
    { id: 'stg-2', name: 'Qualification', probability: 40, color: 'border-blue-400' },
    { id: 'stg-3', name: 'Proposal Sent', probability: 60, color: 'border-indigo-400' },
    { id: 'stg-4', name: 'Negotiation', probability: 80, color: 'border-amber-400' },
    { id: 'stg-5', name: 'Closed Won', probability: 100, color: 'border-emerald-500' }
  ]);

  const [deals, setDeals] = useState<any[]>([
    { id: 'd-1', title: 'Enterprise Cloud Migration', customer_name: 'Acme Corp', amount: 65000, stage_id: 'stg-3', probability: 60 },
    { id: 'd-2', title: '50-Seat Softphone License', customer_name: 'Ravi Kumar Ltd', amount: 45000, stage_id: 'stg-4', probability: 80 },
    { id: 'd-3', title: 'Omnichannel WhatsApp Setup', customer_name: 'Apex Networks', amount: 20000, stage_id: 'stg-2', probability: 40 },
    { id: 'd-4', title: 'Global Contact Center Expansion', customer_name: 'Globex Health', amount: 150000, stage_id: 'stg-5', probability: 100 },
    { id: 'd-5', title: 'Custom IVR Flow Builder Integration', customer_name: 'FinTech Hub', amount: 35000, stage_id: 'stg-1', probability: 20 }
  ]);

  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newAmount, setNewAmount] = useState('30000');
  const [newStageId, setNewStageId] = useState('stg-1');

  const handleAddDeal = (e: React.FormEvent) => {
    e.preventDefault();
    const stage = stages.find((s) => s.id === newStageId);
    setDeals((prev) => [
      ...prev,
      {
        id: `d-${Date.now()}`,
        title: newTitle,
        customer_name: 'New Prospect',
        amount: parseFloat(newAmount) || 10000,
        stage_id: newStageId,
        probability: stage ? stage.probability : 20
      }
    ]);
    setIsAddModalOpen(false);
    setNewTitle('');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Sales Pipelines &amp; Opportunity Kanban</h2>
          <p className="text-xs text-slate-500 mt-0.5">Weighted revenue forecasting and stage velocity</p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" /> Create Deal
        </button>
      </div>

      {/* Kanban Board Columns */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 overflow-x-auto pb-4">
        {stages.map((stage) => {
          const stageDeals = deals.filter((d) => d.stage_id === stage.id);
          const stageTotal = stageDeals.reduce((sum, d) => sum + d.amount, 0);

          return (
            <div key={stage.id} className="bg-slate-100/70 p-3.5 rounded-2xl border border-slate-200/80 flex flex-col min-w-[220px]">
              {/* Column Header */}
              <div className="flex items-center justify-between mb-3 px-1">
                <div>
                  <h3 className="font-bold text-slate-900 text-xs">{stage.name}</h3>
                  <p className="text-[11px] font-mono text-slate-500 font-semibold">${stageTotal.toLocaleString()}</p>
                </div>
                <span className="px-2 py-0.5 bg-white border border-slate-200 rounded-full text-[10px] font-bold text-slate-600">
                  {stageDeals.length}
                </span>
              </div>

              {/* Deal Cards */}
              <div className="space-y-3 flex-1">
                {stageDeals.map((deal) => (
                  <div
                    key={deal.id}
                    className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm hover:shadow transition space-y-2 cursor-pointer"
                  >
                    <p className="font-bold text-slate-900 text-xs leading-tight">{deal.title}</p>
                    <p className="text-[11px] text-slate-500 flex items-center gap-1">
                      <Building2 className="h-3 w-3" /> {deal.customer_name}
                    </p>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                      <span className="font-bold text-slate-900 font-mono text-xs">
                        ${Number(deal.amount).toLocaleString()}
                      </span>
                      <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md text-[10px] font-bold">
                        {deal.probability}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Deal Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Create Opportunity Deal</h3>
            <form onSubmit={handleAddDeal} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Deal Title</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Enterprise 100-Seat Contact Center"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Deal Value ($)</label>
                <input
                  type="number"
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Pipeline Stage</label>
                <select
                  value={newStageId}
                  onChange={(e) => setNewStageId(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                >
                  {stages.map((s) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.probability}%)</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-xl font-semibold shadow-md shadow-indigo-600/30"
                >
                  Create Deal
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
