'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Building2, Phone, Mail, ArrowLeft, HeartPulse, 
  DollarSign, LifeBuoy, Clock, ShieldCheck, Plus 
} from 'lucide-react';
import { api } from '@/lib/api';
import CustomerTimeline from '@/components/timeline/CustomerTimeline';
import { useCallStore } from '@/stores/useCallStore';

export default function Customer360DetailPage({ params }: { params: { id: string } }) {
  const [customerData, setCustomerData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const { setActiveCall } = useCallStore();

  useEffect(() => {
    async function loadC360() {
      try {
        const data = await api.getCustomer360(params.id);
        setCustomerData(data);
      } catch (err) {
        // Mock fallback if offline
        setCustomerData({
          customer: {
            id: params.id,
            name: 'Ravi Kumar (Enterprise Account)',
            email: 'ravi.kumar@enterprise.com',
            phone_number: '+91 98765 43210',
            health_score: 94,
            sentiment: 'POSITIVE',
            lifetime_value: 45000,
            preferred_channel: 'WHATSAPP'
          },
          contacts: [
            { id: 'c-1', full_name: 'Ravi Kumar', job_title: 'Chief Technology Officer', phone_number: '+91 98765 43210', email: 'ravi@enterprise.com', is_primary: true }
          ],
          opportunities: [
            { id: 'opp-1', title: 'Enterprise Contact Center 3-Year Contract', amount: 45000, status: 'OPEN', probability: 80 }
          ],
          tickets: [
            { id: 'tik-1', ticket_number: 'TIK-4891', title: 'SIP Trunking Codec Optimization', priority: 'MEDIUM', status: 'RESOLVED' }
          ],
          timeline: [
            {
              id: 't-1',
              channel: 'WHATSAPP',
              event_type: 'MessageReceived',
              title: 'WhatsApp Message from Ravi',
              description: 'Requested contract amendment for 50 additional softphone seats.',
              actor_name: 'Ravi Kumar',
              occurred_at: new Date(Date.now() - 7200000).toISOString(),
              metadata_json: {}
            },
            {
              id: 't-2',
              channel: 'CALL',
              event_type: 'CallCompleted',
              title: 'Quarterly Business Review Call',
              description: 'Discussed high volume outbound dialer capacity. AHT: 420s.',
              actor_name: 'Dhanunjay Narra',
              occurred_at: new Date(Date.now() - 86400000).toISOString(),
              metadata_json: { recording_url: 'https://cdn.callsphere.com/rec/call_9012.wav' }
            }
          ]
        });
      } finally {
        setLoading(false);
      }
    }
    loadC360();
  }, [params.id]);

  if (!customerData) return null;
  const { customer, contacts, opportunities, tickets, timeline } = customerData;

  const handleCallCustomer = () => {
    setActiveCall({
      activeCallId: `call-${Date.now()}`,
      callStatus: 'IN_PROGRESS',
      toNumber: customer.phone_number,
      callerName: customer.name,
      customerId: customer.id
    });
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Back Link & Header */}
      <div className="flex items-center gap-3">
        <Link href="/customers" className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition">
          <ArrowLeft className="h-4 w-4 text-slate-600" />
        </Link>
        <div>
          <h2 className="text-xl font-bold text-slate-900">{customer.name}</h2>
          <p className="text-xs text-slate-500 font-mono">{customer.phone_number} • {customer.email}</p>
        </div>
      </div>

      {/* Customer 360 Header Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <span className="text-xs text-slate-500 font-medium">Customer Health Score</span>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-2xl font-black text-emerald-600">{customer.health_score}/100</span>
            <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded-full text-[10px] font-bold">Excellent</span>
          </div>
        </div>

        <div>
          <span className="text-xs text-slate-500 font-medium">Customer Lifetime Value (LTV)</span>
          <p className="text-2xl font-black text-slate-900 mt-1 font-mono">${Number(customer.lifetime_value || 0).toLocaleString()}</p>
        </div>

        <div>
          <span className="text-xs text-slate-500 font-medium">Preferred Communication</span>
          <span className="inline-block mt-1 px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs font-bold uppercase">
            {customer.preferred_channel || 'WHATSAPP'}
          </span>
        </div>

        <div className="flex items-center justify-end">
          <button
            onClick={handleCallCustomer}
            className="w-full sm:w-auto px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition"
          >
            <Phone className="h-4 w-4" /> Call via Softphone
          </button>
        </div>
      </div>

      {/* 2-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Contacts, Deals, Tickets (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Associated Contacts */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Stakeholder Contacts</h3>
            <div className="space-y-2">
              {contacts?.map((c: any) => (
                <div key={c.id} className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <p className="font-bold text-slate-900">{c.full_name}</p>
                    {c.is_primary && <span className="text-[10px] text-indigo-600 font-bold">Primary</span>}
                  </div>
                  <p className="text-[11px] text-slate-500">{c.job_title || 'Contact'}</p>
                  <p className="text-[11px] text-slate-600 font-mono">{c.phone_number}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Active Deals / Opportunities */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Active Deals</h3>
            <div className="space-y-2">
              {opportunities?.map((o: any) => (
                <div key={o.id} className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-xl space-y-1 text-xs">
                  <p className="font-bold text-slate-900">{o.title}</p>
                  <div className="flex justify-between font-mono">
                    <span className="font-bold text-indigo-900">${Number(o.amount).toLocaleString()}</span>
                    <span className="text-slate-500 font-semibold">{o.probability}% Probability</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side: Interactive Customer 360 Chronological Timeline (8 cols) */}
        <div className="lg:col-span-8 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Customer 360 Chronological Timeline</h3>
            <p className="text-xs text-slate-500 mt-0.5">Every call, WhatsApp message, email, deal event, and support ticket in unified order</p>
          </div>

          <CustomerTimeline events={timeline || []} />
        </div>
      </div>
    </div>
  );
}
