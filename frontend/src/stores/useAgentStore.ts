import { create } from 'zustand';
import { AgentState, BreakType, UserProfile } from '@/lib/types';

interface AgentStore {
  user: UserProfile | null;
  agentState: AgentState;
  breakType: BreakType | null;
  stateDurationSeconds: number;
  
  setUser: (user: UserProfile | null) => void;
  setAgentState: (state: AgentState, breakType?: BreakType | null) => void;
  incrementStateDuration: () => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  user: null,
  agentState: 'AVAILABLE',
  breakType: null,
  stateDurationSeconds: 0,

  setUser: (user) => set({ user }),
  setAgentState: (agentState, breakType = null) => set({ agentState, breakType, stateDurationSeconds: 0 }),
  incrementStateDuration: () => set((state) => ({ stateDurationSeconds: state.stateDurationSeconds + 1 })),
}));
