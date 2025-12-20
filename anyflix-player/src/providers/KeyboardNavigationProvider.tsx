import React, { useEffect, useCallback, useRef } from "react";
import {
  useFocusContext,
  type Direction,
} from "../contexts/FocusContext";

// WebOS TV Key Codes
export const KEY_CODES = {
  LEFT: 37,
  UP: 38,
  RIGHT: 39,
  DOWN: 40,
  ENTER: 13,
  BACK: 461, // webOS specific
  ESCAPE: 27, // Browser fallback for Back
  RED: 403,
  GREEN: 404,
  YELLOW: 405,
  BLUE: 406,
  PLAY: 415,
  PAUSE: 19,
  STOP: 413,
  REWIND: 412,
  FAST_FORWARD: 417,
} as const;

// Direction mapping from key codes
const KEY_TO_DIRECTION: Record<number, Direction> = {
  [KEY_CODES.LEFT]: "left",
  [KEY_CODES.RIGHT]: "right",
  [KEY_CODES.UP]: "up",
  [KEY_CODES.DOWN]: "down",
};

export interface KeyboardNavigationProviderProps {
  children: React.ReactNode;
  /** Callback for Back button press (return true to prevent default behavior) */
  onBack?: () => boolean | void;
  /** Callback for color buttons */
  onColorButton?: (color: "red" | "green" | "yellow" | "blue") => void;
  /** Callback for media buttons */
  onMediaButton?: (button: "play" | "pause" | "stop" | "rewind" | "fastForward") => void;
  /** Whether to prevent default browser behavior for arrow keys */
  preventDefaultArrows?: boolean;
}

/**
 * KeyboardNavigationProvider - Global keyboard event handler
 *
 * Handles:
 * - Arrow key navigation (delegates to FocusContext)
 * - Back button (webOS and browser Escape)
 * - Enter/OK key (delegates to focused element)
 * - Color buttons (webOS remote)
 * - Media buttons (webOS remote)
 * - Navigation mode switching (pointer vs 5-way)
 *
 * @example
 * <FocusProvider>
 *   <KeyboardNavigationProvider onBack={() => navigate(-1)}>
 *     <App />
 *   </KeyboardNavigationProvider>
 * </FocusProvider>
 */
