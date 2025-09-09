import { cn } from './utils';

/**
 * WebOS TV Focus Ring Utilities
 * Following WebOS best practices for TV navigation
 */

export const focusRingClasses = {
  // Base focus ring for all interactive elements
  base: 'focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black/50',
  
  // Enhanced focus for 5-way navigation (TV remote)
  enhanced: 'focus:ring-offset-4 focus:shadow-lg focus:shadow-white/30',
  
  // Subtle focus for pointer navigation (mouse/touch)
  subtle: 'focus:ring-offset-1',
  
  // Animation for smooth transitions
  animated: 'transition-all duration-200 ease-out',
  
  // Button specific focus
  button: 'focus:ring-white/80 focus:ring-offset-black',
  
  // Card specific focus (for movie cards)
  card: 'focus:ring-white focus:ring-offset-transparent focus:shadow-xl focus:shadow-white/20',
};

/**
 * Get focus classes based on element type and navigation mode
 */
export const getFocusClasses = (
  type: 'button' | 'card' | 'input' = 'button',
  navigationMode: '5way' | 'pointer' = '5way'
) => {
  const baseClasses = [
    focusRingClasses.base,
    focusRingClasses.animated,
  ];

  switch (type) {
    case 'button':
      baseClasses.push(focusRingClasses.button);
      break;
    case 'card':
      baseClasses.push(focusRingClasses.card);
      break;
  }

  if (navigationMode === '5way') {
    baseClasses.push(focusRingClasses.enhanced);
  } else {
    baseClasses.push(focusRingClasses.subtle);
  }

  return cn(...baseClasses);
};

/**
 * WebOS focusable element props
 */
export const getWebOSProps = (disabled = false) => ({
  tabIndex: disabled ? -1 : 0,
  'data-webos-focusable': !disabled,
  'data-webos-sound': true,
});
