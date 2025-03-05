import { createGlobalStyle } from 'styled-components';

export const GlobalStyles = createGlobalStyle`
  /* Apply box-sizing to every element */
  *, *::before, *::after {
    box-sizing: border-box;
  }
  
  html, body, #root {
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
                 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 
                 'Droid Sans', 'Helvetica Neue', sans-serif;
    background-color: #f0f0f0; 
    color: #333;
  }
`;
