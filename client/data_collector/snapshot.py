from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List

@dataclass
class DeviceSnapshot:
    device_name: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AggregatorData:
    guid: str
    name: str
    device_snapshots: List[DeviceSnapshot] = field(default_factory=list)
