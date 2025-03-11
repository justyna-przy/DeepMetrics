from sqlalchemy.orm import relationship
from database.models import (
    Base,
    Aggregator as BaseAggregator,
    Device as BaseDevice,
    DeviceSnapshot as BaseDeviceSnapshot,
    MetricDefinition as BaseMetricDefinition,
    MetricValue as BaseMetricValue,
    MetricDisplayConfig as BaseMetricDisplayConfig
)

"""
    This file contains the extended models with relationships defined.
"""

class AggregatorEx(BaseAggregator):
    __tablename__ = "aggregators" # Ensures both the base and extended class refer to the same table

    devices = relationship(
        "DeviceEx",
        back_populates="aggregator",
        cascade="all, delete-orphan"
    )

    def get_device_by_name(self, name: str):
        return next((d for d in self.devices if d.name == name), None)

class DeviceEx(BaseDevice):
    __tablename__ = "devices"

    aggregator = relationship(
        "AggregatorEx",
        back_populates="devices"
    )

    device_snapshots = relationship(
        "DeviceSnapshotEx",
        back_populates="device",
        cascade="all, delete-orphan"
    )

    def get_latest_snapshot(self):
        if not self.device_snapshots:
            return None
        return max(self.device_snapshots, key=lambda s: s.snapshot_time)

class DeviceSnapshotEx(BaseDeviceSnapshot):
    __tablename__ = "device_snapshots"

    device = relationship(
        "DeviceEx",
        back_populates="device_snapshots"
    )
    metric_values = relationship(
        "MetricValueEx",
        back_populates="device_snapshot",
        cascade="all, delete-orphan"
    )

    def get_metric_value(self, metric_name: str):
        for mv in self.metric_values:
            if mv.metric_def and mv.metric_def.metric_name == metric_name:
                return mv
        return None

class MetricDefinitionEx(BaseMetricDefinition):
    __tablename__ = "metric_definitions"

    metric_values = relationship(
        "MetricValueEx",
        back_populates="metric_def",
        cascade="all, delete-orphan"
    )
    display_config = relationship(
        "MetricDisplayConfigEx",
        back_populates="metric_def",
        uselist=False, # Means its a one-to-one relationship
        cascade="all, delete-orphan"
    )

class MetricValueEx(BaseMetricValue):
    __tablename__ = "metric_values"

    device_snapshot = relationship(
        "DeviceSnapshotEx",
        back_populates="metric_values"
    )
    metric_def = relationship(
        "MetricDefinitionEx",
        back_populates="metric_values"
    )

class MetricDisplayConfigEx(BaseMetricDisplayConfig):
    __tablename__ = "metric_display_config"

    metric_def = relationship(
        "MetricDefinitionEx",
        back_populates="display_config",
        uselist=False
    )
