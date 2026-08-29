"use client";
import React, { useState } from "react";
import { 
  Phone, PhoneCall, PhoneOff, PhoneForwarded, Pause, Mic, MicOff, 
  UserCheck, Users, Ticket, Activity, ShieldCheck, Clock, CheckCircle2,
  Headphones, Search, RefreshCw, BarChart3, AlertCircle, PlusCircle
} from "lucide-react";

export default function CallCenterDashboard() {
  const [agentStatus, setAgentStatus] = useState<"AVAILABLE" | "BUSY" | "WRAP_UP" | "OFFLINE">("AVAILABLE");
  const [dialNumber, setDialNumber] = useState("+1 (800) 555-0199");
  const [callState, setCallState] = useState<"IDLE" | "CALLING" | "CONNECTED" | "ON_HOLD">("IDLE");
  const [isMuted, setIsMuted] = useState(false);
  const [callDuration, setCallDuration] = useState(142);
  const [activeTab, setActiveTab] = useState<"acd_queue" | "customer_360" | "tickets" | "analytics">("acd_queue");

  const [queueItems] = useState([
    { id: "CALL-8921", customer: "Satya Nadella", company: "Microsoft Global", waitSec: 42, queue: "VIP Priority Tier", priority: "HIGH" },
    { id: "CALL-8922", customer: "Sundar Pichai", company: "Alphabet Core", waitSec: 28, queue: "Enterprise Technical", priority: "CRITICAL" },
    { id: "CALL-8923", customer: "Jensen Huang", company: "NVIDIA Compute", waitSec: 15, queue: "Billing & Invoices", priority: "MEDIUM" },
  ]);

  const [tickets] = useState([
    { id: "TICK-901", title: "SIP Trunking jitter spike under peak ACD load", priority: "CRITICAL", status: "IN_PROGRESS", customer: "SpaceX Starlink", sla: "12m left" },
    { id: "TICK-902", title: "CRM Lead Webhook integration payload signature", priority: "HIGH", status: "OPEN", customer: "Stripe Payment Core", sla: "45m left" },
    { id: "TICK-903", title: "WebRTC Audio packet loss on Safari iOS 17.4", priority: "MEDIUM", status: "RESOLVED", customer: "Tesla Energy", sla: "Met SLA" },
  ]);

  const formatTimer = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-600/30">
            <Headphones className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white tracking-tight">ApexConnect OmniChannel</h1>
            <p className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Cloud Call Center & CRM Core</p>
          </div>
        </div>

        {/* Agent Status Selector */}
        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-800 p-1 rounded-xl border border-slate-700">
            {(["AVAILABLE", "BUSY", "WRAP_UP", "OFFLINE"] as const).map((st) => (
              <button
                key={st}
                onClick={() => setAgentStatus(st)}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                  agentStatus === st 
                    ? st === "AVAILABLE" ? "bg-emerald-600 text-white shadow" :
                      st === "BUSY" ? "bg-rose-600 text-white shadow" :
                      st === "WRAP_UP" ? "bg-amber-600 text-white shadow" : "bg-slate-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="h-8 w-[1px] bg-slate-800" />

          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold text-xs">
              DN
            </div>
            <div className="hidden sm:block text-left">
              <span className="text-xs font-bold block text-slate-200">Dhanunjay Narra</span>
              <span className="text-[10px] text-emerald-400 font-semibold">Tier 3 Voice Specialist</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 overflow-hidden">
        {/* Left: Softphone Dialer & Call Session Controls (4 cols) */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Phone className="w-4 h-4" /> WebRTC Softphone Dialer
              </span>
              <span className="text-[10px] font-bold bg-slate-800 px-2 py-0.5 rounded text-slate-400">SIP: v2.4</span>
            </div>

            {/* Dial Display */}
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center mb-4">
              <input
                type="text"
                value={dialNumber}
                onChange={(e) => setDialNumber(e.target.value)}
                className="bg-transparent text-xl font-mono font-bold text-white text-center w-full outline-none"
              />
              <div className="mt-2 flex items-center justify-center gap-2">
                <div className={`w-2 h-2 rounded-full ${callState === "CONNECTED" ? "bg-emerald-500 animate-pulse" : callState === "ON_HOLD" ? "bg-amber-500" : "bg-slate-600"}`} />
                <span className="text-xs text-slate-400 font-semibold uppercase">
                  {callState === "CONNECTED" ? `Live Audio (${formatTimer(callDuration)})` : callState}
                </span>
              </div>
            </div>

            {/* Keypad */}
            <div className="grid grid-cols-3 gap-2 mb-4">
              {["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"].map((k) => (
                <button
                  key={k}
                  onClick={() => setDialNumber((prev) => prev + k)}
                  className="p-3 bg-slate-800/80 hover:bg-slate-700/80 rounded-xl text-base font-bold text-slate-200 transition active:scale-95 border border-slate-700/50"
                >
                  {k}
                </button>
              ))}
            </div>
          </div>

          {/* Call Action Bar */}
          <div className="space-y-3 pt-3 border-t border-slate-800">
            {callState === "IDLE" ? (
              <button
                onClick={() => setCallState("CONNECTED")}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition"
              >
                <PhoneCall className="w-5 h-5" /> Start Outbound Call
              </button>
            ) : (
              <div className="space-y-2">
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setIsMuted(!isMuted)}
                    className={`py-2.5 rounded-xl font-bold text-xs flex flex-col items-center gap-1 border transition ${
                      isMuted ? "bg-rose-500/20 border-rose-500 text-rose-300" : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"
                    }`}
                  >
                    {isMuted ? <MicOff className="w-4 h-4 text-rose-400" /> : <Mic className="w-4 h-4" />}
                    <span>{isMuted ? "Muted" : "Mute"}</span>
                  </button>

                  <button
                    onClick={() => setCallState(callState === "ON_HOLD" ? "CONNECTED" : "ON_HOLD")}
                    className={`py-2.5 rounded-xl font-bold text-xs flex flex-col items-center gap-1 border transition ${
                      callState === "ON_HOLD" ? "bg-amber-500/20 border-amber-500 text-amber-300" : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"
                    }`}
                  >
                    <Pause className="w-4 h-4" />
                    <span>{callState === "ON_HOLD" ? "Resume" : "Hold"}</span>
                  </button>

                  <button
                    onClick={() => alert("Transfer initiated to Tier 2 Supervisor")}
                    className="py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl font-bold text-xs flex flex-col items-center gap-1 text-slate-300 transition"
                  >
                    <PhoneForwarded className="w-4 h-4" />
                    <span>Transfer</span>
                  </button>
                </div>

                <button
                  onClick={() => setCallState("IDLE")}
                  className="w-full py-3 bg-rose-600 hover:bg-rose-500 text-white font-bold text-sm rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-rose-600/30 transition"
                >
                  <PhoneOff className="w-5 h-5" /> Terminate Call
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Right: Workspace Panels (ACD Queue, Customer 360, Tickets) (8 cols) */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col shadow-xl">
          {/* Workspace Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab("acd_queue")}
                className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
                  activeTab === "acd_queue" ? "bg-indigo-600 text-white shadow" : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                ACD Live Queue ({queueItems.length})
              </button>
              <button
                onClick={() => setActiveTab("customer_360")}
                className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
                  activeTab === "customer_360" ? "bg-indigo-600 text-white shadow" : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                Customer 360 Profile
              </button>
              <button
                onClick={() => setActiveTab("tickets")}
                className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
                  activeTab === "tickets" ? "bg-indigo-600 text-white shadow" : "bg-slate-800 text-slate-400 hover:text-white"
                }`}
              >
                Support Tickets ({tickets.length})
              </button>
            </div>

            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>ACD Broker Live</span>
            </div>
          </div>

          {/* Panel Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === "acd_queue" && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400 px-3 font-semibold uppercase">
                  <span>Caller Details</span>
                  <span>Queue Channel</span>
                  <span>Wait Time</span>
                  <span>Action</span>
                </div>
                {queueItems.map((q) => (
                  <div key={q.id} className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl flex items-center justify-between hover:border-slate-700 transition">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-slate-800 text-slate-300 flex items-center justify-center font-bold text-xs">
                        {q.customer.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{q.customer}</h4>
                        <p className="text-xs text-slate-400">{q.company}</p>
                      </div>
                    </div>

                    <div>
                      <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg">
                        {q.queue}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 text-xs text-amber-400 font-mono font-bold">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{q.waitSec}s</span>
                    </div>

                    <button
                      onClick={() => {
                        setCallState("CONNECTED");
                        setDialNumber(q.customer);
                      }}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-lg shadow transition"
                    >
                      Answer
                    </button>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "customer_360" && (
              <div className="space-y-6">
                <div className="p-5 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center text-xl font-black">
                      SN
                    </div>
                    <div>
                      <h3 className="text-lg font-black text-white">Satya Nadella</h3>
                      <p className="text-xs text-slate-400">Chief Executive Officer • Microsoft Corporation</p>
                      <span className="inline-block mt-1 text-[10px] font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full">
                        Enterprise Diamond VIP Tier
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400">Total LTV Revenue</p>
                    <p className="text-xl font-mono font-bold text-emerald-400">$1,450,000</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <p className="text-xs text-slate-400">Voice Calls Total</p>
                    <p className="text-2xl font-bold text-white mt-1">28</p>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <p className="text-xs text-slate-400">Resolved Tickets</p>
                    <p className="text-2xl font-bold text-white mt-1">14</p>
                  </div>
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <p className="text-xs text-slate-400">CSAT Score</p>
                    <p className="text-2xl font-bold text-emerald-400 mt-1">4.9 / 5.0</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "tickets" && (
              <div className="space-y-3">
                {tickets.map((t) => (
                  <div key={t.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono font-bold text-indigo-400">{t.id}</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-800 text-slate-300 rounded">
                          {t.customer}
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          t.priority === "CRITICAL" ? "bg-rose-500/20 text-rose-400" : "bg-amber-500/20 text-amber-400"
                        }`}>
                          {t.priority}
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white">{t.title}</h4>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-bold text-slate-300 block">{t.status}</span>
                      <span className="text-[11px] text-amber-400 font-semibold">{t.sla}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
