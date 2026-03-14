"""
Real‑time mention detection logic.

The MentionDetector consumes TranscriptFragment objects, maintains a
rolling window of recent fragments, and applies configurable rules to
detect signal events. It enforces confidence thresholds, optional speaker
filters, and deduplicates repeated triggers within a cooldown window.
"""

import hashlib
from collections import deque
from typing import Optional, Deque

from .models import TranscriptFragment, SignalEvent
from .rules import RULES


class MentionDetector:
    """
    Sliding‑window detector for salient phrases in streaming transcripts.

    Detection proceeds as follows:
      1. Each new fragment is appended to an internal buffer (max length
         configurable). The buffer holds the most recent transcript text.
      2. Rules are evaluated in order; each defines one or more compiled
         regex patterns, a minimum confidence threshold, and an optional
         speaker whitelist.
      3. When a pattern matches the concatenated window, a deduplication
         key is computed. If the same key has been triggered within the
         past `dedup_seconds`, the match is suppressed.
      4. Otherwise, a SignalEvent is emitted.
    """

    def __init__(self, max_buffer: int = 20, dedup_seconds: float = 10.0) -> None:
        self.buffer: Deque[TranscriptFragment] = deque(maxlen=max_buffer)
        self.recent_keys: dict[str, float] = {}
        self.dedup_seconds = dedup_seconds

    def push(self, fragment: TranscriptFragment) -> None:
        """Append a transcript fragment to the rolling buffer."""
        self.buffer.append(fragment)

    def _window_text(self) -> str:
        """Concatenate the text of all buffered fragments."""
        return " ".join(frag.text for frag in self.buffer)

    def process(self, fragment: TranscriptFragment) -> Optional[SignalEvent]:
        """
        Ingest a new fragment and attempt to detect a signal event.

        Parameters
        ----------
        fragment :
            The incoming transcript fragment.

        Returns
        -------
        Optional[SignalEvent]
            A signal event if a pattern matches and passes deduplication;
            otherwise ``None``.
        """
        self.push(fragment)
        text_window = self._window_text()

        for rule in RULES:
            # Ensure the fragment meets the confidence requirement.
            if fragment.confidence < rule.get("min_confidence", 0.0):
                continue
            # Check speaker whitelist if provided.
            speaker_whitelist = rule.get("speaker_whitelist")
            if speaker_whitelist is not None:
                if fragment.speaker is None or fragment.speaker not in speaker_whitelist:
                    continue
            # Evaluate each compiled pattern against the concatenated window.
            for pattern in rule["patterns"]:
                if pattern.search(text_window):
                    # Build a deduplication key from rule name, source and pattern.
                    dedup_key = f"{rule['name']}|{fragment.source_id}|{pattern.pattern}"
                    last_ts = self.recent_keys.get(dedup_key)
                    if last_ts is not None and (fragment.received_ts - last_ts) < self.dedup_seconds:
                        # Do not emit a new event if the same pattern fired recently.
                        return None
                    # Record the timestamp for deduplication.
                    self.recent_keys[dedup_key] = fragment.received_ts
                    # Generate a deterministic event identifier.
                    event_id = hashlib.md5(
                        f"{dedup_key}|{fragment.received_ts}".encode("utf-8")
                    ).hexdigest()[:12]
                    return SignalEvent(
                        event_id=event_id,
                        source_id=fragment.source_id,
                        event_class=rule["name"],
                        text_window=text_window[-500:],  # limit the text window length
                        confidence=fragment.confidence,
                        detected_ts=fragment.received_ts,
                        is_provisional=not fragment.is_final,
                        speaker=fragment.speaker,
                        trigger_terms=[pattern.pattern],
                    )
        # No matches found
        return None
