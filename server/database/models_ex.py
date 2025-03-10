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


class AggregatorEx(BaseAggregator):
    __tablename__ = "aggregators"

    devices = relationship(
        "DeviceEx",
        back_populates="aggregator",
        cascade="all, delete-orphan",
        overlaps="devices"
    )

    def get_device_by_name(self, name: str):
        """Convenience method to find a device by name among this aggregator's devices."""
        return next((d for d in self.devices if d.name == name), None)


class DeviceEx(BaseDevice):
    __tablename__ = "devices"

    # The base 'Device' often has aggregator = relationship('Aggregator').
    # We add overlaps="aggregator" to tell SQLAlchemy it's okay that both classes manage the same FK.
    aggregator = relationship(
        "AggregatorEx",
        back_populates="devices",
        overlaps="aggregator"
    )

    device_snapshots = relationship(
        "DeviceSnapshotEx",
        back_populates="device",
        cascade="all, delete-orphan",
        overlaps="device_snapshots"
    )

    def get_latest_snapshot(self):
        """
        Return the most recent snapshot for this device, or None if none exist.
        """
        if not self.device_snapshots:
            return None
        # Sort by snapshot_time descending
        return max(self.device_snapshots, key=lambda s: s.snapshot_time)


class DeviceSnapshotEx(BaseDeviceSnapshot):
    __tablename__ = "device_snapshots"

    device = relationship(
        "DeviceEx",
        back_populates="device_snapshots",
        overlaps="device"
    )

    metric_values = relationship(
        "MetricValueEx",
        back_populates="device_snapshot",
        cascade="all, delete-orphan",
        overlaps="metric_values"
    )

    def get_metric_value(self, metric_name: str):
        """
        Return the MetricValueEx object for a given metric_name, or None if not found.
        """
        for mv in self.metric_values:
            if mv.metric_def and mv.metric_def.metric_name == metric_name:
                return mv
        return None


class MetricDefinitionEx(BaseMetricDefinition):
    __tablename__ = "metric_definitions"

    metric_values = relationship(
        "MetricValueEx",
        back_populates="metric_def",
        cascade="all, delete-orphan",
        overlaps="metric_values"
    )

    display_config = relationship(
        "MetricDisplayConfigEx",
        back_populates="metric_def",
        uselist=False,         
        cascade="all, delete-orphan",
        overlaps="display_config"
    )


class MetricValueEx(BaseMetricValue):
    __tablename__ = "metric_values"

    device_snapshot = relationship(
        "DeviceSnapshotEx",
        back_populates="metric_values",
        overlaps="device_snapshot"
    )
    metric_def = relationship(
        "MetricDefinitionEx",
        back_populates="metric_values",
        overlaps="metric_def"
    )


class MetricDisplayConfigEx(BaseMetricDisplayConfig):
    __tablename__ = "metric_display_config"

    metric_def = relationship(
        "MetricDefinitionEx",
        back_populates="display_config",
        uselist=False,
        overlaps="metric_def"
    )
