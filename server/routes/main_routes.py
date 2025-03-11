import logging
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
    MetricValueEx,
    MetricDisplayConfigEx
)
from sqlalchemy import func
from sqlalchemy.sql import text
from utils import BlockTimer, format_timestamp

router = APIRouter()

"""
    FastAPI is built around the concept of dependency injection.
    Depends(get_db) is a dependency that will provide a SQLAlchemy Session to the route function.
    The Session will be closed automatically in the finally clause when the route function returns.
    Each request will have its own Session instance.
"""

@router.post("/api/snapshots")
def create_aggregator_snapshot(agg_in: AggregatorIn, db: Session = Depends(get_db)):
    with BlockTimer("create_aggregator_snapshot", logger=logging.getLogger("uvicorn")):
        # Upsert aggregator by guid
        aggregator = db.query(AggregatorEx).filter_by(guid=agg_in.guid).first()
        if not aggregator:
            aggregator = AggregatorEx(guid=agg_in.guid, name=agg_in.name)
            db.add(aggregator)
            db.flush()  # ensures aggregator.aggregator_id is now assigned
        else:
            aggregator.name = agg_in.name

        # Bulk upsert devices (based on aggregator_id + device_name)
        device_names = {ds_in.device_name for ds_in in agg_in.device_snapshots}
        existing_devices = (
            db.query(DeviceEx)
              .filter(DeviceEx.aggregator_id == aggregator.aggregator_id)
              .filter(DeviceEx.name.in_(device_names))
              .all()
        )
        device_map = {dev.name: dev for dev in existing_devices}

        new_devices = []
        for dev_name in device_names:
            if dev_name not in device_map:
                dev_obj = DeviceEx(
                    aggregator_id=aggregator.aggregator_id,
                    name=dev_name
                )
                db.add(dev_obj)
                device_map[dev_name] = dev_obj
                new_devices.append(dev_obj)

        # Bulk upsert metric definitions
        all_metric_names = set()
        for ds_in in agg_in.device_snapshots:
            for metric_name in ds_in.metrics.keys():
                all_metric_names.add(metric_name)

        existing_mdefs = (
            db.query(MetricDefinitionEx)
              .filter(MetricDefinitionEx.metric_name.in_(all_metric_names))
              .all()
        )
        metricdef_map = {m.metric_name: m for m in existing_mdefs}

        new_mdefs = []
        for mname in all_metric_names:
            if mname not in metricdef_map:
                mdef_obj = MetricDefinitionEx(metric_name=mname)
                db.add(mdef_obj)
                metricdef_map[mname] = mdef_obj
                new_mdefs.append(mdef_obj)

        # Flush once so newly created aggregator, devices, metric defs get their IDs
        db.flush()

        # Upsert metric_display_config for each new metric definition
        if new_mdefs:  # only do a subquery if we created new metric defs
            new_def_ids = [md.metric_def_id for md in new_mdefs]
            existing_display = (
                db.query(MetricDisplayConfigEx)
                  .filter(MetricDisplayConfigEx.metric_def_id.in_(new_def_ids))
                  .all()
            )
            disp_map = {cfg.metric_def_id: cfg for cfg in existing_display}

            for md_obj in new_mdefs:
                if md_obj.metric_def_id not in disp_map:
                    disp_cfg = MetricDisplayConfigEx(metric_def_id=md_obj.metric_def_id)
                    db.add(disp_cfg)
                    disp_map[md_obj.metric_def_id] = disp_cfg
            db.flush()

        # Create device snapshots + metric values now that aggregator, devices, metric defs, and display configs are in place
        snapshot_objs = []
        metric_value_objs = []

        for ds_in in agg_in.device_snapshots:
            device = device_map[ds_in.device_name]
            snapshot = DeviceSnapshotEx(
                device_id=device.device_id,
                snapshot_time=ds_in.timestamp
            )
            db.add(snapshot)
            snapshot_objs.append(snapshot)

            for metric_name, metric_val in ds_in.metrics.items():
                mdef_obj = metricdef_map[metric_name]
                mv = MetricValueEx(
                    metric_def_id=mdef_obj.metric_def_id,
                    metric_value=metric_val
                )
                # Link to snapshot via relationship
                mv.device_snapshot = snapshot
                db.add(mv)
                metric_value_objs.append(mv)

        db.commit()

        return {"message": "Aggregator snapshot data saved successfully."}


