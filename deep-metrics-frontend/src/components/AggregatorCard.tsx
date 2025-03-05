import React from 'react';
import styled from 'styled-components';

interface Device {
  deviceId: number;
  deviceName: string;
}

interface AggregatorCardProps {
  aggregatorName: string;
  devices: Device[];
  onSelectDevice?: (deviceId: number) => void;
  children?: React.ReactNode;
}

const AggregatorCardContainer = styled.div`
  width: calc(100% - 4rem);
  max-width: 85rem;
  margin: 2rem auto;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 0.75rem;
  /* Set a fixed height so overflow can scroll */
 
`;

const AggregatorHeader = styled.div`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  padding: 0.7rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
`;

const Title = styled.h3`
  margin: 0;
  font-weight: 600;
`;

const DeviceDropdown = styled.select`
  background-color: #fff;
  color: #000;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  font-size: 1rem;
  padding: 0.25rem;
`;

const AggregatorBody = styled.div`
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  height: 600px;
  overflow-y: auto;
`;

const AggregatorCard: React.FC<AggregatorCardProps> = ({
  aggregatorName,
  devices,
  onSelectDevice,
  children
}) => {
  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(e.target.value);
    onSelectDevice?.(selectedId);
  };

  return (
    <AggregatorCardContainer>
      <AggregatorHeader>
        <Title>{aggregatorName}</Title>
        <DeviceDropdown onChange={handleSelectChange}>
          <option value="">-- Select a device --</option>
          {devices.map((d) => (
            <option key={d.deviceId} value={d.deviceId}>
              {d.deviceName}
            </option>
          ))}
        </DeviceDropdown>
      </AggregatorHeader>
      <AggregatorBody>
        {children}
      </AggregatorBody>
    </AggregatorCardContainer>
  );
};

export default AggregatorCard;
