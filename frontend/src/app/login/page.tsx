'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Zap, User, Lock, ArrowRight, CheckCircle2, PhoneCall, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('admin@callsphere.com');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (selectedRole: string = 'Super Admin') => {
    setIsLoading(true);
    // Store mock session token & profile
    if (typeof window !== 'undefined') {
      localStorage.setItem('callsphere_auth_token', 'jwt_demo_token_callsphere_crm_2026');
      localStorage.setItem('callsphere_user', JSON.stringify({
        email: email || 'admin@callsphere.com',
        role: selectedRole,
        name: 'Dhanunjay (System Admin)',
        tenant_id: 'tenant_enterprise_001'
      }));
    }

    setTimeout(() => {
      setIsLoading(false);
      router.push('/');
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md bg-slate-800/90 backdrop-blur-xl border border-slate-700/80 rounded-3xl p-8 shadow-2xl space-y-6 relative z-10">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 mb-2">
            <PhoneCall className="h-7 w-7" />
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">CallSphere CRM</h2>
          <p className="text-xs text-slate-400">Intelligent Call Center &amp; Customer Relationship Platform</p>
        </div>

        {/* 1-Click Instant Login Banner */}
        <div className="p-4 bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-2xl text-white shadow-lg space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-300 animate-pulse" />
            <h4 className="text-sm font-bold">1-Click Instant Demo Login</h4>
          </div>
          <p className="text-xs text-indigo-100">
            Click below to instantly access the full system with Super Admin privileges. No typing needed!
          </p>
          <button
            onClick={() => handleLogin('Super Admin')}
            disabled={isLoading}
            className="w-full py-3 bg-white text-indigo-900 hover:bg-indigo-50 font-bold rounded-xl text-sm shadow-md transition flex items-center justify-center gap-2 cursor-pointer"
          >
            {isLoading ? (
              <span className="inline-block animate-spin">⚡</span>
            ) : (
              <>
                <span>🚀 Enter Website Directly (1-Click)</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>

        {/* Or Quick Role Access */}
        <div className="space-y-3">
          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-700 w-full" />
            <span className="bg-slate-800 px-3 text-[11px] font-semibold text-slate-400 uppercase tracking-wider absolute">
              Or Login as Role
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2">
            <button
              onClick={() => handleLogin('Call Center Agent')}
              className="p-3 bg-slate-700/50 hover:bg-slate-700 border border-slate-600/50 rounded-xl text-left transition text-white group"
            >
              <div className="text-xs font-bold flex items-center justify-between">
                <span>Agent Desk</span>
                <ArrowRight className="h-3 w-3 text-slate-400 group-hover:text-indigo-400 transition" />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Softphone &amp; Queue</p>
            </button>

            <button
              onClick={() => handleLogin('Supervisor')}
              className="p-3 bg-slate-700/50 hover:bg-slate-700 border border-slate-600/50 rounded-xl text-left transition text-white group"
            >
              <div className="text-xs font-bold flex items-center justify-between">
                <span>Supervisor</span>
                <ArrowRight className="h-3 w-3 text-slate-400 group-hover:text-indigo-400 transition" />
              </div>
              <p className="text-[10px] text-slate-400 mt-1">Barge-in &amp; SLA</p>
            </button>
          </div>
        </div>

        {/* Credentials Form (Pre-filled) */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLogin('Super Admin');
          }}
          className="space-y-4 pt-2 border-t border-slate-700/50"
        >
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <div className="relative">
              <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-xs bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-xl text-xs transition"
          >
            Standard Sign In
          </button>
        </form>

        {/* Security / Compliance Footer */}
        <div className="flex items-center justify-center gap-1 text-[11px] text-slate-400">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>Enterprise 256-bit TLS • SOC2 &amp; PCI-DSS Ready</span>
        </div>
      </div>
    </div>
  );
}
