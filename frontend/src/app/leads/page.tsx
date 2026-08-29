'use client';

import React, { useState, useEffect } from 'react';
import { 
  Users, Plus, Search, Filter, Phone, Mail, 
  ArrowRight, CheckCircle2, TrendingUp, Sparkles 
} from 'lucide-react';
import { api } from '@/lib/api';
import { useCallStore } from '@/stores/useCallStore';

export default function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newFirstName, setNewFirstName] = useState('');
  const [newLastName, setNewLastName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newEstimatedValue, setNewEstimatedValue] = useState('25000');

  const { setActiveCall } = useCallStore();

  const loadLeads = async () => {
    try {
      const data = await api.listLeads();
      if (data && data.length > 0) {
        setLeads(data);
      } else {
        // Mock fallback leads if empty
        setLeads([
          {
            id: 'l-1',
            first_name: 'Amitabh',
            last_name: 'Sen',
            company_name: 'Sen Logistics Global',
            email: 'amitabh@senlogistics.com',
            phone_number: '+91 98765 11223',
            score: 88,
            estimated_value: 45000,
            status: 'QUALIFIED'
          },
          {
            id: 'l-2',
            first_name: 'Jessica',
            last_name: 'Alba',
            company_name: 'Honest Tech Labs',
            email: 'jessica@honesttech.com',
            phone_number: '+1 555 019 998',
            score: 76,
            estimated_value: 30000,
            status: 'CONTACTED'
          },
          {
            id: 'l-3',
            first_name: 'Carlos',
            last_name: 'Mendez',
            company_name: 'Mendez Manufacturing',
            email: 'carlos@mendezmfg.com',
            phone_number: '+52 55 1234 5678',
            score: 42,
            estimated_value: 15000,
            status: 'NEW'
          }
        ]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createLead({
        first_name: newFirstName,
        last_name: newLastName,
        email: newEmail,
        phone_number: newPhone,
        company_name: newCompany,
        estimated_value: parseFloat(newEstimatedValue) || 10000
      });
      setIsCreateModalOpen(false);
      setNewFirstName('');
      setNewLastName('');
      setNewEmail('');
      setNewPhone('');
      setNewCompany('');
      loadLeads();
    } catch (err) {
      console.error(err);
    }
  };

  const handleCallLead = (lead: any) => {
    setActiveCall({
      activeCallId: `call-${Date.now()}`,
      callStatus: 'IN_PROGRESS',
      toNumber: lead.phone_number,
      callerName: `${lead.first_name} ${lead.last_name || ''}`
    });
  };

  const filteredLeads = leads.filter((l) =>
    `${l.first_name} ${l.last_name} ${l.company_name} ${l.email}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Lead Pipeline &amp; Predictive Scoring</h2>
          <p className="text-xs text-slate-500 mt-0.5">Automated demographic &amp; behavioral lead qualification engine</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition self-start sm:self-auto"
        >
          <Plus className="h-4 w-4" /> Add New Lead
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search leads by name, email, or company..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-6 py-3">Lead / Company</th>
                <th className="px-6 py-3">AI Lead Score</th>
                <th className="px-6 py-3">Deal Potential</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3 text-right">Quick Contact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filteredLeads.map((lead) => (
                <tr key={lead.id} className="hover:bg-slate-50/80 transition">
                  <td className="px-6 py-4">
                    <p className="font-bold text-slate-900">{lead.first_name} {lead.last_name || ''}</p>
                    <p className="text-[11px] text-slate-500">{lead.company_name || 'Individual'}</p>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-[11px] font-black ${
                        lead.score >= 75
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : lead.score >= 50
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {lead.score}/100
                      </span>
                      {lead.score >= 75 && <span className="text-[10px] text-emerald-600 font-bold uppercase">Hot Lead</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 font-bold text-slate-900 font-mono">
                    ${Number(lead.estimated_value || 0).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-lg text-[10px] font-bold uppercase">
                      {lead.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleCallLead(lead)}
                        className="p-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 rounded-lg transition"
                        title="Direct Click-to-Call Softphone"
                      >
                        <Phone className="h-3.5 w-3.5" />
                      </button>
                      <a
                        href={`mailto:${lead.email}`}
                        className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg transition"
                        title="Send Email"
                      >
                        <Mail className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Lead Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-slate-900">Add New Prospect Lead</h3>
            <form onSubmit={handleCreateLead} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">First Name</label>
                  <input
                    required
                    type="text"
                    value={newFirstName}
                    onChange={(e) => setNewFirstName(e.target.value)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Last Name</label>
                  <input
                    type="text"
                    value={newLastName}
                    onChange={(e) => setNewLastName(e.target.value)}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Company</label>
                <input
                  type="text"
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Email</label>
                <input
                  required
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Phone Number</label>
                <input
                  type="tel"
                  placeholder="+1 800 555 0199"
                  value={newPhone}
                  onChange={(e) => setNewPhone(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-200 rounded-xl"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Estimated Deal Value ($)</label>
                <input
                  type="number"
                  value={newEstimatedValue}
                  onChange={(e) => setNewEstimatedValue(e.target.value)}
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
                  Create Lead
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
