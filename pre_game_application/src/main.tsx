import "./styles.css";
import React from "react";
import { Match } from "./view/match";
import { tagTheme } from "./utils/theme";
import { invoke } from "@tauri-apps/api";
import ReactDOM from "react-dom/client";
import { appWindow } from "@tauri-apps/api/window";
import { ChakraProvider, extendTheme } from "@chakra-ui/react";

invoke("is_lcu_success").then((isTrue) => {
  if (isTrue) {
    const theme = extendTheme({
      components: {
        Tag: tagTheme,
      },
    });

    ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
      <Match />
    );
  } else {
    ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
      "LCU connection errorF"
    );
  }
});
