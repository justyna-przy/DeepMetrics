# routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database.db import get_db
from .schemas import AggregatorIn
from .database.models_ex import (
    AggregatorEx,
    DeviceEx,
    DeviceSnapshotEx,
    MetricDefinitionEx,
    MetricValueEx
)

router = APIRouter()

@router.post("/api/snapshots")
def create_aggregator_snapshot(agg_in: AggregatorIn, db: Session = Depends(get_db)):
    """
    Receives an AggregatorIn payload with a GUID, name, and device snapshots.
    Inserts/updates aggregator, devices, metric definitions, 
    then stores new snapshots and metric values.
    """

    # 1. Upsert aggregator by guid
    aggregator = db.query(AggregatorEx).filter_by(guid=agg_in.guid).first()
    if not aggregator:
        aggregator = AggregatorEx(guid=agg_in.guid, name=agg_in.name)
        db.add(aggregator)
        db.flush()
    else:
        # Optionally update aggregator name if it changed
        aggregator.name = agg_in.name

    # 2. For each device snapshot
    for ds_in in agg_in.device_snapshots:
        # Upsert device
        device = db.query(DeviceEx).filter_by(
            aggregator_id=aggregator.aggregator_id,
            name=ds_in.device_name
        ).first()
        if not device:
            device = DeviceEx(
                aggregator_id=aggregator.aggregator_id,
                name=ds_in.device_name
            )
            db.add(device)
            db.flush()

        # Create a new device snapshot
        snapshot = DeviceSnapshotEx(
            device_id=device.device_id,
            snapshot_time=ds_in.timestamp
        )
        db.add(snapshot)
        db.flush()

        # 3. For each metric in ds_in.metrics
        for metric_name, metric_value in ds_in.metrics.items():
            # Upsert metric definition
            metric_def = db.query(MetricDefinitionEx).filter_by(metric_name=metric_name).first()
            if not metric_def:
                metric_def = MetricDefinitionEx(metric_name=metric_name)
                db.add(metric_def)
                db.flush()

            # Insert metric value
            mv = MetricValueEx(
                device_snapshot_id=snapshot.device_snapshot_id,
                metric_def_id=metric_def.metric_def_id,
                metric_value=metric_value
            )
            db.add(mv)

    db.commit()
    return {"message": "Aggregator snapshot data saved successfully."}
