import React, { ReactNode } from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './GlobalStyles';


export const theme = {
  colors: {
    primary: '#1a73e8',
    secondary: '#8884d8',
    text: '#333'
  },
  DeviceCardDimensions: {
    widthDesktop: '27rem', 
    widthMobile: '100%', 
  },
  breakpoints: {
    mobile: '768px',  
  },
};

interface CustomThemeProviderProps {
  children: ReactNode;
}

export default function CustomThemeProvider({ children }: CustomThemeProviderProps) {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyles />
      {children}
    </ThemeProvider>
  );
}