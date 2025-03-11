import React from "react";
import styled from "styled-components";
import { frostedGlass } from "../mixins";
import StyledDropdown from "./Dropdown"; 
import Command from "./Command";
import { Device } from "../data_models";

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
  overflow: hidden;
  ${frostedGlass}
`;

const AggregatorHeader = styled.div`
  background-color: ${({ theme }) => theme.colors.header};
  color: ${({ theme }) => theme.colors.text};
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
        <div style={{ display: "flex", gap: "1rem" }}>
          <StyledDropdown onChange={handleSelectChange}>
            <option value="0">Select a device</option>
            {devices.map((d) => (
              <option key={d.deviceId} value={d.deviceId}>
                {d.deviceName}
              </option>
            ))}
          </StyledDropdown>
          <Command aggregatorName={aggregatorName} devices={devices} />
        </div>
      </AggregatorHeader>
      <AggregatorBody>{children}</AggregatorBody>
    </AggregatorCardContainer>
  );
};

export default AggregatorCard;
