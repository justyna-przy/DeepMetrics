import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import styled, {useTheme} from "styled-components";

interface MetricPoint {
  time: string;
  value: number;
}

interface GraphedMetricProps {
  metricName: string;
  data: MetricPoint[];
  yMax?: number;
  onClick?: (metricName: string) => void; 
}

const GraphedMetricCard = styled.div`
  width: 100%;
  padding: 1rem 1rem 0.5rem;
  cursor: pointer;
  background-color: transparent; 
`;

const MetricName = styled.h2`
  text-align: left;
  margin: 0 0 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const GraphedMetric: React.FC<GraphedMetricProps> = ({
  metricName,
  data,
  yMax,
  onClick,
}) => {
  const theme = useTheme();
  const maxValueInData = data.length
    ? Math.max(...data.map((d) => d.value))
    : 0;
  const upperDomain = yMax !== undefined ? yMax : maxValueInData;

  return (
    <GraphedMetricCard onClick={() => onClick?.(metricName)}>
      <MetricName>{metricName}</MetricName>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 0 }} style={{cursor: "pointer"}}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" axisLine={false} tickLine={false} tick={false} />
          <YAxis domain={[0, upperDomain]} axisLine tickLine />
          <Tooltip
            labelFormatter={(label) => `Time: ${label}`}
            formatter={(value: number) => [`${value}`, "Value"]}
            contentStyle={{
              background: theme.colors.header,
              border: "none",
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#8884d8"
            strokeWidth={2}
            dot
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </GraphedMetricCard>
  );
};

export default GraphedMetric;
