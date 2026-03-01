"""
Voice Module - STT (Whisper) + TTS (edge-tts padrão + clonagem opcional)
"""

import os
import tempfile
import asyncio
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
VOICE_SAMPLE = BASE_DIR / "voices" / "my_voice.wav"
CLONE_ENABLED_FLAG = BASE_DIR / "voices" / "clone_enabled"

# ─── STT ──────────────────────────────────────────────────────────────────────

async def transcribe_audio(audio_path: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_path)

def _transcribe_sync(audio_path: str) -> str:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("faster-whisper nao instalado: pip install faster-whisper")

    wav_path = audio_path + ".wav"
    converted = _convert_to_wav(audio_path, wav_path)
    transcribe_path = wav_path if converted else audio_path

    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(transcribe_path, language="pt")
        return " ".join([s.text for s in segments]).strip()
    finally:
        if converted and os.path.exists(wav_path):
            os.unlink(wav_path)

def _convert_to_wav(input_path: str, output_path: str) -> bool:
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path],
            capture_output=True, timeout=30
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(input_path)
        audio.set_frame_rate(16000).set_channels(1).export(output_path, format="wav")
        return True
    except Exception:
        pass

    return False

# ─── TTS ──────────────────────────────────────────────────────────────────────

async def synthesize_speech(text: str) -> str:
    """Usa voz clonada se habilitada, senão voz padrão PT-BR"""
    if CLONE_ENABLED_FLAG.exists() and VOICE_SAMPLE.exists():
        try:
            return await _synthesize_clone(text)
        except Exception as e:
            print(f"Clonagem falhou, usando voz padrão: {e}")

    return await _synthesize_edge(text)

async def _synthesize_edge(text: str) -> str:
    """Voz padrão - Microsoft Edge TTS, voz masculina brasileira"""
    try:
        import edge_tts
    except ImportError:
        raise ImportError("edge-tts nao instalado: pip install edge-tts")

    output_path = os.path.join(tempfile.gettempdir(), f"tts_{os.getpid()}.mp3")
    communicate = edge_tts.Communicate(text, voice="pt-BR-AntonioNeural")
    await communicate.save(output_path)
    return output_path

async def _synthesize_clone(text: str) -> str:
    """Clonagem de voz com XTTS (requer TTS instalado)"""
    try:
        from TTS.api import TTS
    except ImportError:
        raise ImportError("TTS nao instalado: pip install TTS")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _xtts_sync, text)

def _xtts_sync(text: str) -> str:
    from TTS.api import TTS
    output_path = os.path.join(tempfile.gettempdir(), f"tts_{os.getpid()}.wav")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    tts.tts_to_file(text=text, speaker_wav=str(VOICE_SAMPLE), language="pt", file_path=output_path)
    return output_path

def is_clone_enabled() -> bool:
    return CLONE_ENABLED_FLAG.exists() and VOICE_SAMPLE.exists()

def set_clone_enabled(enabled: bool):
    if enabled:
        CLONE_ENABLED_FLAG.touch()
    elif CLONE_ENABLED_FLAG.exists():
        CLONE_ENABLED_FLAG.unlink()

async def save_voice_sample(audio_path: str) -> bool:
    """Salva amostra de voz do usuário"""
    VOICE_SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    converted = _convert_to_wav(audio_path, str(VOICE_SAMPLE))
    if not converted:
        import shutil
        shutil.copy(audio_path, str(VOICE_SAMPLE))
    return True
