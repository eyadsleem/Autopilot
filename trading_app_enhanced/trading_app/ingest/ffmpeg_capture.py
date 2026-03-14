"""
Stub implementation for capturing audio via FFmpeg.

This class serves as a placeholder for an FFmpeg‑based audio source.
In a real deployment, it would spawn an ffmpeg process to capture a
network stream or device and yield raw PCM audio chunks. Here, the
methods simply raise NotImplementedError to indicate that real
functionality must be provided by the integrator.
"""

from typing import Iterator, Tuple

from .audio_source import AudioSource


class FFmpegAudioSource(AudioSource):
    """Audio source that would capture audio using FFmpeg."""

    def __init__(self, source_id: str, url: str, chunk_duration: float = 0.25) -> None:
        super().__init__(source_id)
        self.url = url
        self.chunk_duration = chunk_duration

    def stream_chunks(self) -> Iterator[Tuple[bytes, float, float]]:
        """
        Yield audio chunks from the configured stream.

        This stub does not implement actual streaming and will raise
        NotImplementedError. In a production system, this method would
        run ffmpeg to pull audio, convert it to 16‑kHz mono PCM and
        yield byte chunks with timestamps.
        """
        raise NotImplementedError(
            "FFmpegAudioSource.stream_chunks is not implemented in this stub"
        )
