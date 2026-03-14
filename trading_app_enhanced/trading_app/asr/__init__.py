"""
Streaming ASR integration stubs.

This subpackage defines interfaces and stubs for integrating a
streaming speech‑to‑text system. Real implementations should connect
to a provider such as Whisper, Vosk, or a cloud ASR service and emit
TranscriptFragment instances as partial and final results are produced.
"""

from .streaming_client import StreamingASRClient  # noqa: F401
