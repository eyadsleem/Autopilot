"""
Audit logging utilities for the trading application.

The AuditLogger collects and records events flowing through the system,
including incoming transcript fragments, detected signal events, trade
intents and the results of order executions. In this simple
implementation the logger appends records to an in‑memory list and
optionally writes structured logs to a file. Production deployments
should integrate with a more robust logging or telemetry system.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from .models import TranscriptFragment, SignalEvent, TradeIntent


class AuditLogger:
    """
    Collect and persist audit logs for diagnostics and compliance.

    Parameters
    ----------
    logfile : Optional[str], optional
        Path to a JSONL file to append logs to. If ``None``, logs are
        kept only in memory. Default ``None``.
    """

    def __init__(self, logfile: Optional[str] = None) -> None:
        self.logfile = logfile
        self.records: List[Dict[str, Any]] = []
        # Create the log file directory if it does not exist.
        if logfile is not None:
            os.makedirs(os.path.dirname(logfile), exist_ok=True)

    def _append(self, record: Dict[str, Any]) -> None:
        """Append a record to the in‑memory list and optionally write to disk."""
        self.records.append(record)
        if self.logfile is not None:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

    def log_fragment(self, fragment: TranscriptFragment) -> None:
        """Record a transcript fragment received by the system."""
        self._append(
            {
                "type": "transcript.fragment",
                "timestamp": datetime.utcnow().isoformat(),
                "source_id": fragment.source_id,
                "fragment_id": fragment.fragment_id,
                "text": fragment.text,
                "audio_start_ts": fragment.audio_start_ts,
                "audio_end_ts": fragment.audio_end_ts,
                "received_ts": fragment.received_ts,
                "confidence": fragment.confidence,
                "is_final": fragment.is_final,
                "speaker": fragment.speaker,
                "revision_of": fragment.revision_of,
            }
        )

    def log_signal(self, event: SignalEvent) -> None:
        """Record a detected signal event."""
        self._append(
            {
                "type": "signal.detected",
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": event.event_id,
                "source_id": event.source_id,
                "event_class": event.event_class,
                "text_window": event.text_window,
                "confidence": event.confidence,
                "detected_ts": event.detected_ts,
                "is_provisional": event.is_provisional,
                "speaker": event.speaker,
                "trigger_terms": event.trigger_terms,
            }
        )

    def log_intent(self, intent: TradeIntent) -> None:
        """Record a trade intent before execution."""
        self._append(
            {
                "type": "trade.intent",
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": intent.event_id,
                "market_ticker": intent.market_ticker,
                "side": intent.side,
                "contracts": intent.contracts,
                "price": intent.limit_price_cents,
                "reason": intent.reason_code,
                "created_ts": intent.created_ts,
            }
        )

    def log_execution(self, result: Dict[str, Any]) -> None:
        """Record the result of an execution attempt."""
        self._append(
            {
                "type": "trade.result",
                "timestamp": datetime.utcnow().isoformat(),
                **result,
            }
        )

    def clear(self) -> None:
        """Clear all in‑memory records (does not truncate logfile)."""
        self.records.clear()