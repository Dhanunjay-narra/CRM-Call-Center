'use client';

import React, { useState } from 'react';
import { 
  Phone, MessageSquare, Mail, LifeBuoy, DollarSign, 
  Clock, User, Filter, CheckCircle, AlertTriangle 
} from 'lucide-react';
import { TimelineEvent } from '@/lib/types';

export default function CustomerTimeline({ events }: { events: TimelineEvent[] }) {
  const [filterChannel, setFilterChannel] = useState<string>('ALL');

  const filteredEvents = filterChannel === 'ALL' 
    ? events 
    : events.filter((e) => e.channel.toUpperCase() === filterChannel);

  const getChannelIcon = (channel: string) => {
    switch (channel.toUpperCase()) {
      case 'CALL': return <Phone className="h-4 w-4 text-emerald-500" />;
      case 'WHATSAPP': return <MessageSquare className="h-4 w-4 text-green-500" />;
      case 'EMAIL': return <Mail className="h-4 w-4 text-sky-500" />;
      case 'TICKET': return <LifeBuoy className="h-4 w-4 text-rose-500" />;
      case 'SALES': return <DollarSign className="h-4 w-4 text-amber-500" />;
      default: return <Clock className="h-4 w-4 text-indigo-500" />;
    }
  };

  const getChannelBg = (channel: string) => {
    switch (channel.toUpperCase()) {
      case 'CALL': return 'bg-emerald-50 border-emerald-200';
      case 'WHATSAPP': return 'bg-green-50 border-green-200';
      case 'EMAIL': return 'bg-sky-50 border-sky-200';
      case 'TICKET': return 'bg-rose-50 border-rose-200';
      case 'SALES': return 'bg-amber-50 border-amber-200';
      default: return 'bg-indigo-50 border-indigo-200';
    }
  };

  return (
    <div className="space-y-4">
      {/* Channel Filter Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {['ALL', 'CALL', 'WHATSAPP', 'EMAIL', 'TICKET', 'SALES'].map((ch) => (
          <button
            key={ch}
            onClick={() => setFilterChannel(ch)}
            className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition ${
              filterChannel === ch
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {ch === 'ALL' ? 'All Interactions' : ch}
          </button>
        ))}
      </div>

      {/* Chronological Stream */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-xs bg-white rounded-xl border border-slate-200">
            No timeline interactions found for this filter.
          </div>
        ) : (
          filteredEvents.map((evt, idx) => (
            <div key={evt.id || idx} className="relative group">
              {/* Event Dot */}
              <div className="absolute -left-6 top-1.5 w-5 h-5 rounded-full bg-white border-2 border-slate-300 group-hover:border-indigo-600 flex items-center justify-center transition">
                <span className="w-1.5 h-1.5 rounded-full bg-slate-400 group-hover:bg-indigo-600" />
              </div>

              {/* Event Card */}
              <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow transition">
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`p-1 rounded-md border ${getChannelBg(evt.channel)}`}>
                      {getChannelIcon(evt.channel)}
                    </span>
                    <span className="text-xs font-bold text-slate-900">{evt.title}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {new Date(evt.occurred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {new Date(evt.occurred_at).toLocaleDateString()}
                  </span>
                </div>

                {evt.description && (
                  <p className="text-xs text-slate-600 mt-1 line-clamp-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    {evt.description}
                  </p>
                )}

                {/* Metadata & Actor */}
                <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-100">
                  <span className="flex items-center gap-1 font-medium text-slate-500">
                    <User className="h-3 w-3" /> {evt.actor_name || 'Agent'}
                  </span>
                  {evt.metadata_json?.recording_url && (
                    <a
                      href={evt.metadata_json.recording_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-indigo-600 font-semibold hover:underline flex items-center gap-1"
                    >
                      <Phone className="h-3 w-3" /> Listen Recording
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
