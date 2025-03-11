import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import CustomThemeProvider from "./ThemeProvider";
import { BrowserRouter } from "react-router-dom";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
  <React.StrictMode>
    <BrowserRouter basename="/deep-metrics">
      <CustomThemeProvider>
        <App />
      </CustomThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
