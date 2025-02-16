from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime, timezone
import json

router = APIRouter()

# Global variable to store the last snapshot
last_snapshot = None

# Define a Pydantic model for a Device.
class Device(BaseModel):
    device_name: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Define a Pydantic model for a Snapshot.
class Snapshot(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    devices: List[Device] = Field(default_factory=list)

@router.post("/api/snapshots")
async def receive_snapshot(snapshot: Snapshot):
    """
    Endpoint to receive snapshots from the aggregator.
    """
    global last_snapshot
    last_snapshot = snapshot
    # For debugging/logging purposes, print the received data.
    print("Received snapshot:", snapshot.model_dump())
    
    # You can add processing logic here (e.g., storing in a database).
    return {"message": "Snapshot received", "device_count": len(snapshot.devices)}

@router.get("/api/snapshot")
async def get_snapshot():
    """
    GET endpoint that returns the last received snapshot in pretty printed JSON.
    """
    if last_snapshot is None:
        content = json.dumps({"message": "No snapshot available."}, indent=4)
        return Response(content=content, media_type="application/json")
    
    # Convert the snapshot to a dict, then dump it as pretty printed JSON.
    content = json.dumps(last_snapshot.dict(), indent=4, default=str)
    return Response(content=content, media_type="application/json")