@router.get("/api/overview")
def get_overview(
    db: Session = Depends(get_db),
    graph_limit: int = Query(10, description="How many snapshots for 'graph' metrics"),
    aggregator: str = Query("all", description="Specific aggregator name or 'all'"),
    device: str = Query("all", description="Specific device name or 'all'")
):
    """
    Calls the get_overview_dynamic(p_graph_limit) DB function,
    which returns up to 'graph_limit' rows for display_type='graph',
    else 1 row for 'row' metrics.

    Then we filter aggregator/device in Python if not 'all',
    and return the same aggregator->devices->metrics structure.
    """
    with BlockTimer("overview", logger=logging.getLogger("uvicorn")):
        raw_sql = "SELECT * FROM get_overview(:glimit)"
        params = {"glimit": graph_limit}

        rows = db.execute(text(raw_sql), params).fetchall()  # each row is a row proxy with columns

        # 2) Filter in Python if aggregator != "all" or device != "all"
        filtered = []
        for row in rows:
            if aggregator != "all" and row["aggregator_name"] != aggregator:
                continue
            if device != "all" and row["device_name"] != device:
                continue
            filtered.append(row)

        # aggregator -> device -> metrics
        aggregator_map = {}
        for r in filtered:
            agg_id = r["aggregator_id"]
            agg_name = r["aggregator_name"]
            dev_id = r["device_id"]
            dev_name = r["device_name"]
            snap_time = r["snapshot_time"]
            metric_def_id = r["metric_def_id"]
            metric_name = r["metric_name"]
            metric_value = r["metric_value"]
            display_type = r["display_type"]

            # aggregator
            if agg_id not in aggregator_map:
                aggregator_map[agg_id] = {
                    "aggregatorId": agg_id,
                    "aggregatorName": agg_name,
                    "devices": {}
                }

            dev_map = aggregator_map[agg_id]["devices"]
            if dev_id not in dev_map:
                dev_map[dev_id] = {
                    "deviceId": dev_id,
                    "deviceName": dev_name,
                    "lastUpdated": None,
                    "metrics": {}
                }

            # update lastUpdated 
            if snap_time is not None:
                device_info = dev_map[dev_id]
                if device_info["lastUpdated"] is None or snap_time > device_info["lastUpdated"]:
                    device_info["lastUpdated"] = snap_time

            # metrics
            metric_map = dev_map[dev_id]["metrics"]
            if metric_def_id not in metric_map:
                metric_map[metric_def_id] = {
                    "metricName": metric_name,
                    "displayType": display_type,
                    "data": []
                }

            metric_map[metric_def_id]["data"].append({
                "time": snap_time.isoformat() if snap_time else None,
                "value": metric_value
            })

        # Convert aggregator_map to final array structure
        result = []
        for agg_id, agg_info in aggregator_map.items():
            device_list = []
            for dev_id, dev_info in agg_info["devices"].items():
                # Convert metrics dictionary to a list
                metric_list = []
                for mdef_id, mval in dev_info["metrics"].items():
                    metric_list.append({
                        "metricName": mval["metricName"],
                        "displayType": mval["displayType"],
                        "data": mval["data"]
                    })

                device_list.append({
                    "deviceId": dev_info["deviceId"],
                    "deviceName": dev_info["deviceName"],
                    "lastUpdated": (format_timestamp(dev_info["lastUpdated"])
                                    if dev_info["lastUpdated"] else None),
                    "metrics": metric_list
                })

            result.append({
                "aggregatorId": agg_id,
                "aggregatorName": agg_info["aggregatorName"],
                "devices": device_list
            })

        return result


@router.get("/api/metrics/history")
def get_metric_history(
    metric_name: str = Query(..., description="Name of the metric to retrieve"),
    time_filter: str = Query("24h", description="Time range filter, e.g., '24h', '7d', '30d'"),
    sort: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Current page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = Depends(get_db)
):
    """
    Returns historical metric values (with pagination) for the specified metric_name,
    filtered by a time range (24h, 7d, or 30d).
    Also computes average and maximum metric values over the given time range.
    """
    with BlockTimer("get_metric_history", logger=logging.getLogger("uvicorn")):
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

        # 2. Locate the metric definition by metric_name
        metric_def = (
            db.query(MetricDefinitionEx)
            .filter_by(metric_name=metric_name)
            .first()
        )
        if not metric_def:
            raise HTTPException(status_code=404, detail="Metric not found")

        # 3. Build a base query that joins MetricValueEx -> DeviceSnapshotEx
        #    We no longer join aggregator/device since we don't need them.
        base_query = (
            db.query(MetricValueEx, DeviceSnapshotEx.snapshot_time)
            .join(DeviceSnapshotEx,
                  DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
            .filter(MetricValueEx.metric_def_id == metric_def.metric_def_id)
            .filter(DeviceSnapshotEx.snapshot_time >= start_time)
        )

        # 4. Counting total records (removing any ORDER BY)
        count_query = base_query.with_entities(func.count()).order_by(None)
        total_count = count_query.scalar()

        # 5. Sort order by snapshot_time asc/desc
        if sort not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="Invalid sort param, must be 'asc' or 'desc'")

        if sort == "asc":
            base_query = base_query.order_by(DeviceSnapshotEx.snapshot_time.asc())
        else:
            base_query = base_query.order_by(DeviceSnapshotEx.snapshot_time.desc())

        # 6. Pagination
        offset = (page - 1) * page_size
        paginated_results = base_query.offset(offset).limit(page_size).all()

        # 7. Calculate average and max over the full filtered range
        stats_query = (
            db.query(
                func.avg(MetricValueEx.metric_value).label("avg_value"),
                func.max(MetricValueEx.metric_value).label("max_value")
            )
            .join(DeviceSnapshotEx,
                  DeviceSnapshotEx.device_snapshot_id == MetricValueEx.device_snapshot_id)
            .filter(MetricValueEx.metric_def_id == metric_def.metric_def_id)
            .filter(DeviceSnapshotEx.snapshot_time >= start_time)
        )
        stats_result = stats_query.first()
        avg_value = stats_result.avg_value if stats_result and stats_result.avg_value is not None else 0
        max_value = stats_result.max_value if stats_result and stats_result.max_value is not None else 0

        # 8. Format the paginated rows
        rows = []
        for (metric_val, snap_time) in paginated_results:
            rows.append({
                "timestamp": format_timestamp(snap_time),
                "value": metric_val.metric_value
            })

        # 9. Return final JSON
        return {
            "metricName": metric_name,
            "timeFilter": time_filter,
            "sort": sort,
            "page": page,
            "pageSize": page_size,
            "totalCount": total_count,
            "averageValue": float(avg_value),
            "maxValue": float(max_value),
            "rows": rows,
        }


