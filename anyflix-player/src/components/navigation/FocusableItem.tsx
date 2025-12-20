import React, { useEffect, useRef, useId, useCallback } from "react";
import {
  useFocusContext,
  type FocusableElementData,
} from "../../contexts/FocusContext";
import { useFocusZone } from "./FocusZone";
import { cn } from "../../lib/utils";

export interface FocusableItemProps {
  /** Unique identifier for this item (auto-generated if not provided) */
  id?: string;
  /** Callback when item is selected (Enter key pressed) */
  onSelect?: () => void;
  /** Callback when item receives focus */
  onFocus?: () => void;
  /** Callback when item loses focus */
  onBlur?: () => void;
  /** Whether the item is disabled */
  disabled?: boolean;
  /** Whether to auto-focus this item on mount */
  autoFocus?: boolean;
  /** Additional class names */
  className?: string;
  /** Focus ring class names (added when focused) */
  focusClassName?: string;
  /** Children elements */
  children: React.ReactNode;
  /** HTML element to render as (default: div) */
  as?: keyof JSX.IntrinsicElements;
  /** Additional props to pass to the element */
  [key: string]: unknown;
}

// Default focus ring styles
const defaultFocusClassName =
  "ring-2 ring-primary ring-offset-2 ring-offset-background";
const enhancedFocusClassName =
  "ring-offset-4 shadow-lg shadow-primary/30 scale-105";

/**
 * FocusableItem - Individual focusable element within a FocusZone
 *
 * Wrapper that makes any element focusable and integrates with
 * the spatial navigation system.
 *
 * @example
 * <FocusableItem id="card-1" onSelect={() => navigate('/detail')}>
 *   <MediaCard ... />
 * </FocusableItem>
 */
