'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  Search, Phone, Bell, User, CheckCircle2, Coffee, ShieldAlert,
  HelpCircle, ChevronDown, PhoneCall, PhoneOff, MessageSquare
} from 'lucide-react';
import { api } from '@/lib/api';
import { useAgentStore } from '@/stores/useAgentStore';
import { useCallStore } from '@/stores/useCallStore';
import { AgentState, BreakType } from '@/lib/types';

export default function Navbar({ onOpenSoftphone }: { onOpenSoftphone: () => void }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [showStateDropdown, setShowStateDropdown] = useState(false);

  const { agentState, breakType, setAgentState } = useAgentStore();
  const { activeCallId, callStatus, fromNumber, toNumber } = useCallStore();

  const searchRef = useRef<HTMLDivElement>(null);

  // Global Search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await api.searchGlobal(searchQuery);
        setSearchResults(res.results || []);
        setShowSearchDropdown(true);
      } catch (err) {
        console.error(err);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleStateChange = async (newState: AgentState, bType?: BreakType) => {
    try {
      await api.setAgentState(newState, bType);
      setAgentState(newState, bType);
      setShowStateDropdown(false);
    } catch (err) {
      console.error(err);
    }
  };

  const getStateColor = (state: AgentState) => {
    switch (state) {
      case 'AVAILABLE': return 'bg-emerald-500 text-white';
      case 'ON_CALL': return 'bg-rose-500 text-white animate-pulse';
      case 'AFTER_CALL_WORK': return 'bg-amber-500 text-white';
      case 'BREAK': return 'bg-amber-400 text-slate-900';
      case 'TRAINING': return 'bg-sky-500 text-white';
      default: return 'bg-slate-400 text-white';
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Global Search */}
      <div className="relative w-96" ref={searchRef}>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search customers, leads, deals, tickets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchResults.length > 0 && setShowSearchDropdown(true)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
          />
        </div>

        {/* Search Results Dropdown */}
        {showSearchDropdown && searchResults.length > 0 && (
          <div className="absolute top-12 left-0 w-full bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-96 overflow-y-auto p-2">
            <p className="text-xs font-semibold text-slate-400 px-3 py-1.5 uppercase">Quick Results</p>
            {searchResults.map((item, idx) => (
              <Link
                key={idx}
                href={item.url}
                onClick={() => setShowSearchDropdown(false)}
                className="flex items-start gap-3 px-3 py-2 hover:bg-slate-50 rounded-lg text-sm transition"
              >
                <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-md font-semibold text-xs uppercase">
                  {item.entity_type.slice(0, 3)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-900 truncate">{item.title}</p>
                  {item.subtitle && <p className="text-xs text-slate-500 truncate">{item.subtitle}</p>}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Center Active Call Indicator if on call */}
      {activeCallId && (
        <button
          onClick={onOpenSoftphone}
          className="flex items-center gap-2.5 px-4 py-1.5 bg-rose-50 border border-rose-200 text-rose-700 rounded-full text-xs font-semibold animate-pulse"
        >
          <PhoneCall className="h-3.5 w-3.5" />
          <span>Active Call: {fromNumber || toNumber || 'Connected'}</span>
        </button>
      )}

      {/* Right Action Tools */}
      <div className="flex items-center gap-4">
        {/* Softphone Dialer Launcher */}
        <button
          onClick={onOpenSoftphone}
          className="flex items-center gap-2 px-3 py-2 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 rounded-lg text-sm font-semibold transition"
        >
          <Phone className="h-4 w-4" />
          <span>Softphone</span>
        </button>

        {/* Agent Workforce State Selector */}
        <div className="relative">
          <button
            onClick={() => setShowStateDropdown(!showStateDropdown)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold shadow-sm transition ${getStateColor(agentState)}`}
          >
            <span className="w-2 h-2 rounded-full bg-white animate-ping" />
            <span>{agentState} {breakType ? `(${breakType})` : ''}</span>
            <ChevronDown className="h-3 w-3" />
          </button>

          {showStateDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-xl z-50 py-1 text-sm">
              <p className="text-xs font-semibold text-slate-400 px-3 py-1 uppercase">Workforce State</p>
              <button
                onClick={() => handleStateChange('AVAILABLE')}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 flex items-center gap-2 text-emerald-600 font-medium"
              >
                <CheckCircle2 className="h-4 w-4" /> Available
              </button>
              <button
                onClick={() => handleStateChange('BREAK', 'LUNCH')}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 flex items-center gap-2 text-amber-600 font-medium"
              >
                <Coffee className="h-4 w-4" /> Lunch Break
              </button>
              <button
                onClick={() => handleStateChange('BREAK', 'TEA')}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 flex items-center gap-2 text-amber-600 font-medium"
              >
                <Coffee className="h-4 w-4" /> Short Break
              </button>
              <button
                onClick={() => handleStateChange('TRAINING')}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 flex items-center gap-2 text-sky-600 font-medium"
              >
                <HelpCircle className="h-4 w-4" /> Training
              </button>
              <button
                onClick={() => handleStateChange('OFFLINE')}
                className="w-full text-left px-3 py-1.5 hover:bg-slate-50 flex items-center gap-2 text-slate-600 font-medium"
              >
                <PhoneOff className="h-4 w-4" /> Offline
              </button>
            </div>
          )}
        </div>

        {/* Notifications */}
        <button className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-full transition relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-600 rounded-full" />
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white flex items-center justify-center text-xs font-bold shadow">
            DN
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-semibold text-slate-800">Dhanunjay Narra</p>
            <p className="text-[10px] text-slate-500 font-medium">Administrator</p>
          </div>
        </div>
      </div>
    </header>
  );
}
