// src/App.tsx
import React from "react";
import styled from "styled-components";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import MetricPage from "./pages/MetricPage";



const Header = styled.header`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 3rem ;
  color: ${({ theme }) => theme.colors.primary};

`;

const Title = styled.h1`
  text-align: center;
  font-size: 1.3rem;
  font-weight: 600;
`;

const PageTitle = styled.h1`
  text-align: center;
  font-size: 1.9rem;
  margin: 0;
  color: ${({ theme }) => theme.colors.text};
`;

const NavLink = styled.a`
  text-decoration: none;
  font-size: 1.3rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.primary};
`;

const App: React.FC = () => {
  return (
    <>
      <Header>
        <Title>Deep Metrics</Title>
        <PageTitle>Dashboard</PageTitle>
        <NavLink href="https://github.com/justyna-przy/DeepMetrics">Github</NavLink>
      </Header>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/metric/:metricName" element={<MetricPage />} />
      </Routes>
    </>
  );
};

export default App;
