import React from "react";
import styled from "styled-components";

interface DeviceCardProps {
  deviceName: string;
  lastUpdated: string;
  children?: React.ReactNode;
}

const DeviceCardContainer = styled.div`
  border-radius: 0.75rem;
  background-color: ${({ theme }) => theme.colors.device_background};
  width: ${({ theme }) => theme.DeviceCardDimensions.widthDesktop};

  @media (max-width: ${({ theme }) => theme.breakpoints.mobile}) {
    width: 100%;
  }
`;

const DeviceHeader = styled.div`
  background-color: ${({ theme }) => theme.colors.header};
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
  padding: 0.7rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h3`
  margin: 0 0 0.25rem;
  font-weight: 600;
`;

const LastUpdated = styled.span`
  font-size: 0.85rem;
  opacity: 0.9;
`;

const DeviceBody = styled.div`
  display: flex;
  flex-direction: column;
  margin: 1rem;
  border-radius: 0.75rem;
  overflow: hidden;
  background-color: ${({ theme }) => theme.colors.device_background};
  border: 1px solid ${({ theme }) => theme.colors.header};

  /* Add a thin divider after each metric except the last child */
  & > *:not(:last-child) {
    border-bottom: 1px solid ${({ theme }) => theme.colors.header};
  }

  /* Alternate background: odd vs. even children */
  & > *:nth-child(odd) {
    background-color: ${({ theme }) => theme.odd_row};
  }

  & > *:nth-child(even) {
    background-color: ${({ theme }) => theme.even_row};
  }
`;

const DeviceCard: React.FC<DeviceCardProps> = ({
  deviceName,
  lastUpdated,
  children,
}) => {
  return (
    <DeviceCardContainer>
      <DeviceHeader>
        <Title>{deviceName}</Title>
        <LastUpdated>Last updated: {lastUpdated}</LastUpdated>
      </DeviceHeader>
      <DeviceBody>{children}</DeviceBody>
    </DeviceCardContainer>
  );
};

export default DeviceCard;
