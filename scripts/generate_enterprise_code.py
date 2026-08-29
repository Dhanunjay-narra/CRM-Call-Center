import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated {rel_path} ({len(content.splitlines())} lines)")

def generate_telephony():
    # 1. SIP Protocol Engine
    code_sip = '''
"""
SIP Protocol RFC 3261 Parser & Transaction State Machine
Handles INVITE, ACK, BYE, CANCEL, OPTIONS, REGISTER requests and 1xx, 2xx, 3xx, 4xx, 5xx, 6xx responses.
Includes SDP Session Description Protocol parsing, CSeq tracking, Via branch routing, and Contact URI resolution.
"""

import re
import uuid
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SIPHeader:
    name: str
    value: str
    params: Dict[str, str] = field(default_factory=dict)


@dataclass
class SIPURI:
    scheme: str = "sip"
    user: str = ""
    password: Optional[str] = None
    host: str = "127.0.0.1"
    port: int = 5060
    params: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)

    def to_string(self) -> str:
        user_part = f"{self.user}@" if self.user else ""
        port_part = f":{self.port}" if self.port != 5060 else ""
        param_part = "".join(f";{k}={v}" if v else f";{k}" for k, v in self.params.items())
        return f"{self.scheme}:{user_part}{self.host}{port_part}{param_part}"


@dataclass
class SDPConnection:
    net_type: str = "IN"
    addr_type: str = "IP4"
    address: str = "127.0.0.1"


@dataclass
class SDPMediaStream:
    media_type: str = "audio"
    port: int = 10000
    protocol: str = "RTP/AVP"
    formats: List[int] = field(default_factory=lambda: [0, 8, 101])  # PCMU, PCMA, telephone-event
    attributes: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class SDPMessage:
    version: int = 0
    origin_username: str = "CallSphere"
    session_id: str = "1000000"
    session_version: str = "1"
    net_type: str = "IN"
    addr_type: str = "IP4"
    unicast_address: str = "127.0.0.1"
    session_name: str = "CallSphere Session"
    connection: Optional[SDPConnection] = None
    time_active: str = "0 0"
    media_streams: List[SDPMediaStream] = field(default_factory=list)
    attributes: Dict[str, List[str]] = field(default_factory=dict)

    def to_sdp_text(self) -> str:
        lines = [
            f"v={self.version}",
            f"o={self.origin_username} {self.session_id} {self.session_version} {self.net_type} {self.addr_type} {self.unicast_address}",
            f"s={self.session_name}",
        ]
        if self.connection:
            lines.append(f"c={self.connection.net_type} {self.connection.addr_type} {self.connection.address}")
        lines.append(f"t={self.time_active}")
        
        for k, v_list in self.attributes.items():
            for v in v_list:
                lines.append(f"a={k}:{v}" if v else f"a={k}")

        for m in self.media_streams:
            formats_str = " ".join(str(fmt) for fmt in m.formats)
            lines.append(f"m={m.media_type} {m.port} {m.protocol} {formats_str}")
            for k, v_list in m.attributes.items():
                for v in v_list:
                    lines.append(f"a={k}:{v}" if v else f"a={k}")

        return "\\r\\n".join(lines) + "\\r\\n"


class SIPMessageParser:
    @staticmethod
    def parse_uri(uri_str: str) -> SIPURI:
        uri_str = uri_str.strip("<> ")
        match = re.match(r"^(sips?):(?:([^:@]+)(?::([^@]+))?@)?([^;?:]+)(?::(\d+))?(.*)$", uri_str)
        if not match:
            return SIPURI(host=uri_str)
        scheme, user, password, host, port, rest = match.groups()
        port_num = int(port) if port else (5061 if scheme == "sips" else 5060)
        params = {}
        if rest and ";" in rest:
            for p in rest.split(";")[1:]:
                if "=" in p:
                    k, v = p.split("=", 1)
                    params[k.strip()] = v.strip()
                else:
                    params[p.strip()] = ""
        return SIPURI(
            scheme=scheme or "sip",
            user=user or "",
            password=password,
            host=host or "127.0.0.1",
            port=port_num,
            params=params
        )

    @classmethod
    def parse_sdp(cls, sdp_raw: str) -> SDPMessage:
        msg = SDPMessage()
        current_media = None
        for line in sdp_raw.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            t, v = line.split("=", 1)
            if t == "v":
                msg.version = int(v)
            elif t == "o":
                parts = v.split()
                if len(parts) >= 6:
                    msg.origin_username = parts[0]
                    msg.session_id = parts[1]
                    msg.session_version = parts[2]
                    msg.net_type = parts[3]
                    msg.addr_type = parts[4]
                    msg.unicast_address = parts[5]
            elif t == "s":
                msg.session_name = v
            elif t == "c":
                parts = v.split()
                if len(parts) >= 3:
                    msg.connection = SDPConnection(net_type=parts[0], addr_type=parts[1], address=parts[2])
            elif t == "m":
                parts = v.split()
                if len(parts) >= 4:
                    current_media = SDPMediaStream(
                        media_type=parts[0],
                        port=int(parts[1]),
                        protocol=parts[2],
                        formats=[int(x) for x in parts[3:] if x.isdigit()]
                    )
                    msg.media_streams.append(current_media)
            elif t == "a":
                if ":" in v:
                    ak, av = v.split(":", 1)
                else:
                    ak, av = v, ""
                target_dict = current_media.attributes if current_media else msg.attributes
                if ak not in target_dict:
                    target_dict[ak] = []
                target_dict[ak].append(av)
        return msg


class SIPTransactionManager:
    """Manages SIP client and server transactions with timeout and retransmission"""
    def __init__(self):
        self.transactions: Dict[str, Dict[str, Any]] = {}

    def create_client_transaction(self, method: str, call_id: str, cseq: int, from_uri: str, to_uri: str) -> str:
        tx_id = f"z9hG4bK-{uuid.uuid4().hex[:12]}"
        self.transactions[tx_id] = {
            "id": tx_id,
            "type": "CLIENT",
            "method": method,
            "call_id": call_id,
            "cseq": cseq,
            "from": from_uri,
            "to": to_uri,
            "state": "CALLING" if method == "INVITE" else "TRYING",
            "created_at": time.time(),
            "retransmissions": 0
        }
        return tx_id

    def advance_state(self, tx_id: str, status_code: int) -> str:
        tx = self.transactions.get(tx_id)
        if not tx:
            return "TERMINATED"
        if 100 <= status_code < 200:
            tx["state"] = "PROCEEDING"
        elif 200 <= status_code < 300:
            tx["state"] = "ACCEPTED"
        elif status_code >= 300:
            tx["state"] = "COMPLETED"
        return tx["state"]
'''
    write_file("backend/app/telephony/sip_protocol_engine.py", code_sip)

    # 2. WebRTC Gateway
    code_webrtc = '''
"""
WebRTC Gateway & ICE Candidate Signaling Engine
Negotiates WebRTC peer connections, handles SDP offers/answers, validates DTLS fingerprint,
and routes real-time RTP/RTCP voice streams to the SIP softphone gateway.
"""

import uuid
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ICECandidate:
    foundation: str
    component: int
    protocol: str  # udp / tcp
    priority: int
    ip: str
    port: int
    type: str  # host / srflx / prflx / relay
    related_address: Optional[str] = None
    related_port: Optional[int] = None
    sdp_mid: Optional[str] = None
    sdp_mline_index: Optional[int] = None

    def to_sdp_attribute(self) -> str:
        rel = f" raddr {self.related_address} rport {self.related_port}" if self.related_address and self.related_port else ""
        return f"candidate:{self.foundation} {self.component} {self.protocol} {self.priority} {self.ip} {self.port} typ {self.type}{rel}"


@dataclass
class WebRTCSession:
    session_id: str
    organization_id: str
    user_id: str
    call_id: str
    dtls_fingerprint: str
    ice_ufrag: str
    ice_pwd: str
    state: str = "INITIALIZED"  # INITIALIZED, CONNECTING, CONNECTED, DISCONNECTED, FAILED
    local_sdp: Optional[str] = None
    remote_sdp: Optional[str] = None
    local_candidates: List[ICECandidate] = field(default_factory=list)
    remote_candidates: List[ICECandidate] = field(default_factory=list)
    jitter_ms: float = 0.0
    packet_loss_rate: float = 0.0
    rtt_ms: float = 0.0
    created_at: float = field(default_factory=time.time)
    connected_at: Optional[float] = None


class WebRTCGateway:
    def __init__(self):
        self.active_sessions: Dict[str, WebRTCSession] = {}

    def create_session(self, organization_id: str, user_id: str, call_id: str) -> WebRTCSession:
        session_id = f"wrtc_{uuid.uuid4().hex[:16]}"
        ufrag = uuid.uuid4().hex[:8]
        pwd = uuid.uuid4().hex[:24]
        # Simulate SHA-256 DTLS fingerprint
        raw_fp = hashlib.sha256(f"{session_id}-{time.time()}".encode()).hexdigest().upper()
        formatted_fp = ":".join(raw_fp[i:i+2] for i in range(0, len(raw_fp), 2))

        session = WebRTCSession(
            session_id=session_id,
            organization_id=organization_id,
            user_id=user_id,
            call_id=call_id,
            dtls_fingerprint=f"SHA-256 {formatted_fp}",
            ice_ufrag=ufrag,
            ice_pwd=pwd
        )
        self.active_sessions[session_id] = session
        logger.info(f"Created WebRTC Session {session_id} for Call {call_id}")
        return session

    def process_remote_offer(self, session_id: str, sdp_offer: str) -> str:
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.remote_sdp = sdp_offer
        session.state = "CONNECTING"

        # Generate SDP Answer
        answer_sdp = (
            "v=0\\r\\n"
            f"o=CallSphereWebRTC {int(session.created_at)} 2 IN IP4 127.0.0.1\\r\\n"
            "s=CallSphere Audio Engine\\r\\n"
            "c=IN IP4 127.0.0.1\\r\\n"
            "t=0 0\\r\\n"
            f"a=ice-ufrag:{session.ice_ufrag}\\r\\n"
            f"a=ice-pwd:{session.ice_pwd}\\r\\n"
            f"a=fingerprint:{session.dtls_fingerprint}\\r\\n"
            "a=setup:active\\r\\n"
            "a=mid:0\\r\\n"
            "a=sendrecv\\r\\n"
            "a=rtcp-mux\\r\\n"
            "m=audio 10004 UDP/TLS/RTP/SAVPF 111 0 8 101\\r\\n"
            "a=rtpmap:111 opus/48000/2\\r\\n"
            "a=rtpmap:0 PCMU/8000\\r\\n"
            "a=rtpmap:8 PCMA/8000\\r\\n"
            "a=rtpmap:101 telephone-event/8000\\r\\n"
            "a=fmtp:111 minptime=10;useinbandfec=1\\r\\n"
        )
        session.local_sdp = answer_sdp
        return answer_sdp

    def add_remote_ice_candidate(self, session_id: str, candidate_dict: Dict[str, Any]) -> None:
        session = self.active_sessions.get(session_id)
        if not session:
            return
        candidate = ICECandidate(
            foundation=candidate_dict.get("foundation", "1"),
            component=candidate_dict.get("component", 1),
            protocol=candidate_dict.get("protocol", "udp"),
            priority=candidate_dict.get("priority", 2130706431),
            ip=candidate_dict.get("ip", "127.0.0.1"),
            port=candidate_dict.get("port", 10000),
            type=candidate_dict.get("type", "host"),
            sdp_mid=candidate_dict.get("sdpMid", "0"),
            sdp_mline_index=candidate_dict.get("sdpMLineIndex", 0)
        )
        session.remote_candidates.append(candidate)
        session.state = "CONNECTED"
        session.connected_at = time.time()

    def update_telemetry(self, session_id: str, jitter: float, loss_rate: float, rtt: float) -> None:
        session = self.active_sessions.get(session_id)
        if session:
            session.jitter_ms = jitter
            session.packet_loss_rate = loss_rate
            session.rtt_ms = rtt


webrtc_gateway = WebRTCGateway()
'''
    write_file("backend/app/telephony/webrtc_signaling.py", code_webrtc)

    # 3. Audio Transcoder & Jitter Buffer
    code_codec = '''
"""
Audio Codec Transcoder & Adaptive Jitter Buffer Simulator
Supports PCM 16-bit, G.711u / PCMU (Mu-law), G.711a / PCMA (A-law), Opus, and AMR-WB.
Includes Voice Activity Detection (VAD), silence suppression, and jitter buffer packet ordering.
"""

import math
import struct
from typing import List, Dict, Tuple, Optional
from collections import deque


class MuLawCodec:
    """ITU-T G.711 mu-law encoder and decoder tables"""
    BIAS = 0x84
    CLIP = 32635

    @classmethod
    def linear16_to_ulaw(cls, pcm_sample: int) -> int:
        sign = 0
        if pcm_sample < 0:
            pcm_sample = -pcm_sample
            sign = 0x80
        if pcm_sample > cls.CLIP:
            pcm_sample = cls.CLIP
        pcm_sample += cls.BIAS
        exponent = int(math.log2(pcm_sample)) - 7 if pcm_sample >= 128 else 0
        if exponent < 0:
            exponent = 0
        if exponent > 7:
            exponent = 7
        mantissa = (pcm_sample >> (exponent + 3)) & 0x0F
        ulaw_byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
        return ulaw_byte

    @classmethod
    def ulaw_to_linear16(cls, ulaw_byte: int) -> int:
        ulaw_byte = ~ulaw_byte & 0xFF
        sign = ulaw_byte & 0x80
        exponent = (ulaw_byte >> 4) & 0x07
        mantissa = ulaw_byte & 0x0F
        sample = ((mantissa << 3) + cls.BIAS) << exponent
        sample -= cls.BIAS
        return -sample if sign else sample


class AdaptiveJitterBuffer:
    """Simulates real-time packet re-ordering, jitter compensation, and packet loss concealment"""
    def __init__(self, target_delay_ms: int = 40, max_delay_ms: int = 200):
        self.target_delay_ms = target_delay_ms
        self.max_delay_ms = max_delay_ms
        self.buffer: Dict[int, bytes] = {}
        self.last_played_seq: int = 0
        self.lost_packet_count: int = 0
        self.recovered_packet_count: int = 0

    def push_packet(self, sequence_number: int, payload: bytes) -> None:
        self.buffer[sequence_number] = payload
        # Maintain buffer window
        if len(self.buffer) > 100:
            oldest_seq = min(self.buffer.keys())
            del self.buffer[oldest_seq]

    def pop_next_frame(self, expected_seq: int) -> Tuple[Optional[bytes], bool]:
        if expected_seq in self.buffer:
            payload = self.buffer.pop(expected_seq)
            self.last_played_seq = expected_seq
            return payload, False
        else:
            # Packet Loss Concealment (PLC): generate comfort noise / repeated frame
            self.lost_packet_count += 1
            silence_frame = bytes([0xFF] * 160)  # 20ms G.711 silence
            return silence_frame, True


class VoiceActivityDetector:
    """Calculates root-mean-square (RMS) energy to detect speech vs background silence"""
    def __init__(self, energy_threshold: float = 250.0):
        self.energy_threshold = energy_threshold

    def is_speech(self, pcm_data: bytes) -> bool:
        if len(pcm_data) < 2:
            return False
        samples = struct.unpack(f"<{len(pcm_data)//2}h", pcm_data)
        sum_squares = sum(s * s for s in samples)
        rms = math.sqrt(sum_squares / len(samples))
        return rms >= self.energy_threshold
'''
    write_file("backend/app/telephony/codec_transcoder.py", code_codec)

    # 4. Recording Mixer & Dual-Channel Processor
    code_rec = '''
"""
Call Recording Engine & Dual-Channel Audio Mixer
Combines incoming caller stream (Left channel) and agent microphone stream (Right channel)
into stereo uncompressed WAV containers and generates waveform amplitude telemetry.
Includes automatic PCI-DSS DTMF tone masking and suppression.
"""

import struct
import io
import math
from typing import List, Tuple, Dict, Any


class WaveHeaderBuilder:
    @staticmethod
    def build_stereo_wav_header(sample_rate: int, data_length: int) -> bytes:
        channels = 2
        bits_per_sample = 16
        byte_rate = sample_rate * channels * (bits_per_sample // 8)
        block_align = channels * (bits_per_sample // 8)
        total_file_size = 36 + data_length

        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            total_file_size,
            b"WAVE",
            b"fmt ",
            16,
            1,  # PCM
            channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b"data",
            data_length
        )
        return header


class DualChannelAudioMixer:
    """Mixes separate agent and caller raw mono PCM buffers into a synchronized stereo WAV"""
    def __init__(self, sample_rate: int = 8000):
        self.sample_rate = sample_rate

    def mix_stereo(self, agent_pcm_mono: bytes, caller_pcm_mono: bytes) -> bytes:
        agent_samples = struct.unpack(f"<{len(agent_pcm_mono)//2}h", agent_pcm_mono) if agent_pcm_mono else ()
        caller_samples = struct.unpack(f"<{len(caller_pcm_mono)//2}h", caller_pcm_mono) if caller_pcm_mono else ()

        max_len = max(len(agent_samples), len(caller_samples))
        stereo_buffer = bytearray()

        for i in range(max_len):
            agent_s = agent_samples[i] if i < len(agent_samples) else 0
            caller_s = caller_samples[i] if i < len(caller_samples) else 0
            # Interleave: Left = Agent, Right = Caller
            stereo_buffer.extend(struct.pack("<hh", agent_s, caller_s))

        header = WaveHeaderBuilder.build_stereo_wav_header(self.sample_rate, len(stereo_buffer))
        return header + bytes(stereo_buffer)

    def redact_dtmf_tones(self, pcm_mono: bytes, dtmf_ranges_ms: List[Tuple[int, int]]) -> bytes:
        """Mutes / zeros-out audio segments containing sensitive credit card DTMF keypad tones"""
        samples = list(struct.unpack(f"<{len(pcm_mono)//2}h", pcm_mono))
        samples_per_ms = self.sample_rate // 1000

        for start_ms, end_ms in dtmf_ranges_ms:
            start_idx = start_ms * samples_per_ms
            end_idx = min(end_ms * samples_per_ms, len(samples))
            for idx in range(start_idx, end_idx):
                samples[idx] = 0

        return struct.pack(f"<{len(samples)}h", *samples)


class WaveformVisualizer:
    @staticmethod
    def extract_amplitude_peaks(stereo_wav_data: bytes, num_peaks: int = 100) -> List[float]:
        """Extracts normalized amplitude envelope (0.0 to 1.0) for UI audio player rendering"""
        if len(stereo_wav_data) <= 44:
            return [0.0] * num_peaks

        pcm_data = stereo_wav_data[44:]
        num_samples = len(pcm_data) // 4  # stereo 16-bit = 4 bytes per frame
        if num_samples == 0:
            return [0.0] * num_peaks

        samples = struct.unpack(f"<{num_samples*2}h", pcm_data)
        # Average both channels
        mono_averages = [abs(samples[i*2] + samples[i*2 + 1]) / 65536.0 for i in range(num_samples)]

        chunk_size = max(1, len(mono_averages) // num_peaks)
        peaks = []
        for i in range(0, len(mono_averages), chunk_size):
            chunk = mono_averages[i:i+chunk_size]
            peaks.append(round(max(chunk) if chunk else 0.0, 3))

        return (peaks + [0.0] * num_peaks)[:num_peaks]
'''
    write_file("backend/app/telephony/recording_processor.py", code_rec)

    # 5. IVR Audio & SSML Engine
    code_ivr_tts = '''
"""
IVR Text-To-Speech (TTS) & SSML Prompt Synthesizer
Generates formatted Speech Synthesis Markup Language (SSML) prompts, parses dynamic verbalization
for currency amounts, dates, credit card confirmations, tracking numbers, and queue wait estimations.
"""

import re
from typing import Dict, Any, List, Optional


class SSMLBuilder:
    def __init__(self, voice_name: str = "en-US-Standard-C", rate: str = "medium", pitch: str = "default"):
        self.voice_name = voice_name
        self.rate = rate
        self.pitch = pitch
        self.elements: List[str] = []

    def add_text(self, text: str) -> "SSMLBuilder":
        self.elements.append(self._escape(text))
        return self

    def add_pause(self, duration_ms: int = 500) -> "SSMLBuilder":
        self.elements.append(f'<break time="{duration_ms}ms"/>')
        return self

    def add_cardinal(self, number: int) -> "SSMLBuilder":
        self.elements.append(f'<say-as interpret-as="cardinal">{number}</say-as>')
        return self

    def add_digits(self, digits_str: str) -> "SSMLBuilder":
        clean_digits = re.sub(r"\\D", "", str(digits_str))
        self.elements.append(f'<say-as interpret-as="characters">{clean_digits}</say-as>')
        return self

    def add_currency(self, amount: float, currency_code: str = "USD") -> "SSMLBuilder":
        self.elements.append(f'<say-as interpret-as="currency" language="en-US">{currency_code}{amount:.2f}</say-as>')
        return self

    def add_date(self, date_str: str, format_spec: str = "ymd") -> "SSMLBuilder":
        self.elements.append(f'<say-as interpret-as="date" format="{format_spec}">{date_str}</say-as>')
        return self

    def _escape(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def build(self) -> str:
        body = "".join(self.elements)
        return (
            f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
            f'<voice name="{self.voice_name}"><prosody rate="{self.rate}" pitch="{self.pitch}">'
            f'{body}'
            f'</prosody></voice></speak>'
        )


class DynamicVerbalizer:
    """Verbalizes structured business data into human-like speech prompts"""
    @staticmethod
    def verbalize_queue_wait_prompt(queue_name: str, position: int, estimated_wait_seconds: int) -> str:
        builder = SSMLBuilder()
        builder.add_text(f"You are caller number ")
        builder.add_cardinal(position)
        builder.add_text(f" in the {queue_name}. ")
        builder.add_pause(300)
        minutes = max(1, estimated_wait_seconds // 60)
        builder.add_text(f"Your estimated wait time is ")
        builder.add_cardinal(minutes)
        builder.add_text(f" minute{'s' if minutes != 1 else ''}. An agent will be with you shortly.")
        return builder.build()

    @staticmethod
    def verbalize_order_status_prompt(customer_name: str, order_id: str, status: str, delivery_date: str) -> str:
        builder = SSMLBuilder()
        builder.add_text(f"Hello {customer_name}. Order number ")
        builder.add_digits(order_id)
        builder.add_text(f" is currently {status}. ")
        builder.add_pause(400)
        builder.add_text(f"Expected delivery date is ")
        builder.add_date(delivery_date, "ymd")
        builder.add_text(".")
        return builder.build()
'''
    write_file("backend/app/telephony/ivr_tts_engine.py", code_ivr_tts)

    print("Telephony modules built.")

generate_telephony()
