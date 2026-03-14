"""
Abstract base classes for audio ingestion.

The trading application requires audio to be ingested and chunked into
small frames for real‑time transcription. An audio source yields tuples
containing raw bytes and timestamps indicating the start and end of the
segment. Subclasses can wrap ffmpeg, pyaudio, or other libraries to
provide audio data.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Tuple


class AudioSource(ABC):
    """Base class for any streaming audio source."""

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    @abstractmethod
    def stream_chunks(self) -> Iterator[Tuple[bytes, float, float]]:
        """
        Yield successive audio chunks.

        Returns
        -------
        Iterator[Tuple[bytes, float, float]]
            Yields tuples of (pcm_bytes, start_ts, end_ts). Timestamps
            are expressed in seconds since the epoch.
        """
        raise NotImplementedError
