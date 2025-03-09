import React from "react";
import styled from "styled-components";
import { frostedGlass } from "../mixins";
import { createGlobalStyle } from "styled-components";
import StyledDropdown from "./Dropdown"; 


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
  max-width: 87rem;
  margin: 2rem auto;
  border-radius: 0.75rem;
  /* Set a fixed height so overflow can scroll */
  ${frostedGlass}
  overflow: hidden;
`;

const AggregatorHeader = styled.div`
  background-color: ${({ theme }) => theme.colors.header};
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
  appearance: none;
  background-color: ${({ theme }) => theme.colors.device_background};
  color: ${({ theme }) => theme.colors.text};
  border: 1px solid ${({ theme }) => theme.colors.header};
  border-radius: 0.25rem;
  font-size: 1rem;
  padding: 0.25rem;
  padding-right: 2rem; /* Space for custom arrow */
  cursor: pointer;

  /* Custom dropdown arrow */
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M7 10l5 5 5-5z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;

  &::-ms-expand {
    display: none;
  }
`;

/* Apply styles globally to dropdown options */
const GlobalDropdownStyles = createGlobalStyle`
  select option {
    background-color: ${({ theme }) => theme.colors.device_background};
    color: ${({ theme }) => theme.colors.text};
  }

  select option:hover,
  select option:focus {
    background-color: ${({ theme }) =>
      theme.colors.highlight}; /* Change this to your preferred hover color */
  }
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
  children,
}) => {
  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(e.target.value);
    onSelectDevice?.(selectedId);
  };

  return (
    <AggregatorCardContainer>
      <AggregatorHeader>
        <Title>{aggregatorName}</Title>
        <StyledDropdown onChange={handleSelectChange}>
          <option value="">Select a device</option>
          {devices.map((d) => (
            <option key={d.deviceId} value={d.deviceId}>
              {d.deviceName}
            </option>
          ))}
        </StyledDropdown>
      </AggregatorHeader>
      <AggregatorBody>{children}</AggregatorBody>
    </AggregatorCardContainer>
  );
};

export default AggregatorCard;
