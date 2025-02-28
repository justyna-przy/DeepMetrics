// src/HomePage.tsx
import React from 'react';
import './styles.css'; // Plain CSS for page-specific styling
import styled from 'styled-components';

// Optional: If you want Recharts, uncomment these lines
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

// Example typed data interface if using Recharts
interface MetricData {
  time: string;
  value: number;
}

const Title = styled.h1`
  color: ${(props) => props.theme.colors.primary};
  text-align: center;
`;

const Home: React.FC = () => {
  // Example data if using Recharts:
  const data: MetricData[] = [
    { time: '10:00', value: 30 },
    { time: '10:05', value: 45 },
    { time: '10:10', value: 28 },
    { time: '10:15', value: 50 },
  ];

  return (
    <div className="home-page-container">
      <Title>Deep Metrics</Title>
      <p>Welcome to the Deep Metrics dashboard!</p>

      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
     
    </div>
  );
};

export default Home;
