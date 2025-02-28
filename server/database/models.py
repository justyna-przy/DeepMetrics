# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Aggregator(Base):
    __tablename__ = 'aggregators'

    aggregator_id = Column(Integer, primary_key=True, server_default=text("nextval('aggregators_aggregator_id_seq'::regclass)"))
    guid = Column(UUID, nullable=False, unique=True)
    name = Column(Text, nullable=False, index=True)


class MetricDefinition(Base):
    __tablename__ = 'metric_definitions'

    metric_def_id = Column(Integer, primary_key=True, server_default=text("nextval('metric_definitions_metric_def_id_seq'::regclass)"))
    metric_name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(True), nullable=False, server_default=text("now()"))


class Device(Base):
    __tablename__ = 'devices'

    device_id = Column(Integer, primary_key=True, server_default=text("nextval('devices_device_id_seq'::regclass)"))
    aggregator_id = Column(ForeignKey('aggregators.aggregator_id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(Text, nullable=False)

    aggregator = relationship('Aggregator')


class DeviceSnapshot(Base):
    __tablename__ = 'device_snapshots'
    __table_args__ = (
        Index('idx_device_snapshots_device_time', 'device_id', 'snapshot_time'),
    )

    device_snapshot_id = Column(Integer, primary_key=True, server_default=text("nextval('device_snapshots_device_snapshot_id_seq'::regclass)"))
    device_id = Column(ForeignKey('devices.device_id', ondelete='CASCADE'), nullable=False)
    snapshot_time = Column(DateTime(True), nullable=False)

    device = relationship('Device')


class MetricValue(Base):
    __tablename__ = 'metric_values'
    __table_args__ = (
        Index('idx_metric_values_def_snapshot', 'metric_def_id', 'device_snapshot_id'),
    )

    metric_value_id = Column(Integer, primary_key=True, server_default=text("nextval('metric_values_metric_value_id_seq'::regclass)"))
    device_snapshot_id = Column(ForeignKey('device_snapshots.device_snapshot_id', ondelete='CASCADE'), nullable=False)
    metric_def_id = Column(ForeignKey('metric_definitions.metric_def_id', ondelete='CASCADE'), nullable=False)
    metric_value = Column(Float(53), nullable=False)

    device_snapshot = relationship('DeviceSnapshot')
    metric_def = relationship('MetricDefinition')
