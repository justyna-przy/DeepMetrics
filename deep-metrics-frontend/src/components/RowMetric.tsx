import React from 'react';
import styled from 'styled-components';

interface RowMetricProps {
  metricName: string;
  value: number;
  onClick?: (metricName: string) => void;
}

const RowContainer = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
  cursor: pointer;
  &:hover {
    background-color: ${({ theme }) => theme.colors.header};
  }
`;

const MetricNameCell = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const MetricValueCell = styled.div`
  font-size: 1rem;
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text};
  text-align: right;
`;

const RowMetric: React.FC<RowMetricProps> = ({ metricName, value, onClick }) => {
  return (
    <RowContainer onClick={() => onClick?.(metricName)} role="row">
      <MetricNameCell role="cell">{metricName}</MetricNameCell>
      <MetricValueCell role="cell">{value}</MetricValueCell>
    </RowContainer>
  );
};

export default RowMetric;
