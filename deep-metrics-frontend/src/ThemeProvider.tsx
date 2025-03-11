import React, { ReactNode } from 'react';
import { ThemeProvider } from 'styled-components';
import { GlobalStyles } from './GlobalStyles';

export const theme = {
  colors: {
    header: '#181229',
    primary: '#512fa9',
    text: '#ffffff',
    device_background: '#120e1f',
    odd_row: '#0b0813',
    even_row: '#1f1b2f',
  },
  DeviceCardDimensions: {
    widthDesktop: '49%', 
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