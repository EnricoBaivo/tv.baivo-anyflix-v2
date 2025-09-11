import { useEffect, useState, useRef, useCallback } from 'react';

interface WebOSFocusOptions {
  onFocus?: () => void;
  onBlur?: () => void;
  onEnter?: () => void;
  onBack?: () => boolean; // Return true if handled, false to continue default behavior
  disabled?: boolean;
}

interface WebOSNavigationOptions {
  containerRef?: React.RefObject<HTMLElement>;
  onNavigate?: (direction: 'left' | 'right' | 'up' | 'down') => boolean;
  onBack?: () => boolean;
  onOk?: () => void;
  autoFocus?: boolean;
}

// Enhanced hook for webOS TV navigation
export const useWebOSNavigation = (options: WebOSNavigationOptions = {}) => {
  const [navigationMode, setNavigationMode] = useState<'pointer' | '5way'>('pointer');
  const [focusedIndex, setFocusedIndex] = useState(0);
  const focusableElements = useRef<HTMLElement[]>([]);

  // webOS TV key codes - defined outside useCallback to avoid dependency issues
  const KEY_CODES = useRef({
    LEFT: 37,
    UP: 38,
    RIGHT: 39,
    DOWN: 40,
    OK: 13,
    BACK: 461, // webOS TV Back button
  });

  // Update focusable elements
  const updateFocusableElements = useCallback(() => {
    if (!options.containerRef?.current) return;
    
    const elements = options.containerRef.current.querySelectorAll(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ) as NodeListOf<HTMLElement>;
    
    focusableElements.current = Array.from(elements);
  }, [options.containerRef]);

  // Handle webOS TV navigation
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const keyCodes = KEY_CODES.current;
    switch (event.keyCode) {
      case keyCodes.LEFT:
        event.preventDefault();
        if (navigationMode === '5way') {
          const handled = options.onNavigate?.('left');
          if (!handled) {
            setFocusedIndex((prev) => {
              const newIndex = prev > 0 ? prev - 1 : focusableElements.current.length - 1;
              focusableElements.current[newIndex]?.focus();
              return newIndex;
            });
          }
        }
        break;

      case keyCodes.RIGHT:
        event.preventDefault();
        if (navigationMode === '5way') {
          const handled = options.onNavigate?.('right');
          if (!handled) {
            setFocusedIndex((prev) => {
              const newIndex = prev < focusableElements.current.length - 1 ? prev + 1 : 0;
              focusableElements.current[newIndex]?.focus();
              return newIndex;
            });
          }
        }
        break;

      case keyCodes.UP:
        event.preventDefault();
        if (navigationMode === '5way') {
          options.onNavigate?.('up');
        }
        break;

      case keyCodes.DOWN:
        event.preventDefault();
        if (navigationMode === '5way') {
          options.onNavigate?.('down');
        }
        break;

      case keyCodes.OK:
        if (navigationMode === '5way') {
          const focusedElement = focusableElements.current[focusedIndex];
          if (focusedElement) {
            focusedElement.click();
          }
          options.onOk?.();
        }
        break;

      case keyCodes.BACK: {
        event.preventDefault();
        const handled = options.onBack?.();
        if (!handled) {
          // Default webOS TV back behavior
          if (window.history.length > 1) {
            window.history.back();
          } else {
            // Show exit confirmation on webOS TV 6.0+
            const confirmExit = window.confirm('Do you want to exit the app?');
            if (confirmExit) {
              window.close();
            }
          }
        }
        break;
      }
    }
  }, [navigationMode, focusedIndex, options]);

  // Detect navigation mode
  const handlePointerMove = useCallback(() => {
    setNavigationMode('pointer');
  }, []);

  const handleNavigationKeyDown = useCallback((e: KeyboardEvent) => {
    if ([37, 38, 39, 40].includes(e.keyCode)) { // Arrow keys
      setNavigationMode('5way');
    }
  }, []);

  useEffect(() => {
    // Check if running on WebOS TV
    const isWebOS = typeof window !== 'undefined' && 
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;
    
    if (isWebOS) {
      setNavigationMode('5way');
    }

    updateFocusableElements();
    
    // Add event listeners
    window.addEventListener('keydown', handleKeyDown);
    document.addEventListener('pointermove', handlePointerMove);
    document.addEventListener('keydown', handleNavigationKeyDown);
    
    // Set initial focus for 5-way navigation
    if (options.autoFocus && navigationMode === '5way' && focusableElements.current.length > 0) {
      focusableElements.current[0]?.focus();
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('pointermove', handlePointerMove);
      document.removeEventListener('keydown', handleNavigationKeyDown);
    };
  }, [handleKeyDown, handlePointerMove, handleNavigationKeyDown, updateFocusableElements, navigationMode, options.autoFocus]);

  return {
    navigationMode,
    focusedIndex,
    updateFocusableElements,
    focusableElements: focusableElements.current,
  };
};

export const useWebOSFocus = (options: WebOSFocusOptions = {}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [navigationMode, setNavigationMode] = useState<'pointer' | '5way'>('pointer');

  useEffect(() => {
    // Check if running on WebOS TV
    const isWebOS = typeof window !== 'undefined' && 
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).webOS !== undefined;
    
    if (isWebOS) {
      setNavigationMode('5way');
    }

    // Listen for navigation mode changes
    const handlePointerMove = () => setNavigationMode('pointer');
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        setNavigationMode('5way');
      }
      // Handle back button
      if (e.keyCode === 461 && options.onBack) {
        e.preventDefault();
        options.onBack();
      }
    };

    document.addEventListener('pointermove', handlePointerMove);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('pointermove', handlePointerMove);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [options]);

  const focusProps = {
    tabIndex: options.disabled ? -1 : 0,
    'data-webos-focusable': !options.disabled,
    onFocus: () => {
      if (!options.disabled) {
        setIsFocused(true);
        options.onFocus?.();
      }
    },
    onBlur: () => {
      setIsFocused(false);
      options.onBlur?.();
    },
    onKeyDown: (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !options.disabled) {
        e.preventDefault();
        options.onEnter?.();
      }
    },
  };

  return {
    isFocused,
    navigationMode,
    focusProps,
    focusClasses: getFocusClasses(isFocused, navigationMode),
  };
};

const getFocusClasses = (isFocused: boolean, navigationMode: 'pointer' | '5way') => {
  if (!isFocused) return '';
  
  const baseClasses = 'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2';
  const animationClasses = 'transition-all duration-200 ease-out';
  
  // More prominent focus ring for 5-way navigation
  if (navigationMode === '5way') {
    return `${baseClasses} focus:ring-offset-4 focus:shadow-lg focus:shadow-primary/30 ${animationClasses}`;
  }
  
  // Subtle focus ring for pointer navigation
  return `${baseClasses} focus:ring-offset-1 ${animationClasses}`;
};
