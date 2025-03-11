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

class CommandIn(BaseModel):
    aggregator_name: str
    device_name: str
    command: str

class CommandAck(BaseModel):
    command_ids: List[int]
