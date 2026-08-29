'use client';

import React, { useState } from 'react';
import { 
  BookOpen, Search, Plus, Sparkles, FileText, 
  HelpCircle, CheckCircle2, ChevronRight 
} from 'lucide-react';

export default function KnowledgeBasePage() {
  const [searchQuery, setSearchQuery] = useState('');

  const articles = [
    {
      id: 'kb-1',
      title: 'SIP Softphone Audio Latency & QoS Optimization Guide',
      category: 'Telephony Infrastructure',
      is_call_script: false,
      snippet: 'Ensure UDP ports 10000-20000 are unblocked and prioritize DSCP EF (Expedited Forwarding) 46 for voice packets.'
    },
    {
      id: 'kb-2',
      title: 'Enterprise Renewal Talking Script & Pricing Tiers',
      category: 'Agent Call Scripts',
      is_call_script: true,
      snippet: 'Active guide for handling contract renewals, volume discounts, and 24/7 dedicated support add-ons.'
    },
    {
      id: 'kb-3',
      title: 'WhatsApp Business Cloud API Webhook Setup SOP',
      category: 'Omnichannel Integration',
      is_call_script: false,
      snippet: 'Step-by-step verification of Meta system user tokens, webhook endpoints, and message status callbacks.'
    }
  ];

  const filteredArticles = articles.filter((a) =>
    `${a.title} ${a.category} ${a.snippet}`.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Knowledge Base &amp; Agent Call Scripts</h2>
          <p className="text-xs text-slate-500 mt-0.5">Central repository for troubleshooting procedures, agent talking scripts, and customer FAQs</p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center gap-2 transition self-start sm:self-auto">
          <Plus className="h-4 w-4" /> New Article / Script
        </button>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search articles, call scripts, and FAQs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredArticles.map((art) => (
          <div key={art.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase text-indigo-600 tracking-wider">
                  {art.category}
                </span>
                {art.is_call_script && (
                  <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md text-[10px] font-bold">
                    Agent Script
                  </span>
                )}
              </div>

              <h4 className="font-bold text-slate-900 text-sm leading-snug">{art.title}</h4>
              <p className="text-xs text-slate-600 line-clamp-3 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                {art.snippet}
              </p>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-indigo-600 font-semibold cursor-pointer hover:underline">
              <span>Read Full Guide</span>
              <ChevronRight className="h-4 w-4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
