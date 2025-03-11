import React, { useState } from "react";
import styled from "styled-components";
import StyledDropdown from "./Dropdown";
import { Device } from "../data_models";
import { config } from "../config/config";


interface CommandDropdownProps {
  aggregatorName: string;
  devices: Device[];
}

const SendButton = styled.button`
  margin-left: 0.5rem;
  padding: 0.25rem 0.75rem;
  border: none;
  background-color: ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.text};
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
`;

const Command: React.FC<CommandDropdownProps> = ({
  aggregatorName,
  devices,
}) => {
  const staticCommands = ["stop", "restart", "start"];

  const options = devices.flatMap((device) =>
    staticCommands.map((command) => ({
      value: `${device.deviceName}|${command}`,
      label: `${device.deviceName} - ${command}`,
    }))
  );

  const [selectedOption, setSelectedOption] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedOption(e.target.value);
  };

  const handleSend = async () => {
    if (!selectedOption) return;

    const [deviceName, command] = selectedOption.split("|");
    try {
      const response = await fetch(
        `${config.apiBaseUrl}${config.endpoints.commands}`,
        {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          aggregator_name: aggregatorName,
          device_name: deviceName,
          command: command,
        }),
      });
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      const data = await response.json();
      console.log("Command enqueued:", data);
    } catch (err) {
      console.error("Failed to send command:", err);
    }
  };

  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      <StyledDropdown value={selectedOption} onChange={handleChange}>
        <option value="">Select a command</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </StyledDropdown>
      <SendButton onClick={handleSend} disabled={!selectedOption}>
        Send
      </SendButton>
    </div>
  );
};

export default Command;
