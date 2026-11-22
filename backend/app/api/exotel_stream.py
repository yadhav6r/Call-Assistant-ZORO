"""Bidirectional Exotel to OpenAI Realtime audio relay.

Exotel's call flow must play an AI disclosure and obtain the caller's consent
before it enters the Voicebot Applet configured with this WebSocket URL.
Audio is streamed for the live call only; this module does not record it.
"""

import asyncio
import base64
import hmac
import json
import time
from urllib.parse import quote

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.asyncio.client import connect as websocket_connect
from websockets.exceptions import ConnectionClosed

from app.config import get_settings

router = APIRouter(prefix="/api/v1/telephony/exotel", tags=["telephony"])

SAMPLE_RATE = 24000
PLAYBACK_CHUNK_BYTES = 4800  # 100 ms of mono PCM16 at 24 kHz; Exotel requires 320-byte multiples.
AI_INSTRUCTIONS = """You are ZORO, an AI assistant answering a call for the owner. The caller has already heard a clear AI disclosure and opted in before this stream began. Speak briefly and naturally. Speak English or Kannada, matching the caller's language; if unclear, ask which they prefer. Never claim to be the owner or a human. Do not claim to have contacted the owner or completed any action. You may collect a short message and say it will be passed to the owner. Do not disclose private information, make promises or commitments, give financial/legal/medical advice, make purchases, or contact anyone. For emergencies, tell the caller to contact local emergency services directly. If asked to stop, say goodbye and end politely."""


def _is_expected_basic_auth(websocket: WebSocket, username: str, password: str) -> bool:
    authorization = websocket.headers.get("authorization", "")
    scheme, _, encoded = authorization.partition(" ")
    if scheme.lower() != "basic" or not encoded:
        return False
    try:
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return False
    expected = f"{username}:{password}"
    return hmac.compare_digest(decoded, expected)


async def _send_model_session(ai_socket) -> None:
    await ai_socket.send(
        json.dumps(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "output_modalities": ["audio"],
                    "audio": {
                        "input": {
                            "format": {"type": "audio/pcm", "rate": SAMPLE_RATE},
                            "turn_detection": {"type": "semantic_vad"},
                        },
                        "output": {
                            "format": {"type": "audio/pcm", "rate": SAMPLE_RATE},
                            "voice": get_settings().openai_realtime_voice,
                        },
                    },
                    "instructions": AI_INSTRUCTIONS,
                },
            }
        )
    )


async def _relay_exotel_to_ai(exotel: WebSocket, ai_socket, stream_sid: str) -> None:
    while True:
        message = json.loads(await exotel.receive_text())
        event = message.get("event")
        if event == "stop":
            return
        if event == "media":
            media = message.get("media", {})
            payload = media.get("payload")
            if payload:
                await ai_socket.send(
                    json.dumps({"type": "input_audio_buffer.append", "audio": payload})
                )
        elif event == "dtmf":
            digit = message.get("dtmf", {}).get("digit")
            if digit == "*":
                return
        elif event == "clear":
            # Caller speech has interrupted playback; discard any pending OpenAI output.
            await exotel.send_json({"event": "clear", "stream_sid": stream_sid})


async def _relay_ai_to_exotel(exotel: WebSocket, ai_socket, stream_sid: str) -> None:
    pending = bytearray()
    sequence = 1
    chunk_number = 1
    start = time.monotonic()

    async def send_audio_chunk(chunk: bytes) -> None:
        nonlocal sequence, chunk_number
        if time.monotonic() - start > get_settings().live_call_max_seconds:
            return
        payload = base64.b64encode(chunk).decode("ascii")
        await exotel.send_json(
            {
                "event": "media",
                "sequence_number": sequence,
                "stream_sid": stream_sid,
                "media": {
                    "chunk": chunk_number,
                    "timestamp": str((chunk_number - 1) * 100),
                    "payload": payload,
                },
            }
        )
        sequence += 1
        chunk_number += 1

    async for raw_event in ai_socket:
        message = json.loads(raw_event)
        event_type = message.get("type")
        if event_type == "error":
            raise RuntimeError("Realtime voice service returned an error")
        if event_type == "input_audio_buffer.speech_started":
            await exotel.send_json({"event": "clear", "stream_sid": stream_sid})
            pending.clear()
        elif event_type == "response.output_audio.delta":
            pending.extend(base64.b64decode(message.get("delta", ""), validate=True))
            while len(pending) >= PLAYBACK_CHUNK_BYTES:
                if time.monotonic() - start > get_settings().live_call_max_seconds:
                    return
                chunk = bytes(pending[:PLAYBACK_CHUNK_BYTES])
                del pending[:PLAYBACK_CHUNK_BYTES]
                await send_audio_chunk(chunk)
        elif event_type == "response.output_audio.done" and pending:
            # Exotel needs a minimum 100 ms packet; pad the last short model chunk with silence.
            tail = bytes(pending[:PLAYBACK_CHUNK_BYTES])
            tail += bytes(PLAYBACK_CHUNK_BYTES - len(tail))
            pending.clear()
            await send_audio_chunk(tail)


@router.websocket("/stream")
async def exotel_voicebot_stream(websocket: WebSocket) -> None:
    settings = get_settings()
    if (
        not settings.live_calls_enabled
        or not settings.exotel_stream_username
        or not settings.exotel_stream_password
        or not settings.openai_api_key
        or not _is_expected_basic_auth(
            websocket,
            settings.exotel_stream_username.get_secret_value(),
            settings.exotel_stream_password.get_secret_value(),
        )
    ):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    try:
        # Exotel sends connected and then start before any audio media.
        stream_sid = None
        while stream_sid is None:
            message = json.loads(await websocket.receive_text())
            if message.get("event") == "stop":
                return
            if message.get("event") != "start":
                continue
            start = message.get("start", {})
            media_format = start.get("media_format", {})
            sample_rate = int(media_format.get("sample_rate", 0))
            encoding = str(media_format.get("encoding", "")).lower()
            if sample_rate != SAMPLE_RATE or encoding not in {
                "raw",
                "raw/slin",
                "slin",
                "slin16",
                "linear16",
                "pcm16",
                "audio/pcm",
            }:
                await websocket.close(code=1003, reason="Unsupported Exotel audio format")
                return
            stream_sid = str(message.get("stream_sid") or start.get("stream_sid") or "")
            if not stream_sid:
                await websocket.close(code=1003, reason="Missing stream identifier")
                return

        model = quote(settings.openai_realtime_model, safe="")
        url = f"wss://api.openai.com/v1/realtime?model={model}"
        async with websocket_connect(
            url,
            additional_headers={"Authorization": f"Bearer {settings.openai_api_key.get_secret_value()}"},
            open_timeout=10,
            close_timeout=2,
            max_size=2**20,
        ) as ai_socket:
            await _send_model_session(ai_socket)
            upstream = asyncio.create_task(_relay_exotel_to_ai(websocket, ai_socket, stream_sid))
            downstream = asyncio.create_task(_relay_ai_to_exotel(websocket, ai_socket, stream_sid))
            timeout = asyncio.create_task(asyncio.sleep(settings.live_call_max_seconds))
            done, pending = await asyncio.wait(
                {upstream, downstream, timeout}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                task.result()
    except (WebSocketDisconnect, ConnectionClosed, asyncio.CancelledError):
        return
    except Exception:
        # Do not expose provider errors, caller audio or secrets to logs or callers.
        try:
            await websocket.close(code=1011, reason="Call assistant temporarily unavailable")
        except RuntimeError:
            pass
