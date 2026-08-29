'use client';

import React, { useState } from 'react';
import { 
  MessageSquare, Mail, Phone, Send, Paperclip, 
  Sparkles, Check, CheckCheck, Clock, User, Building2 
} from 'lucide-react';
import { ChannelType } from '@/lib/types';

interface Thread {
  id: string;
  customer_name: string;
  channel: ChannelType;
  last_message: string;
  last_time: string;
  unread: number;
  phone: string;
}

interface MessageItem {
  id: string;
  direction: 'INBOUND' | 'OUTBOUND';
  body: string;
  time: string;
  status: 'SENT' | 'DELIVERED' | 'READ';
}

export default function UnifiedInboxPage() {
  const [selectedThreadId, setSelectedThreadId] = useState('t-1');
  const [messageInput, setMessageInput] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const threads: Thread[] = [
    {
      id: 't-1',
      customer_name: 'Ravi Kumar',
      channel: 'WHATSAPP',
      last_message: 'Can you please send the updated quotation for 50 licenses?',
      last_time: '10:14 AM',
      unread: 1,
      phone: '+91 98765 43210'
    },
    {
      id: 't-2',
      customer_name: 'Acme Procurement',
      channel: 'EMAIL',
      last_message: 'Re: Master Services Agreement review from legal team',
      last_time: '09:45 AM',
      unread: 0,
      phone: 'procurement@acmemfg.com'
    },
    {
      id: 't-3',
      customer_name: 'Carlos Mendez',
      channel: 'SMS',
      last_message: 'Confirmed receipt of the verification OTP code.',
      last_time: 'Yesterday',
      unread: 0,
      phone: '+52 55 1234 5678'
    }
  ];

  const [messages, setMessages] = useState<Record<string, MessageItem[]>>({
    't-1': [
      { id: 'm-1', direction: 'INBOUND', body: 'Hello CallSphere team, we are ready to finalize our enterprise setup.', time: '10:05 AM', status: 'READ' },
      { id: 'm-2', direction: 'OUTBOUND', body: 'Great to hear Ravi! Our team has prepared the 50-seat contract with dedicated routing.', time: '10:08 AM', status: 'READ' },
      { id: 'm-3', direction: 'INBOUND', body: 'Can you please send the updated quotation for 50 licenses?', time: '10:14 AM', status: 'READ' }
    ]
  });

  const activeThread = threads.find((t) => t.id === selectedThreadId) || threads[0];
  const activeMessages = messages[selectedThreadId] || [];

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageInput.trim()) return;

    const newMsg: MessageItem = {
      id: `m-${Date.now()}`,
      direction: 'OUTBOUND',
      body: messageInput,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      status: 'DELIVERED'
    };

    setMessages((prev) => ({
      ...prev,
      [selectedThreadId]: [...(prev[selectedThreadId] || []), newMsg]
    }));
    setMessageInput('');
  };

  const handleApplyTemplate = (templateBody: string) => {
    setMessageInput(templateBody.replace('{{customer_name}}', activeThread.customer_name).replace('{{quote_amount}}', '$45,000'));
  };

  const getChannelBadge = (ch: ChannelType) => {
    switch (ch) {
      case 'WHATSAPP': return 'bg-green-50 text-green-700 border-green-200';
      case 'EMAIL': return 'bg-sky-50 text-sky-700 border-sky-200';
      case 'SMS': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default: return 'bg-slate-100 text-slate-700';
    }
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex flex-col max-w-7xl mx-auto space-y-4">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Unified Omnichannel Inbox</h2>
        <p className="text-xs text-slate-500 mt-0.5">WhatsApp, Email, and SMS customer conversations in a single multi-threaded stream</p>
      </div>

      {/* 3-Pane Inbox Container */}
      <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden grid grid-cols-1 md:grid-cols-12 min-h-0">
        {/* Left Pane: Conversation Threads (4 cols) */}
        <div className="md:col-span-4 border-r border-slate-200 flex flex-col min-h-0">
          <div className="p-3.5 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
            <span className="font-bold text-xs text-slate-700 uppercase tracking-wider">All Channels</span>
            <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-[10px] font-bold">
              {threads.length} Active
            </span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {threads.map((thread) => (
              <button
                key={thread.id}
                onClick={() => setSelectedThreadId(thread.id)}
                className={`w-full text-left p-4 hover:bg-slate-50 transition flex items-start justify-between gap-3 ${
                  selectedThreadId === thread.id ? 'bg-indigo-50/50 border-l-4 border-indigo-600' : ''
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold border uppercase ${getChannelBadge(thread.channel)}`}>
                      {thread.channel}
                    </span>
                    <p className="font-bold text-slate-900 text-xs truncate">{thread.customer_name}</p>
                  </div>
                  <p className="text-xs text-slate-600 truncate">{thread.last_message}</p>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-[10px] text-slate-400 font-mono">{thread.last_time}</span>
                  {thread.unread > 0 && (
                    <span className="block mt-1 w-4 h-4 bg-indigo-600 text-white rounded-full text-[10px] font-bold text-center leading-4 mx-auto">
                      {thread.unread}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Center Pane: Active Message Thread & Composer (8 cols) */}
        <div className="md:col-span-8 flex flex-col min-h-0">
          {/* Thread Header */}
          <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-xs">
                {activeThread.customer_name[0]}
              </div>
              <div>
                <h4 className="font-bold text-slate-900 text-xs">{activeThread.customer_name}</h4>
                <p className="text-[11px] text-slate-500 font-mono">{activeThread.phone}</p>
              </div>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border uppercase ${getChannelBadge(activeThread.channel)}`}>
              {activeThread.channel} Thread
            </span>
          </div>

          {/* Message Stream */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/30">
            {activeMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.direction === 'OUTBOUND' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-md p-3.5 rounded-2xl text-xs leading-relaxed shadow-sm ${
                    msg.direction === 'OUTBOUND'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none'
                  }`}
                >
                  {msg.body}
                </div>
                <div className="flex items-center gap-1 mt-1 text-[10px] text-slate-400 font-mono">
                  <span>{msg.time}</span>
                  {msg.direction === 'OUTBOUND' && <CheckCheck className="h-3 w-3 text-indigo-500" />}
                </div>
              </div>
            ))}
          </div>

          {/* Quick Template Selector */}
          <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center gap-2 overflow-x-auto text-[11px]">
            <span className="font-semibold text-slate-400 flex items-center gap-1 shrink-0">
              <Sparkles className="h-3 w-3 text-indigo-500" /> Templates:
            </span>
            <button
              onClick={() => handleApplyTemplate('Hello {{customer_name}}, your formal quotation of {{quote_amount}} is ready for review.')}
              className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-100 whitespace-nowrap"
            >
              Formal Quotation
            </button>
            <button
              onClick={() => handleApplyTemplate('Hi {{customer_name}}, confirming our support follow-up call tomorrow at 10 AM.')}
              className="px-2.5 py-1 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-100 whitespace-nowrap"
            >
              Call Follow-up
            </button>
          </div>

          {/* Composer Box */}
          <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-200 bg-white flex items-center gap-2">
            <input
              type="text"
              placeholder={`Reply via ${activeThread.channel}...`}
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              className="flex-1 p-2.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={!messageInput.trim()}
              className="p-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl shadow-md shadow-indigo-600/30 transition"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
