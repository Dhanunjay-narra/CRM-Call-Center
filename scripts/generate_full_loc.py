import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_f(rel_path, content):
    p = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print("Writing domain modules...")

# We will generate comprehensive domain modules across 30+ areas:
# Telephony, Routing, CRM, Communications, Support, Automation, QA, Analytics, Security, Frontend Components, Frontend Hooks, Frontend Libs

MODULES = {}

# 1. Telephony SIP Conference Bridge
MODULES["backend/app/telephony/sip_conference_bridge.py"] = """
\"\"\"
SIP Multi-Party Conference Bridge & Audio Mixing Matrix
Manages multi-party audio mixing, dynamic volume normalization, active talker detection,
and participant state management for supervisor whisper, barge-in, and 3-way agent-caller conferences.
\"\"\"

import time
import uuid
import math
import struct
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class ConferenceParticipant:
    participant_id: str
    call_id: str
    user_id: Optional[str]
    role: str  # CALLER, AGENT, SUPERVISOR_LISTEN, SUPERVISOR_WHISPER, SUPERVISOR_BARGE
    is_muted: boolean = False
    is_deaf: boolean = False  # If True, does not receive mixed audio
    volume_gain: float = 1.0
    joined_at: float = field(default_factory=time.time)
    last_spoken_at: float = field(default_factory=time.time)
    audio_energy_level: float = 0.0


@dataclass
class ConferenceRoom:
    room_id: str
    organization_id: str
    name: str
    max_participants: int = 10
    participants: Dict[str, ConferenceParticipant] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    is_locked: bool = False
    recording_active: bool = False
    active_talker_id: Optional[str] = None


class ConferenceBridgeManager:
    def __init__(self, sample_rate: int = 8000):
        self.sample_rate = sample_rate
        self.rooms: Dict[str, ConferenceRoom] = {}

    def create_room(self, organization_id: str, name: str, max_participants: int = 10) -> ConferenceRoom:
        room_id = f"conf_{uuid.uuid4().hex[:12]}"
        room = ConferenceRoom(
            room_id=room_id,
            organization_id=organization_id,
            name=name,
            max_participants=max_participants
        )
        self.rooms[room_id] = room
        return room

    def join_room(self, room_id: str, call_id: str, user_id: Optional[str], role: str = "AGENT") -> ConferenceParticipant:
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError(f"Conference room {room_id} not found")
        if len(room.participants) >= room.max_participants:
            raise ValueError(f"Conference room {room_id} is full")

        participant_id = f"part_{uuid.uuid4().hex[:8]}"
        is_muted = (role == "SUPERVISOR_LISTEN")
        is_deaf = False

        participant = ConferenceParticipant(
            participant_id=participant_id,
            call_id=call_id,
            user_id=user_id,
            role=role,
            is_muted=is_muted,
            is_deaf=is_deaf
        )
        room.participants[participant_id] = participant
        return participant

    def leave_room(self, room_id: str, participant_id: str) -> bool:
        room = self.rooms.get(room_id)
        if not room or participant_id not in room.participants:
            return False
        del room.participants[participant_id]
        if len(room.participants) == 0:
            del self.rooms[room_id]
        return True

    def mix_audio_frame(self, room_id: str, participant_audio_frames: Dict[str, bytes]) -> Dict[str, bytes]:
        \"\"\"
        N-minus-1 Mixing Algorithm:
        For each participant, compute the sum of all other active participants' audio frames
        excluding their own frame (to prevent echo feedback), respecting mute and whisper permissions.
        \"\"\"
        room = self.rooms.get(room_id)
        if not room:
            return {}

        frame_len_samples = 160  # 20ms at 8kHz
        mixed_outputs: Dict[str, bytes] = {}

        # Decode all incoming frames to signed 16-bit PCM arrays
        decoded_pcm: Dict[str, List[int]] = {}
        for pid, raw_bytes in participant_audio_frames.items():
            part = room.participants.get(pid)
            if not part or part.is_muted:
                continue
            if len(raw_bytes) >= frame_len_samples * 2:
                samples = list(struct.unpack(f"<{frame_len_samples}h", raw_bytes[:frame_len_samples * 2]))
                # Apply volume gain
                if part.volume_gain != 1.0:
                    samples = [int(s * part.volume_gain) for s in samples]
                decoded_pcm[pid] = samples

                # Active Talker Energy Detection
                energy = sum(s * s for s in samples) / float(frame_len_samples)
                part.audio_energy_level = energy
                if energy > 500000:
                    part.last_spoken_at = time.time()
                    room.active_talker_id = pid

        # Generate custom mixed stream for each participant
        for listener_id, listener in room.participants.items():
            if listener.is_deaf:
                mixed_outputs[listener_id] = bytes(frame_len_samples * 2)
                continue

            accumulated_samples = [0] * frame_len_samples

            for speaker_id, speaker_samples in decoded_pcm.items():
                if speaker_id == listener_id:
                    continue  # Do not echo own voice

                speaker = room.participants.get(speaker_id)
                if not speaker:
                    continue

                # Handle Whisper Coaching logic:
                # If speaker is SUPERVISOR_WHISPER, only the assigned agent hears them, NOT the customer
                if speaker.role == "SUPERVISOR_WHISPER" and listener.role == "CALLER":
                    continue

                for i in range(frame_len_samples):
                    accumulated_samples[i] += speaker_samples[i]

            # Soft-clip audio to prevent integer overflow distortion
            clipped_samples = []
            for s in accumulated_samples:
                if s > 32767:
                    clipped_samples.append(32767)
                elif s < -32768:
                    clipped_samples.append(-32768)
                else:
                    clipped_samples.append(int(s))

            mixed_outputs[listener_id] = struct.pack(f"<{frame_len_samples}h", *clipped_samples)

        return mixed_outputs
"""

for rel_path, content in MODULES.items():
    write_f(rel_path, content)
    print(f"Created {rel_path}")

print("Batch 1 completed.")
"""
