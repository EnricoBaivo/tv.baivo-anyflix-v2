"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import SpatialNavigation from "js-spatial-navigation";

export enum Direction {
  Up = "up",
  Down = "down",
  Left = "left",
  Right = "right",
}

type Coordinates = { x: string | number; y: string | number };
type KeyEventInfo = {
  key: string;
  keyCode: number | string;
  keyStatus: string;
};

type KeyRemoteNavigationContextType = {
  coordinates: Coordinates;
  okSelect: string;
  keyEvent: KeyEventInfo;
};

const KeyRemoteNavigationContext = createContext<
  KeyRemoteNavigationContextType | undefined
>(undefined);

type KeyRemoteNavigationProviderProps = {
  children: ReactNode;
};

export const KeyRemoteNavigationProvider = ({
  children,
}: KeyRemoteNavigationProviderProps) => {
  const [coordinates, setCoordinates] = useState<Coordinates>({
    x: "-",
    y: "-",
  });
  const [okSelect, setOkSelect] = useState<string>("-");
  const [keyEvent, setKeyEvent] = useState<KeyEventInfo>({
    key: "-",
    keyCode: "-",
    keyStatus: "-",
  });

  useEffect(() => {
    // Initialize spatial navigation on elements with the class "item"
    SpatialNavigation.init();
    SpatialNavigation.add({ selector: "button" });
    SpatialNavigation.makeFocusable();

    let lastClickedId: string | null = null;
    const items = Array.from(
      document.getElementsByClassName("item")
    ) as HTMLElement[];

    // Update coordinates on global mouseover
    const handleMouseOverGlobal = (e: MouseEvent) => {
      setCoordinates({ x: e.pageX, y: e.pageY });
    };

    // When an item is clicked, update the "OK Select" state.
    const handleClick = (e: Event) => {
      const target = e.target as HTMLElement;
      if (lastClickedId) {
        document.getElementById(lastClickedId)?.classList.remove("clicked");
      }
      target.classList.add("clicked");
      lastClickedId = target.id;
      setOkSelect(target.id);
    };

    // On mouseover over an item, remove focus from all items and focus the current one.
    const handleItemMouseOver = (e: Event) => {
      items.forEach((item) => item.blur());
      (e.target as HTMLElement).focus();
    };

    // Remove focus when the mouse leaves an item.
    const handleItemMouseOut = (e: Event) => {
      (e.target as HTMLElement).blur();
    };

    // On keydown (Enter key) on an item, add an active state.
    const handleItemKeyDown = (e: KeyboardEvent) => {
      if (e.keyCode === 13) {
        (e.target as HTMLElement).classList.add("active");
      }
    };

    // On keyup (Enter key) remove the active state and trigger a click.
    const handleItemKeyUp = (e: KeyboardEvent) => {
      if (e.keyCode === 13) {
        (e.target as HTMLElement).classList.remove("active");
        handleClick(e);
      }
    };

    // Global keydown handler updates the key event state.
    const handleKeyDown = (e: KeyboardEvent) => {
      // Special case: clear coordinates for keyCode 1537 (webOS 1.x)
      if (e.keyCode === 1537) {
        setCoordinates({ x: "-", y: "-" });
      }
      setKeyEvent({ key: e.key, keyCode: e.keyCode, keyStatus: e.type });
    };

    // Global keyup handler updates the key event state.
    const handleKeyUp = (e: KeyboardEvent) => {
      setKeyEvent({ key: e.key, keyCode: e.keyCode, keyStatus: e.type });
    };

    // Handle custom cursor state change events.
    const handleCursorStateChange = (event: CustomEvent) => {
      const { visibility } = event.detail;
      if (!visibility) {
        setCoordinates({ x: "-", y: "-" });
      }
    };

    // Add event listeners.
    window.addEventListener("mouseover", handleMouseOverGlobal);
    items.forEach((item) => {
      item.addEventListener("mouseover", handleItemMouseOver);
      item.addEventListener("mouseout", handleItemMouseOut);
      item.addEventListener("click", handleClick);
      item.addEventListener("keydown", handleItemKeyDown);
      item.addEventListener("keyup", handleItemKeyUp);
    });
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("keyup", handleKeyUp);
    document.addEventListener(
      "cursorStateChange",
      handleCursorStateChange as EventListener
    );

    // Cleanup event listeners on unmount.
    return () => {
      window.removeEventListener("mouseover", handleMouseOverGlobal);
      items.forEach((item) => {
        item.removeEventListener("mouseover", handleItemMouseOver);
        item.removeEventListener("mouseout", handleItemMouseOut);
        item.removeEventListener("click", handleClick);
        item.removeEventListener("keydown", handleItemKeyDown);
        item.removeEventListener("keyup", handleItemKeyUp);
      });
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("keyup", handleKeyUp);
      document.removeEventListener(
        "cursorStateChange",
        handleCursorStateChange as EventListener
      );
    };
  }, []);

  return (
    <KeyRemoteNavigationContext.Provider
      value={{ coordinates, okSelect, keyEvent }}
    >
      {children}
    </KeyRemoteNavigationContext.Provider>
  );
};

// Custom hook to consume the key remote navigation context.
export const useKeyRemoteNavigationContext = () => {
  const context = useContext(KeyRemoteNavigationContext);
  if (!context) {
    throw new Error(
      "useKeyRemoteNavigationContext must be used within a KeyRemoteNavigationProvider"
    );
  }
  return context;
};
