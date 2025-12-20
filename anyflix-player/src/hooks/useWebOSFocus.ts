import { useEffect, useState, useRef, useCallback, useId } from "react";
import { useFocusContextSafe, type NavigationMode } from "../contexts/FocusContext";
import { useFocusZone } from "../components/navigation/FocusZone";

/**
 * Hook options for webOS TV focus management
 */
interface WebOSFocusOptions {
  /** Unique ID for this focusable element */
  id?: string;
  /** Callback when element receives focus */
  onFocus?: () => void;
  /** Callback when element loses focus */
  onBlur?: () => void;
  /** Callback when Enter/OK is pressed while focused */
  onEnter?: () => void;
  /** Whether the element is disabled */
  disabled?: boolean;
  /** Whether to auto-focus this element on mount */
  autoFocus?: boolean;
}

/**
 * Single unified hook for webOS TV focus management
 *
 * This hook integrates with the FocusContext when available (recommended),
 * but also works standalone for backward compatibility.
 *
 * @example
 * // With FocusProvider (recommended)
 * <FocusProvider>
 *   <FocusZone id="my-zone" type="row">
 *     <MyComponent />
 *   </FocusZone>
 * </FocusProvider>
 *
 * // In MyComponent:
 * const { isFocused, ref, focusableProps } = useWebOSFocus({
 *   onFocus: () => console.log('focused'),
 *   onEnter: () => handleClick(),
 * });
 *
 * return <div ref={ref} {...focusableProps}>Content</div>
 */
export const useWebOSFocus = (options: WebOSFocusOptions = {}) => {
  const autoId = useId();
  const id = options.id || `focus-${autoId}`;

  // Try to get focus context (may be null if not in FocusProvider)
  const focusContext = useFocusContextSafe();
  const focusZone = useFocusZone();

  // Local state for standalone mode
  const [localIsFocused, setLocalIsFocused] = useState(false);
  const [localNavigationMode, setLocalNavigationMode] = useState<NavigationMode>("pointer");
  const elementRef = useRef<HTMLElement>(null);

  // Use context values if available, otherwise use local state
  const navigationMode = focusContext?.navigationMode ?? localNavigationMode;
  const isFocused = focusContext
    ? focusContext.focusedElementId === id
    : localIsFocused;

  // Register with FocusContext if available
  useEffect(() => {
    const element = elementRef.current;
    if (!element || !focusContext || !focusZone || options.disabled) return;

    focusContext.registerElement({
      id,
      zoneId: focusZone.zoneId,
      ref: element,
      disabled: options.disabled,
      onFocus: options.onFocus,
      onBlur: options.onBlur,
      onSelect: options.onEnter,
    });

    return () => {
      focusContext.unregisterElement(id);
    };
  }, [id, focusContext, focusZone, options.disabled, options.onFocus, options.onBlur, options.onEnter]);

  // Standalone mode: detect navigation mode
  useEffect(() => {
    // Skip if using FocusContext
    if (focusContext) return;

    // Check if running on WebOS TV
    const isWebOS =
      typeof window !== "undefined" &&
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;

    if (isWebOS) {
      setLocalNavigationMode("5way");
    }

    // Listen for cursor state changes (webOS TV specific)
    const handleCursorStateChange = (event: CustomEvent) => {
      const { visibility } = event.detail;
      setLocalNavigationMode(visibility ? "pointer" : "5way");
    };

    // Detect navigation mode changes
    const handlePointerMove = () => setLocalNavigationMode("pointer");
    const handleKeyDown = (e: KeyboardEvent) => {
      // Arrow keys switch to 5-way mode
      if ([37, 38, 39, 40].includes(e.keyCode)) {
        setLocalNavigationMode("5way");
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
  }, [focusContext]);

  // Standalone mode: handle focus/blur/keydown
  useEffect(() => {
    // Skip if using FocusContext
    if (focusContext) return;

    const element = elementRef.current;
    if (!element || options.disabled) return;

    const handleFocus = () => {
      setLocalIsFocused(true);
      options.onFocus?.();
    };

    const handleBlur = () => {
      setLocalIsFocused(false);
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
    if (options.autoFocus && localNavigationMode === "5way") {
      element.focus();
    }

    return () => {
      element.removeEventListener("focus", handleFocus);
      element.removeEventListener("blur", handleBlur);
      element.removeEventListener("keydown", handleKeyDown as EventListener);
    };
  }, [focusContext, options, localNavigationMode]);

  // Handle auto-focus with FocusContext
  useEffect(() => {
    if (!focusContext || !options.autoFocus || options.disabled) return;

    const timer = setTimeout(() => {
      focusContext.setFocusedElement(id);
    }, 0);

    return () => clearTimeout(timer);
  }, [focusContext, options.autoFocus, options.disabled, id]);

  // Handle native focus events when using FocusContext
  const handleNativeFocus = useCallback(() => {
    if (focusContext && !options.disabled) {
      focusContext.setFocusedElement(id);
    }
  }, [focusContext, options.disabled, id]);

  // Handle Enter key when using FocusContext
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.keyCode === 13 || e.key === "Enter") {
        e.preventDefault();
        options.onEnter?.();
      }
    },
    [options.onEnter]
  );

  // Props to spread on the focusable element
  const focusableProps = {
    tabIndex: options.disabled ? -1 : 0,
    className: getFocusClasses(isFocused, navigationMode),
    "data-webos-focusable": !options.disabled,
    "data-focused": isFocused,
    ...(focusContext && {
      onFocus: handleNativeFocus,
      onKeyDown: handleKeyDown,
    }),
  };

  return {
    id,
    isFocused,
    navigationMode,
    ref: elementRef,
    focusableProps,
    // Expose context functions for advanced use
    setFocused: focusContext
      ? () => focusContext.setFocusedElement(id)
      : () => elementRef.current?.focus(),
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
  const focusContext = useFocusContextSafe();
  const [localNavigationMode, setLocalNavigationMode] = useState<NavigationMode>("pointer");

  const navigationMode = focusContext?.navigationMode ?? localNavigationMode;

  useEffect(() => {
    // Check if running on WebOS TV
    const isWebOS =
      typeof window !== "undefined" &&
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;

    if (isWebOS) {
      setLocalNavigationMode("5way");
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      // Arrow keys
      if ([37, 38, 39, 40].includes(e.keyCode)) {
        setLocalNavigationMode("5way");

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

      // Back button (webOS TV) or Escape
      if ((e.keyCode === 461 || e.keyCode === 27) && options.onBack) {
        const handled = options.onBack();
        if (handled) {
          e.preventDefault();
        }
      }
    };

    const handlePointerMove = () => setLocalNavigationMode("pointer");

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
  navigationMode: NavigationMode
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

/**
 * Get focus classes for use in components
 * Exported for use in custom components
 */
export { getFocusClasses };
