import React, { useEffect, useRef, useId, useMemo } from "react";
import {
  useFocusContext,
  type ZoneType,
  type FocusZoneData,
} from "../../contexts/FocusContext";

export interface FocusZoneProps {
  /** Unique identifier for this zone (auto-generated if not provided) */
  id?: string;
  /** Type of zone - affects navigation behavior */
  type?: ZoneType;
  /** Priority for zone ordering (lower = higher priority, used for up/down navigation) */
  priority?: number;
  /** Whether focus should be trapped within this zone (for modals) */
  trapFocus?: boolean;
  /** Whether to remember the last focused element when leaving this zone */
  rememberFocus?: boolean;
  /** Navigation axis constraint */
  navigationAxis?: "horizontal" | "vertical" | "both";
  /** Callback when zone receives focus */
  onZoneFocus?: () => void;
  /** Callback when zone loses focus */
  onZoneBlur?: () => void;
  /** Additional class names */
  className?: string;
  /** Children elements */
  children: React.ReactNode;
  /** Whether this zone should be treated as a modal (pushes to focus layer stack) */
  isModal?: boolean;
  /** HTML element to render as (default: div) */
  as?: keyof JSX.IntrinsicElements;
}

/**
 * FocusZone - Container for a group of focusable elements
 *
 * Defines a navigation region for the spatial navigation system.
 * Elements within a zone can be navigated using arrow keys.
 *
 * @example
 * <FocusZone id="popular-row" type="row" rememberFocus>
 *   <FocusableItem id="card-1">Card 1</FocusableItem>
 *   <FocusableItem id="card-2">Card 2</FocusableItem>
 * </FocusZone>
 */
export const FocusZone: React.FC<FocusZoneProps> = ({
  id: providedId,
  type = "row",
  priority = 0,
  trapFocus = false,
  rememberFocus = true,
  navigationAxis = type === "row" ? "horizontal" : "both",
  onZoneFocus,
  onZoneBlur,
  className,
  children,
  isModal = false,
  as: Component = "div",
}) => {
  const autoId = useId();
  const id = providedId || `zone-${autoId}`;
  const containerRef = useRef<HTMLDivElement>(null);
  const wasActiveRef = useRef(false);

  const {
    registerZone,
    unregisterZone,
    activeZoneId,
    pushFocusLayer,
    popFocusLayer,
  } = useFocusContext();

  // Register zone on mount
  useEffect(() => {
    const zoneData: FocusZoneData = {
      id,
      type,
      priority,
      trapFocus: trapFocus || isModal,
      rememberFocus,
      navigationAxis,
      onZoneFocus,
      onZoneBlur,
    };

    registerZone(zoneData);

    // If this is a modal, push to focus layer stack
    if (isModal) {
      pushFocusLayer(id);
    }

    return () => {
      // If this is a modal, pop from focus layer stack
      if (isModal) {
        popFocusLayer();
      }
      unregisterZone(id);
    };
  }, [
    id,
    type,
    priority,
    trapFocus,
    rememberFocus,
    navigationAxis,
    isModal,
    registerZone,
    unregisterZone,
    pushFocusLayer,
    popFocusLayer,
    onZoneFocus,
    onZoneBlur,
  ]);

  // Track zone focus changes
  useEffect(() => {
    const isActive = activeZoneId === id;

    if (isActive && !wasActiveRef.current) {
      // Zone just became active
      onZoneFocus?.();
    } else if (!isActive && wasActiveRef.current) {
      // Zone just became inactive
      onZoneBlur?.();
    }

    wasActiveRef.current = isActive;
  }, [activeZoneId, id, onZoneFocus, onZoneBlur]);

  // Create context value for children to access zone info - memoized to prevent re-renders
  const zoneContext = useMemo(() => ({
    zoneId: id,
    zoneType: type,
  }), [id, type]);

  return (
    <FocusZoneContext.Provider value={zoneContext}>
      <Component
        ref={containerRef as React.Ref<HTMLDivElement>}
        className={className}
        data-focus-zone={id}
        data-focus-zone-type={type}
        data-focus-zone-active={activeZoneId === id}
      >
        {children}
      </Component>
    </FocusZoneContext.Provider>
  );
};

// Context for FocusableItem to access parent zone info
interface FocusZoneContextValue {
  zoneId: string;
  zoneType: ZoneType;
}

const FocusZoneContext = React.createContext<FocusZoneContextValue | null>(null);

/**
 * Hook to access parent FocusZone context
 */
export const useFocusZone = (): FocusZoneContextValue | null => {
  return React.useContext(FocusZoneContext);
};

export default FocusZone;
