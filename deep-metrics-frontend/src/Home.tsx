import React from 'react';
import DeviceCard from './components/DeviceCard';
import GraphedMetric from './components/GraphedMetric';
import AggregatorCard from './components/AggregatorCard';
import TableMetric from './components/TableMetric';

const aggregatorName = "Justyna's Laptop";
const deviceList = [
  { deviceId: 1, deviceName: 'Laptop A' },
  { deviceId: 2, deviceName: 'Laptop B' },
  { deviceId: 3, deviceName: 'Laptop C' },
  // ...
];

const sampleData = [
  { time: '10:00', value: 30 },
  { time: '10:05', value: 45 },
  { time: '10:10', value: 28 },
  { time: '10:15', value: 50 },
  // ...
];

const handleMetricClick = (metricName: string) => {
  console.log(`Clicked on ${metricName}`);
}

const handleSelectDevice = (deviceId: number) => {
  console.log(`Selected device ${deviceId}`);
}

const Home: React.FC = () => {
  return (
    <AggregatorCard
      aggregatorName={aggregatorName}
      devices={deviceList}
      onSelectDevice={handleSelectDevice}
    >
      <DeviceCard deviceName="Device A" lastUpdated="2025-03-01 14:05:00">
        <GraphedMetric metricName="CPU Usage Percentage (%)" data={sampleData} yMax={100} onClick={handleMetricClick}/>
        <GraphedMetric metricName="Memory Usage (%)" data={sampleData} yMax={100} onClick={handleMetricClick}/>
        <GraphedMetric metricName="Memory Usage (%)" data={sampleData} yMax={100} onClick={handleMetricClick}/>
        <GraphedMetric metricName="Memory Usage (%)" data={sampleData} yMax={100} onClick={handleMetricClick}/>
      </DeviceCard>

      <DeviceCard deviceName="Device B" lastUpdated="2025-03-01 13:50:00">
        <GraphedMetric metricName="Temperature (°C)" data={sampleData} yMax={100} />
        <TableMetric metricName="Fan Speed (RPM)" value={2000} onClick={handleMetricClick}/>
      </DeviceCard>

      <DeviceCard deviceName="Device C" lastUpdated="2025-03-01 13:50:00">
        <GraphedMetric metricName="Temperature (°C)" data={sampleData} yMax={100} />
      </DeviceCard>
    </AggregatorCard>
  );
};

export default Home;

