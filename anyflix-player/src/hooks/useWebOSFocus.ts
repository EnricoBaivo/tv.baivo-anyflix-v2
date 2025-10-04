import { useEffect, useState, useRef } from "react";

/**
 * Hook options for webOS TV focus management
 */
interface WebOSFocusOptions {
  onFocus?: () => void;
  onBlur?: () => void;
  onEnter?: () => void;
  disabled?: boolean;
  autoFocus?: boolean;
}

/**
 * Single unified hook for webOS TV focus management
 * Works with the global SpatialNavigation system initialized in KeyRemoteNavigationProvider
 *
 * @example
 * const { isFocused, ref, focusableProps } = useWebOSFocus({
 *   onFocus: () => console.log('focused'),
 *   onEnter: () => handleClick(),
 * });
 *
 * return <div ref={ref} {...focusableProps}>Content</div>
 */
export const useWebOSFocus = (options: WebOSFocusOptions = {}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [navigationMode, setNavigationMode] = useState<"pointer" | "5way">(
    "pointer"
  );
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    // Check if running on WebOS TV
    const isWebOS =
      typeof window !== "undefined" &&
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;

    if (isWebOS) {
      setNavigationMode("5way");
    }

    // Listen for cursor state changes (webOS TV specific)
    const handleCursorStateChange = (event: CustomEvent) => {
      const { visibility } = event.detail;
      setNavigationMode(visibility ? "pointer" : "5way");
    };

    // Detect navigation mode changes
    const handlePointerMove = () => setNavigationMode("pointer");
    const handleKeyDown = (e: KeyboardEvent) => {
      // Arrow keys switch to 5-way mode
      if ([37, 38, 39, 40].includes(e.keyCode)) {
        setNavigationMode("5way");
      }
    };

    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener(
      "cursorStateChange",
      handleCursorStateChange as EventListener
    );

    return () => {
      document.removeEventListener("pointermove", handlePointerMove);
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener(
        "cursorStateChange",
        handleCursorStateChange as EventListener
      );
    };
  }, []);

  useEffect(() => {
    const element = elementRef.current;
    if (!element || options.disabled) return;

    const handleFocus = () => {
      setIsFocused(true);
      options.onFocus?.();
    };

    const handleBlur = () => {
      setIsFocused(false);
      options.onBlur?.();
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      // Enter key (OK button on remote)
      if (e.keyCode === 13) {
        e.preventDefault();
        options.onEnter?.();
      }
    };

    element.addEventListener("focus", handleFocus);
    element.addEventListener("blur", handleBlur);
    element.addEventListener("keydown", handleKeyDown as EventListener);

    // Auto focus if requested
    if (options.autoFocus && navigationMode === "5way") {
      element.focus();
    }

    return () => {
      element.removeEventListener("focus", handleFocus);
      element.removeEventListener("blur", handleBlur);
      element.removeEventListener("keydown", handleKeyDown as EventListener);
    };
  }, [options, navigationMode]);

  // Props to spread on the focusable element
  const focusableProps = {
    tabIndex: options.disabled ? -1 : 0,
    className: getFocusClasses(isFocused, navigationMode),
    "data-webos-focusable": !options.disabled,
  };

  return {
    isFocused,
    navigationMode,
    ref: elementRef,
    focusableProps,
  };
};

/**
 * Hook for handling webOS TV key events (arrow keys, back button)
 * Use this when you need custom key handling without focus management
 *
 * @example
 * useWebOSKeyHandler({
 *   onBack: () => { closeModal(); return true; },
 *   onNavigate: (dir) => { if (dir === 'down') openMenu(); }
 * });
 */
export const useWebOSKeyHandler = (
  options: {
    onNavigate?: (
      direction: "left" | "right" | "up" | "down"
    ) => boolean | void;
    onBack?: () => boolean | void;
    onOk?: () => void;
  } = {}
) => {
  const [navigationMode, setNavigationMode] = useState<"pointer" | "5way">(
    "pointer"
  );

  useEffect(() => {
    // Check if running on WebOS TV
    const isWebOS =
      typeof window !== "undefined" &&
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;

    if (isWebOS) {
      setNavigationMode("5way");
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      // Arrow keys
      if ([37, 38, 39, 40].includes(e.keyCode)) {
        setNavigationMode("5way");

        const directionMap = {
          37: "left" as const,
          38: "up" as const,
          39: "right" as const,
          40: "down" as const,
        };

        const direction = directionMap[e.keyCode as keyof typeof directionMap];
        if (direction) {
          const handled = options.onNavigate?.(direction);
          if (handled) {
            e.preventDefault();
          }
        }
      }

      // Enter/OK button
      if (e.keyCode === 13 && options.onOk) {
        options.onOk();
      }

      // Back button (webOS TV)
      if (e.keyCode === 461 && options.onBack) {
        const handled = options.onBack();
        if (handled) {
          e.preventDefault();
        }
      }
    };

    const handlePointerMove = () => setNavigationMode("pointer");

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("pointermove", handlePointerMove);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("pointermove", handlePointerMove);
    };
  }, [options]);

  return { navigationMode };
};

/**
 * Generate CSS classes for focus states based on navigation mode
 */
const getFocusClasses = (
  isFocused: boolean,
  navigationMode: "pointer" | "5way"
) => {
  if (!isFocused) return "";

  const baseClasses =
    "outline-none ring-2 ring-primary ring-offset-2 ring-offset-background";
  const animationClasses = "transition-all duration-200 ease-out";

  // More prominent focus ring for 5-way navigation (remote control)
  if (navigationMode === "5way") {
    return `${baseClasses} ring-offset-4 shadow-lg shadow-primary/30 scale-105 ${animationClasses}`;
  }

  // Subtle focus ring for pointer navigation (mouse/magic remote pointer)
  return `${baseClasses} ring-offset-1 ${animationClasses}`;
};
