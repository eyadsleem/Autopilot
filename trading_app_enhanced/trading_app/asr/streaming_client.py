"""
Stub implementation for a streaming ASR client.

The StreamingASRClient consumes an AudioSource and emits
TranscriptFragment objects asynchronously. This stub merely defines
the interface and yields no data; a production version would
communicate with a speech‑to‑text engine and emit partial and final
transcripts.
"""

from typing import AsyncIterator, AsyncIterable

from ..models import TranscriptFragment


class StreamingASRClient:
    """Base class for streaming speech‑to‑text clients."""

    def __init__(self, model_name: str = "stub") -> None:
        self.model_name = model_name

    async def transcribe(self, audio: AsyncIterable[bytes]) -> AsyncIterator[TranscriptFragment]:
        """
        Asynchronously transcribe audio chunks into TranscriptFragments.

        Parameters
        ----------
        audio : AsyncIterable[bytes]
            An asynchronous iterable yielding raw PCM bytes.

        Yields
        ------
        AsyncIterator[TranscriptFragment]
            Transcript fragments as they are produced. In this stub no
            fragments are yielded.
        """
        # A real implementation would feed audio to an ASR engine and
        # yield TranscriptFragment objects as the engine returns results.
        return
        yield  # pragma: no cover – this makes the function a generator
