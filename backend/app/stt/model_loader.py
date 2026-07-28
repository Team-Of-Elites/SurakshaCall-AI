"""
model_loader.py — Task O-07: faster-whisper Singleton Loader

Loads the faster-whisper model once on application startup.
Supports GPU acceleration (CUDA float16) on RTX 3060 and falls back to CPU (int8) if needed.
"""

from typing import Any
import numpy as np


class WhisperModelLoader:
    _instance: Any = None
    _loaded_device: str = "none"
    _loaded_compute_type: str = "none"
    _load_error: str | None = None

    @classmethod
    def get_model(
        cls,
        model_size: str = "small",
        preferred_device: str = "cuda",
        preferred_compute_type: str = "float16",
    ) -> tuple[Any | None, str, str]:
        if cls._instance is not None:
            return cls._instance, cls._loaded_device, cls._loaded_compute_type

        if preferred_device == "cuda":
            try:
                from faster_whisper import WhisperModel
                instance = WhisperModel(
                    model_size,
                    device="cuda",
                    compute_type=preferred_compute_type,
                )
                # Verify CUDA capability at runtime (check cublas/cudnn DLLs)
                dummy = np.zeros(16000, dtype=np.int16)
                import io, wave
                buf = io.BytesIO()
                with wave.open(buf, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(dummy.tobytes())
                list(instance.transcribe(io.BytesIO(buf.getvalue()), beam_size=1)[0])

                cls._instance = instance
                cls._loaded_device = "cuda"
                cls._loaded_compute_type = preferred_compute_type
                return cls._instance, cls._loaded_device, cls._loaded_compute_type
            except Exception as exc:
                cls._load_error = f"CUDA runtime check failed ({exc}). Falling back to CPU."

        try:
            from faster_whisper import WhisperModel
            cls._instance = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
            )
            cls._loaded_device = "cpu"
            cls._loaded_compute_type = "int8"
            return cls._instance, cls._loaded_device, cls._loaded_compute_type
        except Exception as exc:
            cls._load_error = f"CPU Whisper load failed: {str(exc)}"
            return None, "error", str(exc)

    @classmethod
    def get_cpu_model(cls, model_size: str = "small") -> tuple[Any | None, str, str]:
        cls.reset()
        return cls.get_model(model_size=model_size, preferred_device="cpu", preferred_compute_type="int8")

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._loaded_device = "none"
        cls._loaded_compute_type = "none"
        cls._load_error = None

