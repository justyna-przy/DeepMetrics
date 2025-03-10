from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Union, List

Numeric = Union[int, float]

@dataclass
class DeviceSnapshot:
    device_name: str
    metrics: Dict[str, Numeric] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def merge(self, other: "DeviceSnapshot"):
        """
        Merge metrics from another snapshot of the same device by overwriting metrics with new values.
        The timestamp is updated to the more recent snapshot.
        """
        if self.device_name != other.device_name:
            raise ValueError("Cannot merge snapshots from different devices.")
        
        self.metrics.update(other.metrics)
        
        if other.timestamp > self.timestamp:
            self.timestamp = other.timestamp

@dataclass
class AggregatorData:
    guid: str
    name: str
    device_snapshots: List[DeviceSnapshot] = field(default_factory=list)
