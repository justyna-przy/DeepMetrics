import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AggregatorCard from "../components/AggregatorCard";
import DeviceCard from "../components/DeviceCard";
import GraphedMetric from "../components/GraphedMetric";
import RowMetric from "../components/RowMetric";

// Maybe move this to graphed metric component?
// shit this already exists lol
interface DataPoint {
  time: string;
  value: number;
}

interface Metric {
  metricName: string;
  displayType: string; // "graph" or "row"/"table"
  data: DataPoint[];
}

interface Device {
  deviceId: number;
  deviceName: string;
  lastUpdated: string | null;
  metrics: Metric[];
}

interface Aggregator {
  aggregatorId: number;
  aggregatorName: string;
  devices: Device[];
}

const HomePage: React.FC = () => {
  const [aggregators, setAggregators] = useState<Aggregator[]>([]);
  const navigate = useNavigate();

  // Polling example: fetch data on mount + repeat every 10 seconds
  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        // Example: fetch "all aggregators/all devices" overview
        const resp = await fetch("http://127.0.0.1:8000/api/overview?aggregator=all&device=all");
        if (!resp.ok) {
          console.error("Failed to fetch aggregator data:", resp.statusText);
          return;
        }
        const data = await resp.json();
        if (isMounted) {
          // Expecting data in form: [ { aggregatorId, aggregatorName, devices: [...] }, ... ]
          setAggregators(data);
        }
      } catch (err) {
        console.error("Error fetching aggregator data:", err);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 10_000); // poll every 10s

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  // Optional: function to handle metric clicks
  const handleMetricClick = (metricName: string) => {
    navigate(`/metric/${encodeURIComponent(metricName)}`);
  };

  // Optional: function to handle device selection (from some child component)
  const handleSelectDevice = (deviceId: number) => {
    console.log(`Selected device ${deviceId}`);
    // Possibly fetch only that device's data, or update route, etc.
  };

  return (
    <>
      {aggregators.length === 0 ? (
        <p>Loading...</p>
      ) : (
        aggregators.map((agg) => (
          <AggregatorCard
            key={agg.aggregatorId}
            aggregatorName={agg.aggregatorName}
            devices={agg.devices.map((d) => ({
              deviceId: d.deviceId,
              deviceName: d.deviceName
            }))}
            onSelectDevice={handleSelectDevice}
          >
            {/* Render each DeviceCard inside the aggregator */}
            {agg.devices.map((dev) => (
              <DeviceCard
                key={dev.deviceId}
                deviceName={dev.deviceName}
                lastUpdated={dev.lastUpdated || "N/A"}
              >
                {/* For each metric, choose GraphedMetric or TableMetric */}
                {dev.metrics.map((metric, index) => {
                  if (metric.displayType === "graph") {
                    // Transform data into the shape <GraphedMetric> expects
                    const graphData = metric.data.map((dp) => ({
                      time: dp.time,
                      value: dp.value
                    }));
                    return (
                      <GraphedMetric
                        key={index}
                        metricName={metric.metricName}
                        data={graphData}
                        yMax={100} // or compute from your data?
                        onClick={handleMetricClick}
                      />
                    );
                  } else {
                    // For "row" or "table" metrics, only 1 data point typically
                    const latestValue =
                      metric.data.length > 0 ? metric.data[metric.data.length - 1].value : 0;
                    return (
                      <RowMetric
                        key={index}
                        metricName={metric.metricName}
                        value={latestValue}
                        onClick={handleMetricClick}
                      />
                    );
                  }
                })}
              </DeviceCard>
            ))}
          </AggregatorCard>
        ))
      )}
    </>
  );
};

export default HomePage;
