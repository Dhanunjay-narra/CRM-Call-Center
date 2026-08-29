'use client';

import React, { useState } from 'react';
import { 
  GitFork, Phone, Volume2, Play, ArrowRight, 
  Settings, CheckCircle2, PhoneForwarded, Sparkles 
} from 'lucide-react';

interface IVRNode {
  id: string;
  name: string;
  type: 'MENU' | 'PLAY_MESSAGE' | 'TRANSFER_QUEUE' | 'HANGUP';
  text_to_speech?: string;
  routes?: Record<string, string>;
  queue_name?: string;
}

export default function VisualIVRPage() {
  const [activeSimNodeId, setActiveSimNodeId] = useState<string>('node-1');
  const [simLog, setSimLog] = useState<string[]>([
    'Call Started: Connected to Main IVR Entry Point'
  ]);

  const ivrNodes: IVRNode[] = [
    {
      id: 'node-1',
      name: 'Main Business Greeting',
      type: 'PLAY_MESSAGE',
      text_to_speech: 'Thank you for calling CallSphere Enterprise. Your call may be recorded for quality assurance.'
    },
    {
      id: 'node-2',
      name: 'Department Routing Menu',
      type: 'MENU',
      text_to_speech: 'Press 1 for Sales, Press 2 for Technical Support, or Press 0 for General Operator.',
      routes: {
        '1': 'node-3',
        '2': 'node-4',
        '0': 'node-5'
      }
    },
    {
      id: 'node-3',
      name: 'Transfer to VIP Sales Queue',
      type: 'TRANSFER_QUEUE',
      queue_name: 'VIP Sales Queue (Required: Sales, English/Telugu)'
    },
    {
      id: 'node-4',
      name: 'Transfer to Support Tier 2',
      type: 'TRANSFER_QUEUE',
      queue_name: 'Technical Support Tier 2'
    },
    {
      id: 'node-5',
      name: 'Transfer to Operator',
      type: 'TRANSFER_QUEUE',
      queue_name: 'General Inquiries'
    }
  ];

  const handleSimulateDTMF = (digit: string) => {
    const currentNode = ivrNodes.find((n) => n.id === activeSimNodeId);
    if (!currentNode || !currentNode.routes) return;

    const nextNodeId = currentNode.routes[digit];
    if (nextNodeId) {
      const nextNode = ivrNodes.find((n) => n.id === nextNodeId);
      setActiveSimNodeId(nextNodeId);
      setSimLog((prev) => [
        ...prev,
        `Pressed DTMF: [${digit}] -> Routing to '${nextNode?.name}'`,
        nextNode?.type === 'TRANSFER_QUEUE' ? `Enqueued into ${nextNode.queue_name}` : ''
      ].filter(Boolean));
    } else {
      setSimLog((prev) => [...prev, `Invalid digit [${digit}]. Please choose 1, 2, or 0.`]);
    }
  };

  const handleSimulateNext = () => {
    if (activeSimNodeId === 'node-1') {
      setActiveSimNodeId('node-2');
      setSimLog((prev) => [...prev, 'Message completed -> Moving to Department Routing Menu']);
    }
  };

  const handleResetSim = () => {
    setActiveSimNodeId('node-1');
    setSimLog(['Call Started: Connected to Main IVR Entry Point']);
  };

  const activeNode = ivrNodes.find((n) => n.id === activeSimNodeId);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-slate-900">Visual IVR Flow Builder &amp; Interactive Simulator</h2>
        <p className="text-xs text-slate-500 mt-0.5">Design multi-level DTMF voice trees, Text-to-Speech greetings, and smart queue handoffs</p>
      </div>

      {/* 2-Column Builder & Simulator Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Visual Node Tree (7 cols) */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-xs uppercase tracking-wider">Active IVR Tree Hierarchy</h3>
            <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-[10px] font-bold">
              Published &bull; Version 2.4
            </span>
          </div>

          <div className="space-y-4 pt-2">
            {ivrNodes.map((node, idx) => (
              <div
                key={node.id}
                className={`p-4 rounded-xl border transition ${
                  activeSimNodeId === node.id
                    ? 'border-indigo-600 bg-indigo-50/40 ring-2 ring-indigo-500/20'
                    : 'border-slate-200 bg-slate-50/50'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-900 text-white text-[10px] font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <span className="font-bold text-xs text-slate-900">{node.name}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-slate-200 text-slate-700 rounded text-[10px] font-mono font-bold">
                    {node.type}
                  </span>
                </div>

                {node.text_to_speech && (
                  <p className="text-xs text-slate-600 bg-white p-2.5 rounded-lg border border-slate-200 mt-2 flex items-start gap-2">
                    <Volume2 className="h-4 w-4 text-indigo-500 shrink-0 mt-0.5" />
                    <span>&quot;{node.text_to_speech}&quot;</span>
                  </p>
                )}

                {node.routes && (
                  <div className="mt-2.5 flex gap-2">
                    {Object.entries(node.routes).map(([key, target]) => (
                      <span key={key} className="px-2 py-1 bg-indigo-100/70 text-indigo-800 rounded text-[10px] font-bold font-mono">
                        Key [{key}] &rarr; {ivrNodes.find((n) => n.id === target)?.name}
                      </span>
                    ))}
                  </div>
                )}

                {node.queue_name && (
                  <p className="text-xs text-emerald-700 font-semibold mt-2 flex items-center gap-1.5">
                    <PhoneForwarded className="h-3.5 w-3.5" /> Transfer to: {node.queue_name}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right Side: Interactive DTMF Simulator (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900 text-white p-6 rounded-2xl shadow-xl flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white text-sm flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-400" /> Interactive DTMF Simulator
              </h3>
              <button onClick={handleResetSim} className="text-[11px] text-indigo-400 hover:underline">
                Restart Call
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-1">Test live caller experience &amp; audio flow</p>
          </div>

          {/* Current Sim Voice Output */}
          <div className="p-4 bg-slate-800 rounded-xl border border-slate-700 space-y-2">
            <p className="text-[10px] font-bold uppercase text-indigo-400 tracking-wider">Current IVR Prompt Audio</p>
            <p className="text-xs font-medium text-slate-200 italic">
              &quot;{activeNode?.text_to_speech || activeNode?.queue_name || 'Enqueued into Agent Routing'}&quot;
            </p>
            {activeNode?.type === 'PLAY_MESSAGE' && (
              <button
                onClick={handleSimulateNext}
                className="mt-2 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-semibold hover:bg-indigo-500 transition"
              >
                Simulate Greeting End &rarr;
              </button>
            )}
          </div>

          {/* Simulator Dialpad */}
          <div>
            <p className="text-[10px] font-bold uppercase text-slate-400 tracking-wider mb-2">Caller Keypad Input</p>
            <div className="grid grid-cols-3 gap-2">
              {['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'].map((d) => (
                <button
                  key={d}
                  onClick={() => handleSimulateDTMF(d)}
                  className="py-2.5 bg-slate-800 hover:bg-indigo-600 hover:text-white border border-slate-700 rounded-xl font-bold font-mono text-sm transition"
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Live Execution Logs */}
          <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 font-mono text-[11px] space-y-1 max-h-40 overflow-y-auto">
            <p className="text-slate-500 font-bold uppercase text-[9px]">Simulator Execution Log:</p>
            {simLog.map((log, i) => (
              <p key={i} className="text-slate-300">&gt; {log}</p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
