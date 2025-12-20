import React, {
  createContext,
  useContext,
  useCallback,
  useRef,
  useState,
  useMemo,
} from "react";
import {
  findNextFocusable,
  findNearestInZone,
} from "../lib/spatial-navigation";

// Direction type for navigation
export type Direction = "left" | "right" | "up" | "down";

// Navigation mode - pointer (mouse/magic remote) or 5-way (directional pad)
export type NavigationMode = "pointer" | "5way";

// Zone types for different navigation behaviors
export type ZoneType = "row" | "grid" | "modal" | "menu";

// Focusable element registration
export interface FocusableElementData {
  id: string;
  zoneId: string;
  ref: HTMLElement;
  disabled?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onSelect?: () => void;
}

// Focus zone configuration
export interface FocusZoneData {
  id: string;
  type: ZoneType;
  priority: number;
  trapFocus?: boolean;
  rememberFocus?: boolean;
  navigationAxis?: "horizontal" | "vertical" | "both";
  onZoneFocus?: () => void;
  onZoneBlur?: () => void;
}

// Context value interface
interface FocusContextValue {
  // Current focus state
  activeZoneId: string | null;
  focusedElementId: string | null;
  navigationMode: NavigationMode;

  // Zone management
  registerZone: (zone: FocusZoneData) => void;
  unregisterZone: (zoneId: string) => void;
  getZone: (zoneId: string) => FocusZoneData | undefined;
  getZones: () => FocusZoneData[];

  // Element management
  registerElement: (element: FocusableElementData) => void;
  unregisterElement: (elementId: string) => void;
  getElement: (elementId: string) => FocusableElementData | undefined;
  getElementsByZone: (zoneId: string) => FocusableElementData[];

  // Navigation
  moveFocus: (direction: Direction) => boolean;
  setFocusedElement: (elementId: string | null) => void;
  setActiveZone: (zoneId: string | null) => void;

  // Focus memory per zone
  getFocusMemory: (zoneId: string) => string | undefined;
  setFocusMemory: (zoneId: string, elementId: string) => void;

  // Mode switching
  setNavigationMode: (mode: NavigationMode) => void;

  // Modal/overlay management
  pushFocusLayer: (zoneId: string) => void;
  popFocusLayer: () => string | null;
  getFocusLayerStack: () => string[];
}

// Create context with undefined default
const FocusContext = createContext<FocusContextValue | undefined>(undefined);

// Provider props
interface FocusProviderProps {
  children: React.ReactNode;
  defaultNavigationMode?: NavigationMode;
}

/**
 * FocusProvider - Global focus state management for webOS TV navigation
 *
 * Manages:
 * - Focus zones (rows, grids, modals)
 * - Focusable elements within zones
 * - Navigation mode (pointer vs 5-way)
 * - Focus memory per zone
 * - Modal focus layer stack
 */
