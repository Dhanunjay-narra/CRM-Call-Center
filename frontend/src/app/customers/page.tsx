'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Building2, Search, Plus, Phone, Mail, 
  ArrowRight, ShieldCheck, HeartPulse, Sparkles 
} from 'lucide-react';
import { api } from '@/lib/api';

export default function CustomersPage() {
  const [customers, setCustomers] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const loadCustomers = async () => {
    try {
      const data = await api.listCustomers();
      if (data && data.length > 0) {
        setCustomers(data);
      } else {
        setCustomers([
          {
            id: 'cust-1',
            name: 'Ravi Kumar',
            email: 'ravi.kumar@enterprise.com',
            phone_number: '+91 98765 43210',
            health_score: 94,
            sentiment: 'POSITIVE',
            lifetime_value: 45000,
            open_opportunities_count: 1,
            open_tickets_count: 0
          },
          {
            id: 'cust-2',
            name: 'Acme Manufacturing Corp',
            email: 'procurement@acmemfg.com',
            phone_number: '+1 800 555 1199',
            health_score: 72,
            sentiment: 'NEUTRAL',
            lifetime_value: 120000,
            open_opportunities_count: 2,
            open_tickets_count: 1
          },
          {
            id: 'cust-3',
            name: 'Globex Health Group',
            email: 'admin@globexhealth.org',
            phone_number: '+44 20 7946 0912',
            health_score: 88,
            sentiment: 'POSITIVE',
            lifetime_value: 85000,
            open_opportunities_count: 0,
            open_tickets_count: 0
          }
        ]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, []);

  const filteredCustomers = customers.filter((c) =>
    `${c.name} ${c.email} ${c.phone_number}`
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Customer 360 Accounts</h2>
          <p className="text-xs text-slate-500 mt-0.5">Comprehensive relationship timeline, health telemetry &amp; lifetime value</p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search accounts by name, email, or phone..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Customer Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCustomers.map((cust) => (
          <div key={cust.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition space-y-4 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 font-bold flex items-center justify-center text-xs">
                    <Building2 className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{cust.name}</h4>
                    <p className="text-[11px] text-slate-500 font-mono">{cust.phone_number || cust.email}</p>
                  </div>
                </div>

                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                  cust.health_score >= 80
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                }`}>
                  Health: {cust.health_score}%
                </span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl grid grid-cols-3 gap-2 text-center text-xs">
                <div>
                  <p className="text-[10px] text-slate-500">LTV</p>
                  <p className="font-bold text-slate-900 font-mono mt-0.5">${Number(cust.lifetime_value || 0).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-500">Deals</p>
                  <p className="font-bold text-indigo-600 mt-0.5">{cust.open_opportunities_count || 0}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-500">Tickets</p>
                  <p className="font-bold text-slate-900 mt-0.5">{cust.open_tickets_count || 0}</p>
                </div>
              </div>
            </div>

            <Link
              href={`/customers/${cust.id}`}
              className="w-full py-2 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 font-semibold rounded-xl text-xs flex items-center justify-center gap-1 transition"
            >
              <span>View Customer 360 Profile</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
