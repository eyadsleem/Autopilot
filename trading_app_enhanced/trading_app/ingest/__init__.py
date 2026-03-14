"""
Audio ingest utilities.

This subpackage defines abstractions for streaming audio from various
sources such as local files, network streams or capture devices. Real
implementations should yield raw audio bytes along with precise
timestamps for synchronisation with transcription.
"""

from .audio_source import AudioSource  # noqa: F401
from .ffmpeg_capture import FFmpegAudioSource  # noqa: F401
