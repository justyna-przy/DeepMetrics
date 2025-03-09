import React from 'react';
import styled from 'styled-components';

interface RowMetricProps {
    metricName: string;
    value: number;
    onClick?: (metricName: string) => void;
}

const RowContainer = styled.tr`
    display: flex;
    justify-content: space-between;
    padding: 0.3rem 1rem;
    flex-direction: row;
    cursor: pointer;
    &:hover {
        background-color: ${({ theme }) => theme.colors.header};
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

const RowMetric: React.FC<RowMetricProps> = ({ metricName, value, onClick }) => {
    return (
        <RowContainer onClick={() => onClick?.(metricName)}>
            <MetricName>{metricName}</MetricName>
            <MetricValue>{value}</MetricValue>
        </RowContainer>
    )
}

export default RowMetric;