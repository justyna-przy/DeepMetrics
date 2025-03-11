import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.db import get_db
from schemas import AggregatorIn
from database.models_ex import (
    AggregatorEx,
    DeviceEx,
    DeviceSnapshotEx,
    MetricDefinitionEx,
    MetricValueEx
)

router = APIRouter()

"""
    FastAPI is built around the concept of dependency injection.
    Depends(get_db) is a dependency that will provide a SQLAlchemy Session to the route function.
    The Session will be closed automatically in the finally clause when the route function returns.
    Each request will have its own Session instance.
"""

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


@router.get("/api/aggregators")
def list_aggregators(db: Session = Depends(get_db)):
    """
    Returns a simple list of all aggregators (id and name) for populating a dropdown.
    """
    aggs = db.query(AggregatorEx).all()
    return [
        {
            "aggregatorId": agg.aggregator_id,
            "aggregatorName": agg.name
        }
        for agg in aggs
    ]


@router.get("/api/aggregators/{aggregator_id}/devices")
def list_devices_for_aggregator(aggregator_id: int, db: Session = Depends(get_db)):
    """
    Returns a list of devices (id, name) under a specific aggregator.
    Pass aggregator_id = 0 or 'all' to handle the "all" case if you want.
    """
    if aggregator_id == 0:
        # or if aggregator_id is 'all', up to you
        # Return devices across ALL aggregators
        devices = db.query(DeviceEx).all()
    else:
        # Return devices for the specified aggregator
        agg = db.query(AggregatorEx).filter_by(aggregator_id=aggregator_id).first()
        if not agg:
            raise HTTPException(status_code=404, detail="Aggregator not found")
        devices = agg.devices  # via relationship

    return [
        {
            "deviceId": d.device_id,
            "deviceName": d.name
        }
        for d in devices
    ]