export const FocusProvider: React.FC<FocusProviderProps> = ({
  children,
  defaultNavigationMode = "pointer",
}) => {
  // State
  const [activeZoneId, setActiveZoneId] = useState<string | null>(null);
  const [focusedElementId, setFocusedElementIdStateInternal] = useState<string | null>(
    null
  );

  const setFocusedElementIdState = useCallback((value: string | null) => {
    setFocusedElementIdStateInternal(value);
  }, []);
  const [navigationMode, setNavigationModeState] =
    useState<NavigationMode>(defaultNavigationMode);

  // Refs for storing registrations (avoid re-renders on every registration)
  const zonesRef = useRef<Map<string, FocusZoneData>>(new Map());
  const elementsRef = useRef<Map<string, FocusableElementData>>(new Map());
  const focusMemoryRef = useRef<Map<string, string>>(new Map());
  const focusLayerStackRef = useRef<string[]>([]);
  // Ref to track current focused element for use in stable callbacks
  const focusedElementIdRef = useRef<string | null>(null);

  // Keep ref in sync with state
  React.useEffect(() => {
    focusedElementIdRef.current = focusedElementId;
  }, [focusedElementId]);

  // Detect webOS and set initial mode
  React.useEffect(() => {
    const isWebOS =
      typeof window !== "undefined" &&
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;

    if (isWebOS) {
      setNavigationModeState("5way");
    }
  }, []);

  // Zone management
  const registerZone = useCallback((zone: FocusZoneData) => {
    zonesRef.current.set(zone.id, zone);
  }, []);

  const unregisterZone = useCallback((zoneId: string) => {
    zonesRef.current.delete(zoneId);
    // Clean up focus memory for this zone
    focusMemoryRef.current.delete(zoneId);
  }, []);

  const getZone = useCallback((zoneId: string) => {
    return zonesRef.current.get(zoneId);
  }, []);

  const getZones = useCallback(() => {
    return Array.from(zonesRef.current.values());
  }, []);

  // Element management
  const registerElement = useCallback((element: FocusableElementData) => {
    elementsRef.current.set(element.id, element);
  }, []);

  const unregisterElement = useCallback(
    (elementId: string) => {
      const element = elementsRef.current.get(elementId);
      if (element) {
        // If this element was focused, clear focus
        // Use ref to avoid dependency on focusedElementId state
        if (focusedElementIdRef.current === elementId) {
          setFocusedElementIdState(null);
        }
        // Clean up from focus memory if needed
        const zoneMemory = focusMemoryRef.current.get(element.zoneId);
        if (zoneMemory === elementId) {
          focusMemoryRef.current.delete(element.zoneId);
        }
      }
      elementsRef.current.delete(elementId);
    },
    [] // No dependencies - uses refs for current values
  );

  const getElement = useCallback((elementId: string) => {
    return elementsRef.current.get(elementId);
  }, []);

  const getElementsByZone = useCallback((zoneId: string) => {
    const elements: FocusableElementData[] = [];
    elementsRef.current.forEach((element) => {
      if (element.zoneId === zoneId && !element.disabled) {
        elements.push(element);
      }
    });
    return elements;
  }, []);

  // Focus memory
  const getFocusMemory = useCallback((zoneId: string) => {
    return focusMemoryRef.current.get(zoneId);
  }, []);

  const setFocusMemory = useCallback((zoneId: string, elementId: string) => {
    focusMemoryRef.current.set(zoneId, elementId);
  }, []);

  // Focus layer stack (for modals)
  const pushFocusLayer = useCallback((zoneId: string) => {
    focusLayerStackRef.current.push(zoneId);
    setActiveZoneId(zoneId);
  }, []);

  const popFocusLayer = useCallback(() => {
    const popped = focusLayerStackRef.current.pop();
    const newTop =
      focusLayerStackRef.current[focusLayerStackRef.current.length - 1] || null;
    setActiveZoneId(newTop);
    return popped || null;
  }, []);

  const getFocusLayerStack = useCallback(() => {
    return [...focusLayerStackRef.current];
  }, []);

  // Set focused element with callbacks
  const setFocusedElement = useCallback(
    (elementId: string | null) => {
      const previousElement = focusedElementId
        ? elementsRef.current.get(focusedElementId)
        : null;
      const newElement = elementId
        ? elementsRef.current.get(elementId)
        : null;

      // Call blur on previous element
      if (previousElement && previousElement.id !== elementId) {
        previousElement.onBlur?.();
      }

      // Update state
      setFocusedElementIdState(elementId);

      // Update active zone
      if (newElement) {
        setActiveZoneId(newElement.zoneId);

        // Store in focus memory
        const zone = zonesRef.current.get(newElement.zoneId);
        if (zone?.rememberFocus) {
          focusMemoryRef.current.set(newElement.zoneId, elementId!);
        }

        // Focus the actual DOM element
        newElement.ref.focus({ preventScroll: false });

        // Call focus callback
        newElement.onFocus?.();
      }
    },
    [focusedElementId]
  );

  // Set active zone
  const setActiveZone = useCallback((zoneId: string | null) => {
    setActiveZoneId(zoneId);
  }, []);

  // Navigation mode
  const setNavigationMode = useCallback((mode: NavigationMode) => {
    setNavigationModeState(mode);
  }, []);

  // Move focus in a direction
  const moveFocus = useCallback(
    (direction: Direction): boolean => {
      const currentElement = focusedElementId
        ? elementsRef.current.get(focusedElementId)
        : null;

      // Get current zone or top layer zone
      const currentZoneId =
        focusLayerStackRef.current[focusLayerStackRef.current.length - 1] ||
        activeZoneId;
      const currentZone = currentZoneId
        ? zonesRef.current.get(currentZoneId)
        : null;

      // If in a modal with trapFocus, only navigate within that zone
      if (currentZone?.trapFocus) {
        const elementsInZone = getElementsByZone(currentZone.id);
        if (currentElement && elementsInZone.length > 0) {
          const nextElement = findNextFocusable(
            currentElement.ref,
            direction,
            elementsInZone.map((e) => e.ref),
            currentZone.navigationAxis || "both"
          );

          if (nextElement) {
            const nextElementData = Array.from(elementsRef.current.values()).find(
              (e) => e.ref === nextElement
            );
            if (nextElementData) {
              setFocusedElement(nextElementData.id);
              return true;
            }
          }
        }
        return false;
      }

      // Normal navigation - first try within current zone
      if (currentElement && currentZone) {
        const elementsInZone = getElementsByZone(currentZone.id);
        const nextElement = findNextFocusable(
          currentElement.ref,
          direction,
          elementsInZone.map((e) => e.ref),
          currentZone.navigationAxis || "both"
        );

        if (nextElement) {
          const nextElementData = Array.from(elementsRef.current.values()).find(
            (e) => e.ref === nextElement
          );
          if (nextElementData) {
            setFocusedElement(nextElementData.id);
            return true;
          }
        }
      }

      // Try to navigate to adjacent zone
      const zones = Array.from(zonesRef.current.values())
        .filter((z) => !z.trapFocus) // Skip modal zones
        .sort((a, b) => a.priority - b.priority);

      if (zones.length === 0) return false;

      // For up/down navigation, find adjacent zone
      if (direction === "up" || direction === "down") {
        const currentZoneIndex = zones.findIndex((z) => z.id === currentZoneId);

        let targetZone: FocusZoneData | undefined;
        if (direction === "up" && currentZoneIndex > 0) {
          targetZone = zones[currentZoneIndex - 1];
        } else if (direction === "down" && currentZoneIndex < zones.length - 1) {
          targetZone = zones[currentZoneIndex + 1];
        }

        if (targetZone) {
          // Check for focus memory
          const rememberedElementId = focusMemoryRef.current.get(targetZone.id);
          if (rememberedElementId) {
            const rememberedElement = elementsRef.current.get(rememberedElementId);
            if (rememberedElement && !rememberedElement.disabled) {
              setFocusedElement(rememberedElementId);
              return true;
            }
          }

          // Find nearest element in target zone
          const targetElements = getElementsByZone(targetZone.id);
          if (targetElements.length > 0 && currentElement) {
            const nearestElement = findNearestInZone(
              currentElement.ref,
              targetElements.map((e) => e.ref)
            );

            if (nearestElement) {
              const nearestData = Array.from(elementsRef.current.values()).find(
                (e) => e.ref === nearestElement
              );
              if (nearestData) {
                setFocusedElement(nearestData.id);
                return true;
              }
            }
          }
        }
      }

      return false;
    },
    [
      focusedElementId,
      activeZoneId,
      getElementsByZone,
      setFocusedElement,
    ]
  );

  // Memoize context value
  const value = useMemo<FocusContextValue>(
    () => ({
      activeZoneId,
      focusedElementId,
      navigationMode,
      registerZone,
      unregisterZone,
      getZone,
      getZones,
      registerElement,
      unregisterElement,
      getElement,
      getElementsByZone,
      moveFocus,
      setFocusedElement,
      setActiveZone,
      getFocusMemory,
      setFocusMemory,
      setNavigationMode,
      pushFocusLayer,
      popFocusLayer,
      getFocusLayerStack,
    }),
    [
      activeZoneId,
      focusedElementId,
      navigationMode,
      registerZone,
      unregisterZone,
      getZone,
      getZones,
      registerElement,
      unregisterElement,
      getElement,
      getElementsByZone,
      moveFocus,
      setFocusedElement,
      setActiveZone,
      getFocusMemory,
      setFocusMemory,
      setNavigationMode,
      pushFocusLayer,
      popFocusLayer,
      getFocusLayerStack,
    ]
  );

  return (
    <FocusContext.Provider value={value}>{children}</FocusContext.Provider>
  );
};

/**
 * Hook to access focus context
 * @throws Error if used outside FocusProvider
 */
export const useFocusContext = (): FocusContextValue => {
  const context = useContext(FocusContext);
  if (context === undefined) {
    throw new Error("useFocusContext must be used within a FocusProvider");
  }
  return context;
};

/**
 * Hook to optionally access focus context (returns null if not in provider)
 */
export const useFocusContextSafe = (): FocusContextValue | null => {
  return useContext(FocusContext) || null;
};

export default FocusContext;
