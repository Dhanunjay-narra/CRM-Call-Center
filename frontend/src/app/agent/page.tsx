'use client';

import React, { useState } from 'react';
import { 
  Phone, PhoneCall, PhoneOff, Mic, MicOff, Pause, Play, 
  MessageSquare, Mail, LifeBuoy, FileText, CheckCircle2, 
  User, ShieldCheck, Clock, Send, Sparkles, AlertCircle
} from 'lucide-react';
import { useCallStore } from '@/stores/useCallStore';
import { useAgentStore } from '@/stores/useAgentStore';
import CustomerTimeline from '@/components/timeline/CustomerTimeline';

export default function AgentWorkspacePage() {
  const [quickNotes, setQuickNotes] = useState('');
  const [activeTab, setActiveTab] = useState<'timeline' | 'script' | 'notes'>('timeline');
  const [quickMessageChannel, setQuickMessageChannel] = useState<'WHATSAPP' | 'SMS' | 'EMAIL'>('WHATSAPP');
  const [quickMessageText, setQuickMessageText] = useState('Hi Ravi, thank you for speaking with CallSphere today. Your quotation has been generated.');
  const [messageSentNotification, setMessageSentNotification] = useState(false);

  const { 
    activeCallId, callStatus, fromNumber, toNumber, callerName, 
    isOnHold, isMuted, callDurationSeconds,
    toggleHold, toggleMute, clearActiveCall, setActiveCall
  } = useCallStore();

  const { agentState, setAgentState } = useAgentStore();

  const sampleCustomer = {
    name: 'Ravi Kumar',
    email: 'ravi.kumar@enterprise.com',
    phone: '+91 98765 43210',
    company: 'Enterprise Solutions Ltd',
    healthScore: 92,
    sentiment: 'POSITIVE',
    ltv: '$45,000',
    plan: 'Enterprise CallSphere Tier',
  };

  const sampleTimeline = [
    {
      id: '1',
      channel: 'WHATSAPP',
      event_type: 'MessageReceived',
      title: 'WhatsApp Inquiry from Ravi',
      description: 'Inquired about enterprise SLA terms and custom CRM integrations.',
      actor_name: 'Ravi Kumar',
      occurred_at: new Date(Date.now() - 3600000).toISOString(),
      metadata_json: {}
    },
    {
      id: '2',
      channel: 'CALL',
      event_type: 'CallCompleted',
      title: 'Inbound Call with Senior Support',
      description: 'Resolved SIP softphone network latency configuration query. AHT: 240s.',
      actor_name: 'Agent Sarah',
      occurred_at: new Date(Date.now() - 86400000).toISOString(),
      metadata_json: { recording_url: 'https://cdn.callsphere.com/rec/call_89412.wav' }
    },
    {
      id: '3',
      channel: 'SALES',
      event_type: 'OpportunityCreated',
      title: 'Enterprise Annual Renewal Deal Created',
      description: 'Opportunity value: $45,000 | Stage: Proposal Sent (80% probability)',
      actor_name: 'Account Exec',
      occurred_at: new Date(Date.now() - 172800000).toISOString(),
      metadata_json: {}
    }
  ];

  const handleSendQuickMessage = () => {
    setMessageSentNotification(true);
    setTimeout(() => setMessageSentNotification(false), 3000);
  };

  return (
    <div className="h-full flex flex-col space-y-4 max-w-7xl mx-auto">
      {/* Active Call Floating Status Banner */}
      <div className="bg-slate-900 text-white px-6 py-3.5 rounded-2xl shadow-xl flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
            <PhoneCall className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white">{callerName || sampleCustomer.name}</span>
              <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-[10px] uppercase font-bold">
                Matched VIP Customer
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">{fromNumber || toNumber || sampleCustomer.phone}</p>
          </div>
        </div>

        {/* Softphone In-Call Controls */}
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 bg-slate-800 rounded-xl text-xs font-mono font-bold text-slate-300 flex items-center gap-2 border border-slate-700">
            <Clock className="h-3.5 w-3.5 text-indigo-400" />
            <span>03:42</span>
          </div>

          <button
            onClick={toggleMute}
            className={`p-2 rounded-xl text-xs font-semibold border transition ${
              isMuted ? 'bg-amber-500 text-slate-900 border-amber-400' : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            {isMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </button>

          <button
            onClick={toggleHold}
            className={`p-2 rounded-xl text-xs font-semibold border transition ${
              isOnHold ? 'bg-amber-500 text-slate-900 border-amber-400' : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            {isOnHold ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
          </button>

          <button
            onClick={() => { clearActiveCall(); setAgentState('AVAILABLE'); }}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold rounded-xl text-xs shadow-lg shadow-rose-600/30 flex items-center gap-2 transition"
          >
            <PhoneOff className="h-4 w-4" /> End Call
          </button>
        </div>
      </div>

      {/* 3-Column Agent Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-0 overflow-hidden">
        {/* Left Column: Live Queue & Customer Profile (3 cols) */}
        <div className="lg:col-span-3 space-y-4 overflow-y-auto">
          {/* Live Inbound Queue Depth */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Live Priority Queues</h3>
              <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-bold">2 Waiting</span>
            </div>

            <div className="space-y-2">
              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-slate-900">VIP Sales Queue</p>
                  <p className="text-[10px] text-slate-500">+1 800 555 0199</p>
                </div>
                <span className="font-mono text-indigo-600 font-bold">00:14</span>
              </div>
              <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-slate-900">Tech Support Tier 1</p>
                  <p className="text-[10px] text-slate-500">+1 800 555 0122</p>
                </div>
                <span className="font-mono text-amber-600 font-bold">01:05</span>
              </div>
            </div>
          </div>

          {/* Caller Profile Card */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white flex items-center justify-center font-bold text-sm shadow">
                RK
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-sm">{sampleCustomer.name}</h4>
                <p className="text-xs text-slate-500">{sampleCustomer.company}</p>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Health Score:</span>
                <span className="font-bold text-emerald-600">{sampleCustomer.healthScore}/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Lifetime Value:</span>
                <span className="font-bold text-slate-900">{sampleCustomer.ltv}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Current Plan:</span>
                <span className="font-semibold text-indigo-600">{sampleCustomer.plan}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Column: Interactive C360 Timeline & Agent Call Script (6 cols) */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
          {/* Navigation Tabs */}
          <div className="flex items-center border-b border-slate-200 px-4 pt-3 gap-2">
            <button
              onClick={() => setActiveTab('timeline')}
              className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
                activeTab === 'timeline'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-900'
              }`}
            >
              Unified Customer Timeline
            </button>
            <button
              onClick={() => setActiveTab('script')}
              className={`px-4 py-2 text-xs font-semibold border-b-2 transition ${
                activeTab === 'script'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-900'
              }`}
            >
              Call Script &amp; Talking Points
            </button>
          </div>

          <div className="flex-1 p-5 overflow-y-auto">
            {activeTab === 'timeline' && (
              <CustomerTimeline events={sampleTimeline as any} />
            )}

            {activeTab === 'script' && (
              <div className="space-y-4 text-xs text-slate-700">
                <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl space-y-1.5">
                  <p className="font-bold text-indigo-950 flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4 text-indigo-600" /> Greeting &amp; Identity Verification
                  </p>
                  <p className="text-slate-600">
                    &quot;Thank you for calling CallSphere VIP Support, my name is Dhanunjay. May I confirm who I have the pleasure of speaking with today?&quot;
                  </p>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
                  <p className="font-bold text-slate-900">Enterprise Renewal Script</p>
                  <p className="text-slate-600">
                    &quot;I see your enterprise subscription is scheduled for renewal next month. We have prepared an optimized multi-channel communication bundle with 15% dedicated agent savings.&quot;
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Quick Omnichannel Actions & Notes (3 cols) */}
        <div className="lg:col-span-3 space-y-4 overflow-y-auto">
          {/* Quick Omnichannel Dispatch */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Quick Omnichannel Action</h3>

            <div className="flex gap-1">
              {(['WHATSAPP', 'SMS', 'EMAIL'] as const).map((ch) => (
                <button
                  key={ch}
                  onClick={() => setQuickMessageChannel(ch)}
                  className={`flex-1 py-1.5 rounded-lg text-[11px] font-semibold transition ${
                    quickMessageChannel === ch ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {ch}
                </button>
              ))}
            </div>

            <textarea
              rows={3}
              value={quickMessageText}
              onChange={(e) => setQuickMessageText(e.target.value)}
              className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />

            {messageSentNotification && (
              <p className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" /> Message Sent Successfully!
              </p>
            )}

            <button
              onClick={handleSendQuickMessage}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-md shadow-indigo-600/30 flex items-center justify-center gap-1.5 transition"
            >
              <Send className="h-3.5 w-3.5" /> Send {quickMessageChannel}
            </button>
          </div>

          {/* Agent Call Notes */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Live Interaction Notes</h3>
            <textarea
              rows={5}
              placeholder="Type call notes here..."
              value={quickNotes}
              onChange={(e) => setQuickNotes(e.target.value)}
              className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
