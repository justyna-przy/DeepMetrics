export interface DataPoint {
  time: string;
  value: number;
}

export interface Metric {
  metricName: string;
  displayType: string;
  data: DataPoint[];
}

export interface Device {
  deviceId: number;
  deviceName: string;
  lastUpdated?: string | null;
  metrics?: Metric[];
}

export interface Aggregator {
  aggregatorId: number;
  aggregatorName: string;
  devices: Device[];
}