export const KeyboardNavigationProvider: React.FC<KeyboardNavigationProviderProps> = ({
  children,
  onBack,
  onColorButton,
  onMediaButton,
  preventDefaultArrows = true,
}) => {
  const {
    moveFocus,
    setNavigationMode,
    focusedElementId,
    getElement,
    popFocusLayer,
    getFocusLayerStack,
  } = useFocusContext();

  // Track last input type for mode switching
  const lastInputRef = useRef<"pointer" | "keyboard">("pointer");

  // Handle key down
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      const keyCode = event.keyCode;

      // Switch to 5-way mode on arrow key press
      if (KEY_TO_DIRECTION[keyCode]) {
        if (lastInputRef.current !== "keyboard") {
          lastInputRef.current = "keyboard";
          setNavigationMode("5way");
        }
      }

      // Arrow keys - navigate
      const direction = KEY_TO_DIRECTION[keyCode];
      if (direction) {
        const handled = moveFocus(direction);
        if (handled && preventDefaultArrows) {
          event.preventDefault();
        }
        return;
      }

      // Enter/OK - select focused element
      if (keyCode === KEY_CODES.ENTER) {
        if (focusedElementId) {
          const element = getElement(focusedElementId);
          if (element?.onSelect) {
            event.preventDefault();
            element.onSelect();
          }
        }
        return;
      }

      // Back button (webOS) or Escape (browser)
      if (keyCode === KEY_CODES.BACK || keyCode === KEY_CODES.ESCAPE) {
        // CRITICAL: Stop event propagation to prevent webOS TV from handling it
        // This prevents the "Exit app?" dialog from appearing
        event.preventDefault();
        event.stopPropagation();

        // First check if there's a modal to close
        const layerStack = getFocusLayerStack();
        if (layerStack.length > 0) {
          popFocusLayer();
          // Also call onBack so parent component can update its state
          onBack?.();
          return;
        }

        // Then call the onBack callback for normal navigation
        onBack?.();
        return;
      }

      // Color buttons
      if (onColorButton) {
        switch (keyCode) {
          case KEY_CODES.RED:
            onColorButton("red");
            break;
          case KEY_CODES.GREEN:
            onColorButton("green");
            break;
          case KEY_CODES.YELLOW:
            onColorButton("yellow");
            break;
          case KEY_CODES.BLUE:
            onColorButton("blue");
            break;
        }
      }

      // Media buttons
      if (onMediaButton) {
        switch (keyCode) {
          case KEY_CODES.PLAY:
            onMediaButton("play");
            break;
          case KEY_CODES.PAUSE:
            onMediaButton("pause");
            break;
          case KEY_CODES.STOP:
            onMediaButton("stop");
            break;
          case KEY_CODES.REWIND:
            onMediaButton("rewind");
            break;
          case KEY_CODES.FAST_FORWARD:
            onMediaButton("fastForward");
            break;
        }
      }
    },
    [
      moveFocus,
      setNavigationMode,
      focusedElementId,
      getElement,
      popFocusLayer,
      getFocusLayerStack,
      onBack,
      onColorButton,
      onMediaButton,
      preventDefaultArrows,
    ]
  );

  // Handle pointer movement - switch to pointer mode
  const handlePointerMove = useCallback(() => {
    if (lastInputRef.current !== "pointer") {
      lastInputRef.current = "pointer";
      setNavigationMode("pointer");
    }
  }, [setNavigationMode]);

  // Handle webOS cursor state change
  const handleCursorStateChange = useCallback(
    (event: CustomEvent) => {
      const { visibility } = event.detail;
      if (visibility) {
        lastInputRef.current = "pointer";
        setNavigationMode("pointer");
      } else {
        lastInputRef.current = "keyboard";
        setNavigationMode("5way");
      }
    },
    [setNavigationMode]
  );

  // Set up event listeners
  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener(
      "cursorStateChange",
      handleCursorStateChange as EventListener
    );

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("pointermove", handlePointerMove);
      document.removeEventListener(
        "cursorStateChange",
        handleCursorStateChange as EventListener
      );
    };
  }, [handleKeyDown, handlePointerMove, handleCursorStateChange]);

  return <>{children}</>;
};

/**
 * Hook for handling specific key events
 *
 * Use this when you need custom key handling in a component
 *
 * @example
 * useKeyHandler({
 *   onBack: () => closeModal(),
 *   onColorButton: (color) => console.log('Color:', color),
 * });
 */
export const useKeyHandler = (options: {
  onBack?: () => boolean | void;
  onColorButton?: (color: "red" | "green" | "yellow" | "blue") => void;
  onMediaButton?: (button: "play" | "pause" | "stop" | "rewind" | "fastForward") => void;
  onArrowKey?: (direction: Direction) => boolean | void;
}) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const keyCode = event.keyCode;

      // Arrow keys
      const direction = KEY_TO_DIRECTION[keyCode];
      if (direction && options.onArrowKey) {
        const handled = options.onArrowKey(direction);
        if (handled) {
          event.preventDefault();
          event.stopPropagation();
        }
        return;
      }

      // Back button
      if (
        (keyCode === KEY_CODES.BACK || keyCode === KEY_CODES.ESCAPE) &&
        options.onBack
      ) {
        const handled = options.onBack();
        if (handled) {
          event.preventDefault();
          event.stopPropagation();
        }
        return;
      }

      // Color buttons
      if (options.onColorButton) {
        switch (keyCode) {
          case KEY_CODES.RED:
            options.onColorButton("red");
            break;
          case KEY_CODES.GREEN:
            options.onColorButton("green");
            break;
          case KEY_CODES.YELLOW:
            options.onColorButton("yellow");
            break;
          case KEY_CODES.BLUE:
            options.onColorButton("blue");
            break;
        }
      }

      // Media buttons
      if (options.onMediaButton) {
        switch (keyCode) {
          case KEY_CODES.PLAY:
            options.onMediaButton("play");
            break;
          case KEY_CODES.PAUSE:
            options.onMediaButton("pause");
            break;
          case KEY_CODES.STOP:
            options.onMediaButton("stop");
            break;
          case KEY_CODES.REWIND:
            options.onMediaButton("rewind");
            break;
          case KEY_CODES.FAST_FORWARD:
            options.onMediaButton("fastForward");
            break;
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [options]);
};

export default KeyboardNavigationProvider;
