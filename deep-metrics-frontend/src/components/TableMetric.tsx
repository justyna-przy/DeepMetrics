import React from 'react';
import styled from 'styled-components';

interface TableMetricProps {
    metricName: string;
    value: number;
    onClick?: (metricName: string) => void;
}

const TableRow = styled.tr`
    display: flex;
    justify-content: space-between;
    padding: 1rem;
    flex-direction: row;
    cursor: pointer;
    &:hover {
        background-color: #fafafa;
    }
`;

const MetricName = styled.h2`
    text-align: left;
    font-size: 1rem;
    font-weight: 600;
    color: ${({ theme }) => theme.colors.text};
`

const MetricValue = styled.h2`
    text-align: right;
    font-size: 1rem;
    font-weight: 500;
    color: ${({ theme }) => theme.colors.text};
`

const TableMetric: React.FC<TableMetricProps> = ({ metricName, value, onClick }) => {
    return (
        <TableRow onClick={() => onClick?.(metricName)}>
            <MetricName>{metricName}</MetricName>
            <MetricValue>{value}</MetricValue>
        </TableRow>
    )
}

export default TableMetric;