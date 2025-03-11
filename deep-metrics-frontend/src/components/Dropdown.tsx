import React from "react";
import styled from "styled-components";

interface CustomDropdownProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  children: React.ReactNode;
}

const DropdownStyled = styled.select`
  appearance: none;
  background-color: ${({ theme }) => theme.colors.device_background};
  color: ${({ theme }) => theme.colors.text};
  border: 1px solid ${({ theme }) => theme.colors.header};
  border-radius: 0.25rem;
  font-size: 1rem;
  padding: 0.25rem;
  padding-right: 2rem; 
  cursor: pointer;

  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M7 10l5 5 5-5z'/></svg>");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;

  &::-ms-expand {
    display: none;
  }

  option {
    background-color: ${({ theme }) => theme.colors.device_background};
    color: ${({ theme }) => theme.colors.text};
  }
`;

const StyledDropdown: React.FC<CustomDropdownProps> = ({ children, ...props }) => {
  return <DropdownStyled {...props}>{children}</DropdownStyled>;
};

export default StyledDropdown;