export const FocusableItem: React.FC<FocusableItemProps> = ({
  id: providedId,
  onSelect,
  onFocus: onFocusProp,
  onBlur: onBlurProp,
  disabled = false,
  autoFocus = false,
  className,
  focusClassName = defaultFocusClassName,
  children,
  as: Component = "div",
  ...rest
}) => {
  const autoId = useId();
  const id = providedId || `item-${autoId}`;
  const elementRef = useRef<HTMLDivElement>(null);

  // Use refs for callbacks to avoid re-registration on every render
  const onSelectRef = useRef(onSelect);
  const onFocusPropRef = useRef(onFocusProp);
  const onBlurPropRef = useRef(onBlurProp);

  // Keep refs updated
  useEffect(() => {
    onSelectRef.current = onSelect;
    onFocusPropRef.current = onFocusProp;
    onBlurPropRef.current = onBlurProp;
  });

  const focusZone = useFocusZone();
  const {
    registerElement,
    unregisterElement,
    focusedElementId,
    setFocusedElement,
    navigationMode,
  } = useFocusContext();

  const isFocused = focusedElementId === id;
  const is5Way = navigationMode === "5way";

  // Handle focus callback
  const handleFocus = useCallback(() => {
    if (!disabled) {
      setFocusedElement(id);
      onFocusProp?.();
    }
  }, [disabled, id, setFocusedElement, onFocusProp]);

  // Handle blur callback
  const handleBlur = useCallback(() => {
    onBlurProp?.();
  }, [onBlurProp]);

  // Handle select (Enter key or click)
  const handleSelect = useCallback(() => {
    if (!disabled) {
      onSelect?.();
    }
  }, [disabled, onSelect]);

  // Register element on mount - use refs for callbacks to avoid re-registration
  useEffect(() => {
    const element = elementRef.current;
    if (!element || !focusZone) return;

    const elementData: FocusableElementData = {
      id,
      zoneId: focusZone.zoneId,
      ref: element,
      disabled,
      // Use wrapper functions that call the refs
      onFocus: () => onFocusPropRef.current?.(),
      onBlur: () => onBlurPropRef.current?.(),
      onSelect: () => onSelectRef.current?.(),
    };

    registerElement(elementData);

    return () => {
      unregisterElement(id);
    };
  }, [
    id,
    focusZone,
    disabled,
    // Don't include callback props - use refs instead
    registerElement,
    unregisterElement,
  ]);

  // Handle auto-focus
  useEffect(() => {
    if (autoFocus && !disabled && elementRef.current) {
      // Delay to ensure element is registered
      const timer = setTimeout(() => {
        setFocusedElement(id);
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [autoFocus, disabled, id, setFocusedElement]);

  // Handle native focus events
  const handleNativeFocus = useCallback(
    (e: React.FocusEvent) => {
      // Prevent infinite loop - only handle if not already focused via context
      if (focusedElementId !== id) {
        handleFocus();
      }
    },
    [focusedElementId, id, handleFocus]
  );

  // Handle keyboard events
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Enter key - select
      if (e.keyCode === 13 || e.key === "Enter") {
        e.preventDefault();
        handleSelect();
      }
    },
    [handleSelect]
  );

  // Handle click
  const handleClick = useCallback(() => {
    handleFocus();
    handleSelect();
  }, [handleFocus, handleSelect]);

  // Build class names
  const focusRingClasses = isFocused
    ? cn(focusClassName, is5Way && enhancedFocusClassName)
    : "";

  return (
    <Component
      ref={elementRef as React.Ref<HTMLDivElement>}
      tabIndex={disabled ? -1 : 0}
      className={cn(
        "outline-none transition-all duration-200 ease-out",
        className,
        focusRingClasses
      )}
      data-focusable-item={id}
      data-focused={isFocused}
      data-disabled={disabled}
      data-webos-focusable={!disabled}
      aria-disabled={disabled}
      onFocus={handleNativeFocus}
      onBlur={handleBlur}
      onKeyDown={handleKeyDown}
      onClick={handleClick}
      {...rest}
    >
      {children}
    </Component>
  );
};

/**
 * Hook to create focusable item props for existing components
 *
 * Use this when you can't wrap the component with FocusableItem
 *
 * @example
 * const focusProps = useFocusableItemProps({
 *   id: 'my-button',
 *   onSelect: handleClick,
 * });
 * return <button {...focusProps}>Click me</button>;
 */
export const useFocusableItemProps = (options: {
  id?: string;
  onSelect?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  disabled?: boolean;
}) => {
  const autoId = useId();
  const id = options.id || `item-${autoId}`;
  const elementRef = useRef<HTMLElement>(null);

  const focusZone = useFocusZone();
  const {
    registerElement,
    unregisterElement,
    focusedElementId,
    setFocusedElement,
    navigationMode,
  } = useFocusContext();

  const isFocused = focusedElementId === id;
  const is5Way = navigationMode === "5way";

  // Register element on mount
  useEffect(() => {
    const element = elementRef.current;
    if (!element || !focusZone) return;

    const elementData: FocusableElementData = {
      id,
      zoneId: focusZone.zoneId,
      ref: element,
      disabled: options.disabled,
      onFocus: options.onFocus,
      onBlur: options.onBlur,
      onSelect: options.onSelect,
    };

    registerElement(elementData);

    return () => {
      unregisterElement(id);
    };
  }, [
    id,
    focusZone,
    options.disabled,
    options.onFocus,
    options.onBlur,
    options.onSelect,
    registerElement,
    unregisterElement,
  ]);

  const handleFocus = useCallback(() => {
    if (!options.disabled) {
      setFocusedElement(id);
      options.onFocus?.();
    }
  }, [options.disabled, options.onFocus, id, setFocusedElement]);

  const handleBlur = useCallback(() => {
    options.onBlur?.();
  }, [options.onBlur]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.keyCode === 13 || e.key === "Enter") {
        e.preventDefault();
        options.onSelect?.();
      }
    },
    [options.onSelect]
  );

  const handleClick = useCallback(() => {
    handleFocus();
    options.onSelect?.();
  }, [handleFocus, options.onSelect]);

  // Focus ring classes
  const focusClassName = isFocused
    ? cn(
        "ring-2 ring-primary ring-offset-2 ring-offset-background",
        is5Way && "ring-offset-4 shadow-lg shadow-primary/30 scale-105"
      )
    : "";

  return {
    ref: elementRef,
    tabIndex: options.disabled ? -1 : 0,
    className: focusClassName,
    "data-focusable-item": id,
    "data-focused": isFocused,
    "data-disabled": options.disabled,
    "data-webos-focusable": !options.disabled,
    "aria-disabled": options.disabled,
    onFocus: handleFocus,
    onBlur: handleBlur,
    onKeyDown: handleKeyDown,
    onClick: handleClick,
    isFocused,
    navigationMode,
  };
};

export default FocusableItem;
