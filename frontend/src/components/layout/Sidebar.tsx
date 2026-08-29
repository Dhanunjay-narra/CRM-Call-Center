'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, Headphones, Activity, MessageSquare, 
  Users, Building2, KanbanSquare, LifeBuoy, GitFork, 
  Sparkles, BookOpen, Award, BarChart3, ShieldCheck, PhoneForwarded
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Agent Workspace', href: '/agent', icon: Headphones, badge: 'Live' },
  { name: 'Supervisor Live', href: '/supervisor', icon: Activity },
  { name: 'Unified Inbox', href: '/inbox', icon: MessageSquare },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Customers 360', href: '/customers', icon: Building2 },
  { name: 'Sales Pipelines', href: '/deals', icon: KanbanSquare },
  { name: 'Support & SLA', href: '/tickets', icon: LifeBuoy },
  { name: 'Visual IVR', href: '/ivr', icon: PhoneForwarded },
  { name: 'Automation', href: '/workflows', icon: GitFork },
  { name: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
  { name: 'QA & Scorecards', href: '/qa', icon: Award },
  { name: 'Analytics & KPIs', href: '/analytics', icon: BarChart3 },
  { name: 'Admin & Audit', href: '/admin', icon: ShieldCheck },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-500/30">
          <Headphones className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-bold text-white tracking-wide text-sm">CallSphere CRM</h1>
          <p className="text-[10px] text-indigo-400 font-semibold tracking-wider uppercase">Contact Center 360</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <item.icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-[10px] uppercase font-bold animate-pulse">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800">
        <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700/50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-medium text-slate-300">Telephony Engine</span>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-950 text-emerald-300 rounded-md">99.99%</span>
        </div>
      </div>
    </aside>
  );
}
