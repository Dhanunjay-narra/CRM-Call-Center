'use client';

import React, { useState, useEffect } from 'react';
import { 
  LifeBuoy, Plus, Search, AlertTriangle, CheckCircle2, 
  Clock, ShieldAlert, User, Check 
} from 'lucide-react';
import { api } from '@/lib/api';
import { TicketPriority, TicketStatus } from '@/lib/types';

export default function SupportTicketsPage() {
  const [tickets, setTickets] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newCategory, setNewCategory] = useState('Technical Support');
  const [newPriority, setNewPriority] = useState<TicketPriority>('MEDIUM');

  const loadTickets = async () => {
    try {
      const data = await api.listTickets();
      if (data && data.length > 0) {
        setTickets(data);
      } else {
        setTickets([
          {
            id: 'tik-1',
            ticket_number: 'TIK-94812',
            title: 'Critical Outage: VoIP Trunk Gateway Connection Timeout',
            category: 'Infrastructure',
            priority: 'CRITICAL',
            status: 'IN_PROGRESS',
            sla_status: 'WARNING_80_PERCENT',
            created_at: new Date(Date.now() - 3600000).toISOString()
          },
          {
            id: 'tik-2',
            ticket_number: 'TIK-94808',
            title: 'Request for WhatsApp Business API Template Approval',
            category: 'Account Access',
            priority: 'MEDIUM',
            status: 'NEW',
            sla_status: 'WITHIN_SLA',
            created_at: new Date(Date.now() - 7200000).toISOString()
          },
          {
            id: 'tik-3',
            ticket_number: 'TIK-94792',
            title: 'Custom CRM Webhook Retries After Network Hiccup',
            category: 'Technical Support',
            priority: 'HIGH',
            status: 'RESOLVED',
            sla_status: 'WITHIN_SLA',
            created_at: new Date(Date.now() - 86400000).toISOString()
          }
        ]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createTicket({
        title: newTitle,
        description: newDescription,
        category: newCategory,
        priority: newPriority
      });
      setIsCreateModalOpen(false);
      setNewTitle('');
      setNewDescription('');
      loadTickets();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredTickets = tickets.filter((t) => {
    const matchesSearch = `${t.ticket_number} ${t.title} ${t.category}`.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || t.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getPriorityBadge = (pri: TicketPriority) => {
    switch (pri) {
      case 'CRITICAL': return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'HIGH': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'MEDIUM': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getSLABadge = (sla: string) => {
    switch (sla) {
      case 'BREACHED':
        return <span className="px-2 py-0.5 bg-rose-100 text-rose-800 rounded-md font-bold text-[10px] flex items-center gap-1"><ShieldAlert className="h-3 w-3" /> SLA Breached</span>;
      case 'WARNING_80_PERCENT':
        return <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded-md font-bold text-[10px] flex items-center gap-1"><AlertTriangle className="h-3 w-3" /> 80% SLA Warning</span>;
      default:
        return <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-md font-bold text-[10px] flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> Within SLA</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Support Ticketing &amp; SLA Management</h2>
          <p className="text-xs text-slate-500 mt-0.5">Automated First Response &amp; Resolution SLA tracking with supervisor escalation</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" /> Create Support Ticket
        </button>
      </div>

      {/* Filter Tabs & Search */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-1 overflow-x-auto pb-1">
          {['ALL', 'NEW', 'IN_PROGRESS', 'RESOLVED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition ${
                statusFilter === st ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search ticket # or subject..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Tickets List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden divide-y divide-slate-100">
        {filteredTickets.map((ticket) => (
          <div key={ticket.id} className="p-5 hover:bg-slate-50 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="font-mono font-bold text-xs text-indigo-600">{ticket.ticket_number}</span>
                <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold border uppercase ${getPriorityBadge(ticket.priority)}`}>
                  {ticket.priority}
                </span>
                <span className="text-[11px] text-slate-400">• {ticket.category}</span>
              </div>
              <h4 className="font-bold text-slate-900 text-sm">{ticket.title}</h4>
            </div>

            <div className="flex items-center gap-4 shrink-0">
              {getSLABadge(ticket.sla_status)}
              <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold uppercase">
                {ticket.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Create Ticket Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">New Support Ticket</h3>
            <form onSubmit={handleCreateTicket} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Subject / Issue Title</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Inbound call drop on mobile softphone"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as any)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                >
                  <option value="CRITICAL">CRITICAL (15m Response / 2h Resolution)</option>
                  <option value="HIGH">HIGH (30m Response / 4h Resolution)</option>
                  <option value="MEDIUM">MEDIUM (60m Response / 8h Resolution)</option>
                  <option value="LOW">LOW (120m Response / 24h Resolution)</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Issue Description</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Detailed symptoms, affected extensions..."
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-xl font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-xl font-semibold shadow-md shadow-indigo-600/30"
                >
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