@router.get("/api/overview")
def get_overview(
    db: Session = Depends(get_db),
    aggregator: str = Query("all"),
    device: str = Query("all")
):
    """
    Returns aggregator(s) + device(s) + metric data.
    aggregator: "all" or aggregator ID (as string) or aggregator name
    device: "all" or device ID (as string) or device name
    """
    # 1. Figure out if aggregator == "all" or a specific aggregator
    aggregators = []
    if aggregator == "all":
        aggregators = db.query(AggregatorEx).all()
    else:
        # Depending on your UI, aggregator might be an ID or a name
        # Let's assume it's an integer ID in the query param for simplicity
        try:
            agg_id = int(aggregator)
            found = db.query(AggregatorEx).filter_by(aggregator_id=agg_id).first()
        except ValueError:
            # aggregator param is not an int, maybe it's a name
            found = db.query(AggregatorEx).filter_by(name=aggregator).first()
        if found:
            aggregators = [found]
        else:
            raise HTTPException(status_code=404, detail="Aggregator not found")

    result = []

    for agg in aggregators:
        agg_info = {
            "aggregatorId": agg.aggregator_id,
            "aggregatorName": agg.name,
            "devices": []
        }

        # 2. For each device in this aggregator, or if device != "all", only fetch that device
        if device == "all":
            selected_devices = agg.devices
        else:
            # Same logic: try int ID, else treat as name
            try:
                dev_id = int(device)
                selected_devices = [
                    d for d in agg.devices if d.device_id == dev_id
                ]
            except ValueError:
                # device param is not an int, maybe it's a device name
                selected_devices = [
                    d for d in agg.devices if d.name == device
                ]
            if not selected_devices:
                # If the user specified a specific device that doesn't belong
                # to this aggregator, skip or raise 404
                raise HTTPException(status_code=404, detail="Device not found")

        device_list = []
        for dev in selected_devices:
            # get last snapshot
            last_snap = (
                db.query(DeviceSnapshotEx)
                .filter_by(device_id=dev.device_id)
                .order_by(DeviceSnapshotEx.snapshot_time.desc())
                .first()
            )
            last_updated = last_snap.snapshot_time.isoformat() if last_snap else None

            dev_info = {
                "deviceId": dev.device_id,
                "deviceName": dev.name,
                "lastUpdated": last_updated,
                "metrics": []
            }

            # gather distinct metric definitions used by this device
            metric_defs = (
                db.query(MetricDefinitionEx)
                .join(MetricValueEx, MetricValueEx.metric_def_id == MetricDefinitionEx.metric_def_id)
                .join(DeviceSnapshotEx, DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
                .filter(DeviceSnapshotEx.device_id == dev.device_id)
                .distinct()
                .all()
            )

            # For each metric_def, decide row vs. graph
            for metric_def in metric_defs:
                # If you have a real display_config table, use that:
                # display_type = metric_def.display_config.display_type or "row"
                # For this example, let's guess based on name:
                display_type = "graph" if "Usage" in metric_def.metric_name else "row"
                limit = 10 if display_type == "graph" else 1

                recent_values = (
                    db.query(MetricValueEx)
                    .join(DeviceSnapshotEx, DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
                    .filter(DeviceSnapshotEx.device_id == dev.device_id)
                    .filter(MetricValueEx.metric_def_id == metric_def.metric_def_id)
                    .order_by(DeviceSnapshotEx.snapshot_time.desc())
                    .limit(limit)
                    .all()
                )

                # Reverse them so earliest is first
                data_points = []
                for mv in reversed(recent_values):
                    snap_time = mv.device_snapshot.snapshot_time.isoformat()
                    data_points.append({
                        "time": snap_time,
                        "value": mv.metric_value
                    })

                dev_info["metrics"].append({
                    "metricName": metric_def.metric_name,
                    "displayType": display_type,
                    "data": data_points
                })

            device_list.append(dev_info)

        agg_info["devices"] = device_list
        result.append(agg_info)

    logging.getLogger("uvicorn").info("Hello from uvicorn logger!")

    return result


@router.get("/api/metrics/history")
def get_metric_history(
    metric_name: str = Query(..., description="Name of the metric to retrieve"),
    aggregator_id: Optional[int] = Query(None, description="Optional aggregator ID filter"),
    device_id: Optional[int] = Query(None, description="Optional device ID filter"),
    time_filter: str = Query("24h", description="Time range filter, e.g., '24h', '7d', '30d'"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Current page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db)
):
    """
    Returns historical metric values (with pagination) for the specified metric_name.
    Also computes average and maximum metric values over the given time range.
    Optionally filters by aggregator_id and/or device_id.
    """

    # 1. Determine start_time based on time_filter
    now = datetime.utcnow()
    if time_filter == "24h":
        start_time = now - timedelta(hours=24)
    elif time_filter == "7d":
        start_time = now - timedelta(days=7)
    elif time_filter == "30d":
        start_time = now - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid time_filter provided.")

    # 2. Locate the metric definition
    metric_def = (
        db.query(MetricDefinitionEx)
        .filter_by(metric_name=metric_name)
        .first()
    )
    if not metric_def:
        raise HTTPException(status_code=404, detail="Metric not found")

    # 3. Build a base query that joins MetricValueEx -> DeviceSnapshotEx -> DeviceEx -> AggregatorEx
    base_query = (
        db.query(MetricValueEx, DeviceSnapshotEx.snapshot_time)
        .join(DeviceSnapshotEx, DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
        .join(DeviceEx, DeviceEx.device_id == DeviceSnapshotEx.device_id)
        .join(AggregatorEx, AggregatorEx.aggregator_id == DeviceEx.aggregator_id)
        .filter(MetricValueEx.metric_def_id == metric_def.metric_def_id)
        .filter(DeviceSnapshotEx.snapshot_time >= start_time)
    )

    # 4. Apply aggregator/device filters if provided
    if aggregator_id is not None:
        base_query = base_query.filter(AggregatorEx.aggregator_id == aggregator_id)
    if device_id is not None:
        base_query = base_query.filter(DeviceEx.device_id == device_id)

    # 5. Create a separate query for counting, removing any ORDER BY
    count_query = base_query.with_entities(func.count()).order_by(None)
    total_count = count_query.scalar()

    # 6. Now apply the sort order to our base_query for actual data retrieval
    if sort not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort param, must be 'asc' or 'desc'")

    if sort == "asc":
        base_query = base_query.order_by(DeviceSnapshotEx.snapshot_time.asc())
    else:
        base_query = base_query.order_by(DeviceSnapshotEx.snapshot_time.desc())

    # 7. Apply pagination
    offset = (page - 1) * page_size
    paginated_results = base_query.offset(offset).limit(page_size).all()

    # 8. Calculate average and max over the full filtered range
    stats_query = (
        db.query(
            func.avg(MetricValueEx.metric_value).label("avg_value"),
            func.max(MetricValueEx.metric_value).label("max_value")
        )
        .join(DeviceSnapshotEx, DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
        .join(DeviceEx, DeviceEx.device_id == DeviceSnapshotEx.device_id)
        .join(AggregatorEx, AggregatorEx.aggregator_id == DeviceEx.aggregator_id)
        .filter(MetricValueEx.metric_def_id == metric_def.metric_def_id)
        .filter(DeviceSnapshotEx.snapshot_time >= start_time)
    )

    if aggregator_id is not None:
        stats_query = stats_query.filter(AggregatorEx.aggregator_id == aggregator_id)
    if device_id is not None:
        stats_query = stats_query.filter(DeviceEx.device_id == device_id)

    stats_result = stats_query.first()
    avg_value = stats_result.avg_value if stats_result and stats_result.avg_value is not None else 0
    max_value = stats_result.max_value if stats_result and stats_result.max_value is not None else 0

    # 9. Format the paginated rows
    rows = []
    for (metric_val, snap_time) in paginated_results:
        rows.append({
            "timestamp": snap_time.isoformat(),
            "value": metric_val.metric_value
        })

    return {
        "metricName": metric_name,
        "timeFilter": time_filter,
        "aggregatorId": aggregator_id,
        "deviceId": device_id,
        "sort": sort,
        "page": page,
        "pageSize": page_size,
        "totalCount": total_count,
        "averageValue": float(avg_value),
        "maxValue": float(max_value),
        "rows": rows,
    }