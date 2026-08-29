'use client';

import React, { useState, useEffect } from 'react';
import { 
  Phone, PhoneOff, PhoneCall, Mic, MicOff, Pause, Play, 
  ArrowRightLeft, X, Delete, CheckCircle2, User, Clock
} from 'lucide-react';
import { api } from '@/lib/api';
import { useCallStore } from '@/stores/useCallStore';
import { useAgentStore } from '@/stores/useAgentStore';

export default function SoftphoneModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [dialNumber, setDialNumber] = useState('');
  const [dispositionCode, setDispositionCode] = useState('INTERESTED');
  const [dispositionCategory, setDispositionCategory] = useState('Sales Pitch');
  const [dispositionNotes, setDispositionNotes] = useState('');
  const [isTransferring, setIsTransferring] = useState(false);
  const [transferTarget, setTransferTarget] = useState('');

  const { 
    activeCallId, callStatus, fromNumber, toNumber, callerName, 
    isOnHold, isMuted, callDurationSeconds,
    setActiveCall, clearActiveCall, toggleHold, toggleMute, incrementDuration
  } = useCallStore();

  const { setAgentState } = useAgentStore();

  // Call Duration Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (callStatus === 'IN_PROGRESS' || callStatus === 'ON_HOLD') {
      interval = setInterval(() => {
        incrementDuration();
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [callStatus, incrementDuration]);

  if (!isOpen) return null;

  const handleDigitClick = (digit: string) => {
    setDialNumber((prev) => prev + digit);
  };

  const handleInitiateCall = async () => {
    if (!dialNumber) return;
    try {
      const res = await api.initiateCall({
        direction: 'OUTBOUND',
        from_number: '+18005550000',
        to_number: dialNumber
      });
      setActiveCall({
        activeCallId: res.id,
        callStatus: 'RINGING',
        toNumber: dialNumber,
        customerId: res.customer_id,
        callerName: res.caller_name || 'Prospect'
      });
      // Simulate answer after 1.5s
      setTimeout(async () => {
        await api.answerCall(res.id);
        setActiveCall({ callStatus: 'IN_PROGRESS' });
        setAgentState('ON_CALL');
      }, 1500);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnswerCall = async () => {
    if (!activeCallId) return;
    try {
      await api.answerCall(activeCallId);
      setActiveCall({ callStatus: 'IN_PROGRESS' });
      setAgentState('ON_CALL');
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleHold = async () => {
    if (!activeCallId) return;
    try {
      const newHold = !isOnHold;
      await api.holdCall(activeCallId, newHold);
      toggleHold();
      setActiveCall({ callStatus: newHold ? 'ON_HOLD' : 'IN_PROGRESS' });
    } catch (err) {
      console.error(err);
    }
  };

  const handleEndCall = async () => {
    if (!activeCallId) return;
    try {
      await api.endCall(activeCallId);
      setActiveCall({ callStatus: 'AFTER_CALL_WORK' });
      setAgentState('AFTER_CALL_WORK');
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitDisposition = async () => {
    if (!activeCallId) return;
    try {
      await api.submitDisposition(activeCallId, {
        disposition_code: dispositionCode,
        category: dispositionCategory,
        summary_notes: dispositionNotes,
        follow_up_required: dispositionCode === 'CALLBACK_REQUESTED'
      });
      clearActiveCall();
      setAgentState('AVAILABLE');
      setDialNumber('');
      setDispositionNotes('');
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="fixed bottom-6 right-6 w-80 bg-white border border-slate-200 rounded-2xl shadow-2xl z-50 overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-5">
      {/* Header */}
      <div className="px-4 py-3 bg-slate-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Phone className="h-4 w-4 text-indigo-400" />
          <span className="font-semibold text-xs">WebRTC Softphone Dialer</span>
        </div>
        <button onClick={onClose} className="p-1 text-slate-400 hover:text-white rounded-full">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 flex-1">
        {/* State 1: Active In Progress or On Hold */}
        {(callStatus === 'IN_PROGRESS' || callStatus === 'ON_HOLD' || callStatus === 'RINGING') && (
          <div className="text-center py-3">
            <div className="w-16 h-16 rounded-full bg-indigo-50 border-4 border-indigo-100 text-indigo-600 flex items-center justify-center mx-auto mb-3">
              <User className="h-8 w-8" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">{callerName || 'Connected Call'}</h3>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{toNumber || fromNumber || '+1555019876'}</p>

            <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 bg-slate-100 rounded-full text-xs font-mono font-semibold text-slate-700">
              <Clock className="h-3.5 w-3.5 text-indigo-500" />
              <span>{callStatus === 'RINGING' ? 'Ringing...' : formatTimer(callDurationSeconds)}</span>
            </div>

            {callStatus === 'RINGING' ? (
              <div className="mt-6 flex justify-center gap-4">
                <button onClick={handleAnswerCall} className="p-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-full shadow-lg shadow-emerald-500/30 transition">
                  <PhoneCall className="h-5 w-5" />
                </button>
                <button onClick={handleEndCall} className="p-3 bg-rose-500 hover:bg-rose-600 text-white rounded-full shadow-lg shadow-rose-500/30 transition">
                  <PhoneOff className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                <div className="grid grid-cols-3 gap-2">
                  <button onClick={toggleMute} className={`p-2.5 rounded-xl border flex flex-col items-center gap-1 text-xs font-medium transition ${isMuted ? 'bg-amber-50 border-amber-300 text-amber-700' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}>
                    {isMuted ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                    <span>{isMuted ? 'Unmute' : 'Mute'}</span>
                  </button>
                  <button onClick={handleToggleHold} className={`p-2.5 rounded-xl border flex flex-col items-center gap-1 text-xs font-medium transition ${isOnHold ? 'bg-amber-50 border-amber-300 text-amber-700' : 'border-slate-200 text-slate-700 hover:bg-slate-50'}`}>
                    {isOnHold ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                    <span>{isOnHold ? 'Resume' : 'Hold'}</span>
                  </button>
                  <button onClick={() => setIsTransferring(!isTransferring)} className="p-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 flex flex-col items-center gap-1 text-xs font-medium transition">
                    <ArrowRightLeft className="h-4 w-4" />
                    <span>Transfer</span>
                  </button>
                </div>

                {isTransferring && (
                  <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-left">
                    <p className="text-[11px] font-semibold text-slate-600">Transfer Target (Extension or Queue)</p>
                    <input
                      type="text"
                      placeholder="e.g. 104 or Tier 2 Support"
                      value={transferTarget}
                      onChange={(e) => setTransferTarget(e.target.value)}
                      className="w-full text-xs px-2.5 py-1.5 bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                    <div className="flex gap-2">
                      <button onClick={handleEndCall} className="flex-1 py-1 bg-indigo-600 text-white rounded text-xs font-semibold">Cold Transfer</button>
                      <button onClick={handleEndCall} className="flex-1 py-1 bg-slate-200 text-slate-700 rounded text-xs font-semibold">Warm Transfer</button>
                    </div>
                  </div>
                )}

                <button onClick={handleEndCall} className="w-full py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-xl shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 text-xs transition">
                  <PhoneOff className="h-4 w-4" /> End Active Call
                </button>
              </div>
            )}
          </div>
        )}

        {/* State 2: After Call Work Wrap-Up & Disposition Form */}
        {callStatus === 'AFTER_CALL_WORK' && (
          <div className="space-y-3 py-1 text-left">
            <div className="flex items-center gap-2 text-amber-600 bg-amber-50 px-3 py-1.5 rounded-lg text-xs font-semibold">
              <CheckCircle2 className="h-4 w-4" />
              <span>Call Ended. Complete Wrap-Up</span>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-700 block mb-1">Outcome Disposition</label>
              <select
                value={dispositionCode}
                onChange={(e) => setDispositionCode(e.target.value)}
                className="w-full text-xs px-2.5 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="INTERESTED">Interested in Proposal</option>
                <option value="RESOLVED">Query Resolved Successfully</option>
                <option value="CALLBACK_REQUESTED">Callback Requested</option>
                <option value="NOT_INTERESTED">Not Interested</option>
                <option value="ESCALATED_TIER_2">Escalated to Tier 2</option>
                <option value="WRONG_NUMBER">Wrong Number</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-700 block mb-1">Wrap-up Notes</label>
              <textarea
                rows={3}
                placeholder="Key takeaways and next action items..."
                value={dispositionNotes}
                onChange={(e) => setDispositionNotes(e.target.value)}
                className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              onClick={handleSubmitDisposition}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-xs shadow-md shadow-emerald-600/30 transition"
            >
              Save Disposition &amp; Next Call
            </button>
          </div>
        )}

        {/* State 3: Dialpad Ready State */}
        {!callStatus && (
          <div>
            <div className="relative mb-3">
              <input
                type="text"
                placeholder="Enter phone number..."
                value={dialNumber}
                onChange={(e) => setDialNumber(e.target.value)}
                className="w-full text-center text-lg font-mono font-bold tracking-wider py-2 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              {dialNumber && (
                <button onClick={() => setDialNumber('')} className="absolute right-3 top-3 text-slate-400 hover:text-slate-600">
                  <Delete className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* Dialpad Matrix */}
            <div className="grid grid-cols-3 gap-2">
              {['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'].map((d) => (
                <button
                  key={d}
                  onClick={() => handleDigitClick(d)}
                  className="py-2.5 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-600 border border-slate-200 rounded-xl text-sm font-bold font-mono transition"
                >
                  {d}
                </button>
              ))}
            </div>

            <button
              onClick={handleInitiateCall}
              disabled={!dialNumber}
              className="w-full mt-3 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 text-xs transition"
            >
              <Phone className="h-4 w-4" /> Place Outbound Call
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
