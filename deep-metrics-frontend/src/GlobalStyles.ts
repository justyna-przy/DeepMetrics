import { createGlobalStyle } from 'styled-components';

export const GlobalStyles = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }
  
  html, body, #root {
    margin: 0;
    padding: 0;
  }

  body {
    font-family: "Recursive", sans-serif;
    background-color: #0b0813; 
    color: white;
  }

  select {
    font-family: "Recursive", sans-serif;
  }

  button {
    font-family: "Recursive", sans-serif;
  }


  ::-webkit-scrollbar {
    width: 1rem;
    height: 1rem;
  }

  ::-webkit-scrollbar-track {
    background: #0b0813;
    border-radius: 0.3rem;
  }

  ::-webkit-scrollbar-thumb {
    background: #4c4f78;
    border-radius: 5px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #6c6f98;
    cursor: pointer;
  }

  html {
    scrollbar-width: thin;
    scrollbar-color: #4c4f78 #1e1e2e;
  }
`;
