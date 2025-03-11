import React from "react";
import styled from "styled-components";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import MetricPage from "./pages/MetricPage";
import { useLocation, matchPath } from "react-router-dom";



const Header = styled.header`
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 3rem ;
  color: ${({ theme }) => theme.colors.text};

`;


const PageTitle = styled.h1`
  text-align: center;
  font-size: 1.9rem;
  margin: 0;
`;

const NavLink = styled.a`
  text-decoration: none;
  font-size: 1.3rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const App: React.FC = () => {
  const location = useLocation();

  // Default title
  let pageTitle = "Dashboard";

  // Check if the current route matches "/metric/:metricName"
  const metricMatch = matchPath("/metric/:metricName", location.pathname);
  if (metricMatch && metricMatch.params.metricName) {
    pageTitle = decodeURIComponent(metricMatch.params.metricName);
  }

  return (
    <>
      <Header>
        <NavLink href="/">Deep Metrics</NavLink>
        <PageTitle>{pageTitle}</PageTitle>
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
