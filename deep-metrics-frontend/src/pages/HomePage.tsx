// src/pages/HomePage.tsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AggregatorCard from "../components/AggregatorCard";
import DeviceCard from "../components/DeviceCard";
import GraphedMetric from "../components/GraphedMetric";
import RowMetric from "../components/RowMetric";
import { SyncLoader } from "react-spinners";
import { config } from "../config/config";
import { Aggregator} from "../data_models";

const HomePage: React.FC = () => {
  const [aggregators, setAggregators] = useState<Aggregator[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDevices, setSelectedDevices] = useState<
    Record<string, string>
  >({});
  const navigate = useNavigate();

  // 1) On first mount, fetch aggregator=all & device=all to discover all aggregators.
  useEffect(() => {
    let isMounted = true;
    const initialFetch = async () => {
      try {
        const resp = await fetch(
          `${config.apiBaseUrl}${config.endpoints.overview}?aggregator=all&device=all`
        );

        if (!resp.ok) {
          throw new Error(
            `Failed to fetch aggregator data: ${resp.statusText}`
          );
        }
        const data = await resp.json(); // Expecting an array of aggregator objects
        if (isMounted) {
          setAggregators(data);
        }
      } catch (err) {
        console.error("Error fetching aggregator data:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    initialFetch();
    return () => {
      isMounted = false;
    };
  }, []);

  // 2) Poll every 10 seconds for each aggregator using aggregatorName and selected device.
  //    We remove `aggregators` from the dependency array to avoid re-creating the interval on every poll.
  useEffect(() => {
    if (loading || aggregators.length === 0) return;

    let isMounted = true;
    const pollData = async () => {
      try {
        const newAggregators: Aggregator[] = [];
        for (const agg of aggregators) {
          // Use the selected device for this aggregator if set; otherwise "all"
          const deviceName = selectedDevices[agg.aggregatorName] ?? "all";
          const url = `https://deepmetrics.onrender.com/api/overview?aggregator=${encodeURIComponent(
            agg.aggregatorName
          )}&device=${encodeURIComponent(deviceName)}`;
          const resp = await fetch(url);
          if (!resp.ok) {
            throw new Error(`Failed aggregator fetch: ${resp.statusText}`);
          }
          const data = await resp.json(); // typically an array with one aggregator object
          if (data.length > 0) {
            newAggregators.push(data[0]);
          } else {
            newAggregators.push({
              aggregatorId: agg.aggregatorId,
              aggregatorName: agg.aggregatorName,
              devices: [],
            });
          }
        }
        if (isMounted) {
          setAggregators(newAggregators);
        }
      } catch (err) {
        console.error("Error polling aggregator data:", err);
      }
    };

    // Call pollData immediately and then every 10 seconds.
    pollData();
    const intervalId = setInterval(pollData, 10000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [loading, selectedDevices]);

  // When a metric is clicked, navigate to its detailed page.
  const handleMetricClick = (metricName: string) => {
    navigate(`/metric/${encodeURIComponent(metricName)}`);
  };

  /**
   * Called by each AggregatorCard when a device is selected.
   * If deviceId === 0, it means "All devices" are selected.
   * Otherwise, find the device name in the aggregator and store it.
   */
  const handleSelectDevice = (aggregatorName: string, deviceId: number) => {
    if (deviceId === 0) {
      setSelectedDevices((prev) => ({ ...prev, [aggregatorName]: "all" }));
      return;
    }
    const agg = aggregators.find((a) => a.aggregatorName === aggregatorName);
    if (!agg) return;
    const device = agg.devices.find((d) => d.deviceId === deviceId);
    if (!device) return;
    setSelectedDevices((prev) => ({
      ...prev,
      [aggregatorName]: device.deviceName,
    }));
  };

  if (loading) {
    return (
      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "2rem" }}
      >
        <SyncLoader color="#6936d7" />
      </div>
    );
  }

  if (aggregators.length === 0) {
    return <p>No aggregators found.</p>;
  }

  return (
    <>
      {aggregators.map((agg) => (
        <AggregatorCard
          key={agg.aggregatorId}
          aggregatorName={agg.aggregatorName}
          // Pass devices as an array of { deviceId, deviceName }
          devices={agg.devices.map((d) => ({
            deviceId: d.deviceId,
            deviceName: d.deviceName,
          }))}
          onSelectDevice={(deviceId) =>
            handleSelectDevice(agg.aggregatorName, deviceId)
          }
        >
          {/* Render each DeviceCard for the aggregator */}
          {agg.devices.map((dev) => (
            <DeviceCard
              key={dev.deviceId}
              deviceName={dev.deviceName}
              lastUpdated={dev.lastUpdated || "N/A"}
            >
              {dev.metrics?.map((metric, index) => {
                if (metric.displayType === "graph") {
                  const graphData = metric.data.map((dp) => ({
                    time: dp.time,
                    value: dp.value,
                  }));
                  return (
                    <GraphedMetric
                      key={index}
                      metricName={metric.metricName}
                      data={graphData}
                      yMax={100}
                      onClick={handleMetricClick}
                    />
                  );
                } else {
                  const latestValue =
                    metric.data.length > 0
                      ? metric.data[metric.data.length - 1].value
                      : 0;
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
      ))}
    </>
  );
};

export default HomePage;
