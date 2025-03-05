// src/App.tsx
import React from "react";
import Home from "./Home";
import styled from "styled-components";

const Title = styled.h1`
  text-align: center;
  font-size: 1.5rem;
  margin: 2rem auto;
`;

const App: React.FC = () => {
  return (
    <>
      <Title>Deep Metrics</Title>
      <Home />
    </>
  );
};

export default App;
