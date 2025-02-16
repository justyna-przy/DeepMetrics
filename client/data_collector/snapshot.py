from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List

@dataclass
class Device:
    device_name: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Snapshot:
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    devices: List[Device] = field(default_factory=list)
