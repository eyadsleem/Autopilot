"""
Definition of simple rule patterns for mention detection.

Rules provide a name, a list of compiled regular expressions to scan for,
an optional minimum confidence threshold, and an optional speaker whitelist.
These are intentionally static and can be modified or extended by users
deploying the trading application to suit their own signal vocabulary.
"""

import re
from typing import List, Dict, Any


Rule = Dict[str, Any]

RULES: List[Rule] = [
    {
        "name": "hawkish_rate_signal",
        "patterns": [
            re.compile(r"\bdo not expect cuts\b", re.IGNORECASE),
            re.compile(r"\bno need for cuts\b", re.IGNORECASE),
            re.compile(r"\bhigher for longer\b", re.IGNORECASE),
            re.compile(r"\binflation remains sticky\b", re.IGNORECASE),
        ],
        # Minimum confidence threshold for the transcript fragment.
        "min_confidence": 0.82,
        # Restrict which speakers can trigger this rule (None means any).
        "speaker_whitelist": {"Jerome Powell", "Chair Powell", "FOMC Member"},
    },
    {
        "name": "shutdown_avoided_signal",
        "patterns": [
            re.compile(r"\bshutdown averted\b", re.IGNORECASE),
            re.compile(r"\bdeal reached\b", re.IGNORECASE),
            re.compile(r"\bcontinuing resolution agreed\b", re.IGNORECASE),
        ],
        "min_confidence": 0.80,
        "speaker_whitelist": None,
    },
    {
        "name": "nominee_support_signal",
        "patterns": [
            re.compile(r"\bsupport\s+for\s+nomination\b", re.IGNORECASE),
            re.compile(r"\bconfirm\s+the\s+nominee\b", re.IGNORECASE),
        ],
        "min_confidence": 0.80,
        "speaker_whitelist": None,
    },
]
