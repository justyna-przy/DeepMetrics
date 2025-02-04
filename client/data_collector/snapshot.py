# snapshot.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

@dataclass
class Snapshot:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Optionally validate or transform data here if needed
        pass
