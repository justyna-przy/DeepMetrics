import React, { ReactNode } from 'react';
import { ThemeProvider } from 'styled-components';

const theme = {
  colors: {
    primary: '#0070f3',
  },
};

interface CustomThemeProviderProps {
  children: ReactNode;
}

export default function CustomThemeProvider({ children }: CustomThemeProviderProps) {
  return <ThemeProvider theme={theme}>{children}</ThemeProvider>;
}
