import { useEffect, useState } from 'react';

interface WebOSFocusOptions {
  onFocus?: () => void;
  onBlur?: () => void;
  onEnter?: () => void;
  disabled?: boolean;
}

export const useWebOSFocus = (options: WebOSFocusOptions = {}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [navigationMode, setNavigationMode] = useState<'pointer' | '5way'>('pointer');

  useEffect(() => {
    // Detect WebOS navigation mode
    const detectNavigationMode = () => {
      // Check if running on WebOS TV
      const isWebOS = typeof window !== 'undefined' && 
        (window as any).webOS !== undefined;
      
      if (isWebOS) {
        // Default to 5-way for TV
        setNavigationMode('5way');
      }
    };

    detectNavigationMode();

    // Listen for navigation mode changes
    const handlePointerMove = () => setNavigationMode('pointer');
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        setNavigationMode('5way');
      }
    };

    document.addEventListener('pointermove', handlePointerMove);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('pointermove', handlePointerMove);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

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
  
  const baseClasses = 'ring-2 ring-white ring-offset-2 ring-offset-black/50';
  const animationClasses = 'transition-all duration-200 ease-out';
  
  // More prominent focus ring for 5-way navigation
  if (navigationMode === '5way') {
    return `${baseClasses} ring-offset-4 shadow-lg shadow-white/30 ${animationClasses}`;
  }
  
  // Subtle focus ring for pointer navigation
  return `${baseClasses} ring-offset-1 ${animationClasses}`;
};
