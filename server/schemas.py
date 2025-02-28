from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class DeviceSnapshotIn(BaseModel):
    device_name: str
    timestamp: datetime
    metrics: Dict[str, Any]

class AggregatorIn(BaseModel):
    guid: str
    name: str
    device_snapshots: List[DeviceSnapshotIn] = []
