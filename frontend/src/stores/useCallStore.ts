import { create } from 'zustand';
import { CallStatus } from '@/lib/types';

interface CallState {
  activeCallId: string | null;
  callStatus: CallStatus | null;
  fromNumber: string | null;
  toNumber: string | null;
  callerName: string | null;
  customerId: string | null;
  isOnHold: boolean;
  isMuted: boolean;
  callDurationSeconds: number;
  
  setActiveCall: (call: Partial<CallState>) => void;
  clearActiveCall: () => void;
  toggleHold: () => void;
  toggleMute: () => void;
  incrementDuration: () => void;
}

export const useCallStore = create<CallState>((set) => ({
  activeCallId: null,
  callStatus: null,
  fromNumber: null,
  toNumber: null,
  callerName: null,
  customerId: null,
  isOnHold: false,
  isMuted: false,
  callDurationSeconds: 0,

  setActiveCall: (call) => set((state) => ({ ...state, ...call })),
  clearActiveCall: () => set({
    activeCallId: null,
    callStatus: null,
    fromNumber: null,
    toNumber: null,
    callerName: null,
    customerId: null,
    isOnHold: false,
    isMuted: false,
    callDurationSeconds: 0,
  }),
  toggleHold: () => set((state) => ({ isOnHold: !state.isOnHold })),
  toggleMute: () => set((state) => ({ isMuted: !state.isMuted })),
  incrementDuration: () => set((state) => ({ callDurationSeconds: state.callDurationSeconds + 1 })),
}));
