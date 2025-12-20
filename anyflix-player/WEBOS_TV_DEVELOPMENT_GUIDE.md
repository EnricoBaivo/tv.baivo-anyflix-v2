# WebOS TV Development Guide for LLMs

> **Purpose:** This document contains comprehensive learnings for developing web applications targeting LG webOS TV platforms. Use this as a reference when assisting with webOS TV app development.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Browser Engine Versions by webOS Version](#browser-engine-versions-by-webos-version)
3. [Critical CSS Compatibility Issues](#critical-css-compatibility-issues)
4. [JavaScript Compatibility](#javascript-compatibility)
5. [Hardware Acceleration & Rendering](#hardware-acceleration--rendering)
6. [Remote Control & Navigation](#remote-control--navigation)
7. [Modal & Overlay Best Practices](#modal--overlay-best-practices)
8. [appinfo.json Configuration](#appinfojson-configuration)
9. [Build Configuration](#build-configuration)
10. [Testing Checklist](#testing-checklist)
11. [Quick Reference: What Works / What Doesn't](#quick-reference-what-works--what-doesnt)

---

## Platform Overview

### webOS TV Architecture

webOS TV is LG's smart TV operating system. Web apps run in a Chromium-based browser engine with TV-specific APIs.

**Key Characteristics:**
- **Rendering Engine:** Chromium (version varies by webOS version)
- **Input Methods:** Magic Remote (pointer), Standard Remote (5-way D-pad)
- **Resolution:** 1920x1080 (FHD) or 3840x2160 (UHD)
- **Memory:** Limited compared to desktop browsers
- **GPU:** Hardware acceleration available but requires explicit hints

### webOS TV Version History

| webOS Version | Year | TV Models | Chromium Version |
|---------------|------|-----------|------------------|
| webOS TV 1.x | 2014 | 2014 LG TVs | WebKit-based |
| webOS TV 2.x | 2015 | 2015 LG TVs | WebKit-based |
| webOS TV 3.x | 2016-2017 | 2016-2017 LG TVs | Chromium 38 |
| webOS TV 4.x | 2018 | 2018 LG TVs | Chromium 53 |
| webOS TV 5.x | 2019-2020 | 2019-2020 LG TVs | Chromium 68 |
| webOS TV 6.x | 2021 | 2021 LG TVs | **Chromium 79** |
| webOS TV 7.x | 2022 | 2022 LG TVs | Chromium 87 |
| webOS TV 8.x | 2023 | 2023 LG TVs | Chromium 94+ |
| webOS TV 23/24 | 2023-2024 | 2023-2024 LG TVs | Chromium 108+ |

---

## Browser Engine Versions by webOS Version

### webOS TV 6.x (2021) - Chromium 79

**Release Date:** Chromium 79 was released December 10, 2019

**Critical Limitations:**
- No CSS flexbox `gap` property (added in Chrome 84)
- Buggy `backdrop-filter` support
- No optional chaining (`?.`) - added in Chrome 80
- No nullish coalescing (`??`) - added in Chrome 80
- Limited CSS Grid `gap` support

**Fully Supported:**
- ES6 features (arrow functions, classes, promises, async/await)
- CSS transforms (`transform: scale()`, `translate()`, `rotate()`)
- CSS transitions
- Flexbox (without `gap`)
- CSS Grid (without reliable `gap`)
- `getBoundingClientRect()`
- All standard DOM APIs

---

## Critical CSS Compatibility Issues

### 1. Flexbox `gap` Property - NOT SUPPORTED (Chromium 79)

**The Problem:**
```css
/* This DOES NOT work in Chromium 79 */
.container {
  display: flex;
  gap: 1rem; /* ❌ Ignored completely */
}
```

**The Solution - Use margin instead:**
```css
/* Option 1: Adjacent sibling selector */
.container {
  display: flex;
}
.container > * + * {
  margin-left: 1rem;
}

/* Option 2: Direct margin on children */
.card {
  margin-right: 1rem;
}

/* Option 3: For vertical layouts */
.container {
  display: flex;
  flex-direction: column;
}
.container > * + * {
  margin-top: 1rem;
}
```

**In React/Tailwind:**
```tsx
// ❌ WRONG - gap-4 is ignored in Chromium 79
<div className="flex gap-4">
  <Card />
  <Card />
</div>

// ✅ CORRECT - margin-right on each item
<div className="flex">
  <Card className="mr-4" />
  <Card className="mr-4" />
</div>
```

**Impact if not fixed:**
- Elements collapse together with no spacing
- Spatial navigation algorithms fail (wrong `getBoundingClientRect()` values)
- Navigation skips elements (e.g., p2 → p4 instead of p2 → p3)

### 2. `backdrop-filter` - BUGGY/BROKEN (Chromium 79)

**The Problem:**
```css
/* This causes rendering issues in Chromium 79 */
.modal-backdrop {
  backdrop-filter: blur(4px); /* ❌ Causes flickering */
  -webkit-backdrop-filter: blur(4px); /* ❌ Also buggy */
}
```

**Symptoms:**
- Elements not visible until user interaction
- Flickering when switching between pointer and 5-way modes
- Modal appearing/disappearing randomly

**The Solution:**
```css
/* Use simple solid overlay instead */
.modal-backdrop {
  background-color: black;
  opacity: 0.85;
  /* Force hardware acceleration */
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}
```

### 3. CSS Grid `gap` - LIMITED SUPPORT

```css
/* May not work reliably */
.grid {
  display: grid;
  gap: 1rem; /* ⚠️ Inconsistent support */
}

/* Use margin fallback */
.grid {
  display: grid;
  margin: -0.5rem;
}
.grid > * {
  margin: 0.5rem;
}
```

### 4. Other Unsupported CSS Features

| Feature | Chromium Support | Alternative |
|---------|------------------|-------------|
| `gap` (flexbox) | Chrome 84+ | Use margin |
| `backdrop-filter` | Chrome 76+ (buggy until 88) | Use solid overlay |
| `aspect-ratio` | Chrome 88+ | Use padding-bottom trick |
| `content-visibility` | Chrome 85+ | Not needed for TV |
| `scroll-snap-stop` | Chrome 75+ | Usually works |
| `:is()` selector | Chrome 88+ | Use individual selectors |
| `:where()` selector | Chrome 88+ | Use individual selectors |
| `clamp()` | Chrome 79+ | ✅ Supported |
| `min()` / `max()` | Chrome 79+ | ✅ Supported |

### 5. Required Vendor Prefixes (Chromium 79)

Always include `-webkit-` prefixes for these properties:

```css
.element {
  /* Transforms */
  -webkit-transform: translateZ(0);
  transform: translateZ(0);

  /* Animations */
  -webkit-animation: fadeIn 0.3s ease;
  animation: fadeIn 0.3s ease;

  /* Flexbox (for older webOS) */
  display: -webkit-flex;
  display: flex;
  -webkit-justify-content: center;
  justify-content: center;
  -webkit-align-items: center;
  align-items: center;
}

@-webkit-keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

---

## JavaScript Compatibility

### Supported ES6+ Features (Chromium 79)

```javascript
// ✅ All of these work in Chromium 79

// Arrow functions
const fn = () => {};

// Classes
class MyClass {
  constructor() {}
  method() {}
}

// Template literals
const str = `Hello ${name}`;

// Destructuring
const { a, b } = obj;
const [x, y] = arr;

// Spread operator
const newArr = [...arr, item];
const newObj = { ...obj, prop: value };

// Promises
Promise.resolve().then(() => {});

// Async/await
async function fetchData() {
  const data = await fetch(url);
}

// Map, Set, Symbol
const map = new Map();
const set = new Set();
const sym = Symbol('description');

// for...of loops
for (const item of iterable) {}

// Default parameters
function fn(a = 1, b = 2) {}

// Rest parameters
function fn(...args) {}
```

### NOT Supported in Chromium 79

```javascript
// ❌ Optional chaining - Chrome 80+
const value = obj?.nested?.property; // FAILS

// ✅ Use this instead:
const value = obj && obj.nested && obj.nested.property;
// Or with lodash: _.get(obj, 'nested.property')

// ❌ Nullish coalescing - Chrome 80+
const value = input ?? defaultValue; // FAILS

// ✅ Use this instead:
const value = input !== null && input !== undefined ? input : defaultValue;
// Or: const value = input != null ? input : defaultValue;

// ❌ BigInt literals
const big = 123n; // FAILS in some contexts

// ❌ Dynamic import() - Limited support
const module = await import('./module.js'); // May fail

// ❌ globalThis - Chrome 71+ but may have issues
// ✅ Use window instead in browser context
```

### Babel/TypeScript Target Configuration

```javascript
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        chrome: '79'
      }
    }],
    '@babel/preset-react',
    '@babel/preset-typescript'
  ],
  plugins: [
    '@babel/plugin-transform-optional-chaining',
    '@babel/plugin-transform-nullish-coalescing-operator'
  ]
};
```

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2019",
    "lib": ["ES2019", "DOM", "DOM.Iterable"],
    "module": "ESNext"
  }
}
```

---

## Hardware Acceleration & Rendering

### Why Hardware Acceleration Matters on TV

webOS TVs have:
- Limited CPU compared to desktop
- GPU available for rendering
- Layer-based compositor
- Memory constraints

Without explicit hardware acceleration hints, elements may:
- Render on CPU (slow)
- Switch between CPU/GPU randomly (flickering)
- Not composite properly with other layers

### Forcing Hardware Acceleration

```css
/* Apply to elements that need stable rendering */
.hardware-accelerated {
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  /* Or use: */
  will-change: transform;
  /* Or: */
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
```

### When to Use Hardware Acceleration

**DO use for:**
- Modal containers and backdrops
- Fixed position headers/footers
- Elements that animate
- Scrolling containers
- Video overlays

**DON'T overuse:**
- Every element (wastes GPU memory)
- Static content that never changes
- Too many layers = memory issues

### React Example

```tsx
// Modal with proper hardware acceleration
const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        // Force hardware acceleration
        transform: 'translateZ(0)',
        WebkitTransform: 'translateZ(0)',
      }}
    >
      {/* Backdrop */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'black',
          opacity: 0.85,
          transform: 'translateZ(0)',
          WebkitTransform: 'translateZ(0)',
        }}
        onClick={onClose}
      />

      {/* Content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          transform: 'translateZ(0)',
          WebkitTransform: 'translateZ(0)',
        }}
      >
        {children}
      </div>
    </div>
  );
};
```

---

## Remote Control & Navigation

### Remote Control Key Codes

```javascript
// Standard webOS TV remote key codes
const KEY_CODES = {
  // Navigation
  LEFT: 37,
  UP: 38,
  RIGHT: 39,
  DOWN: 40,

  // Action buttons
  ENTER: 13,        // OK button
  BACK: 461,        // webOS specific back button
  ESCAPE: 27,       // Browser escape (fallback for back)

  // Color buttons
  RED: 403,
  GREEN: 404,
  YELLOW: 405,
  BLUE: 406,

  // Media buttons
  PLAY: 415,
  PAUSE: 19,
  STOP: 413,
  REWIND: 412,
  FAST_FORWARD: 417,

  // Number keys
  NUM_0: 48,
  NUM_1: 49,
  // ... NUM_2 through NUM_9
  NUM_9: 57,
};
```

### Handling Back Button

```javascript
// CRITICAL: Must prevent default AND stop propagation
document.addEventListener('keydown', (event) => {
  if (event.keyCode === 461 || event.keyCode === 27) {
    // Prevent webOS from showing "Exit app?" dialog
    event.preventDefault();
    event.stopPropagation();

    // Handle back action
    if (isModalOpen) {
      closeModal();
    } else {
      // Normal back navigation
      history.back();
    }
  }
});
```

### Navigation Modes

webOS TVs have two navigation modes:

1. **Pointer Mode (Magic Remote)**
   - User moves cursor with wrist motion
   - Click to select
   - `pointermove` events fired

2. **5-Way Mode (D-Pad)**
   - Up/Down/Left/Right arrow keys
   - Enter to select
   - No pointer events

```javascript
// Detect navigation mode
let navigationMode = 'pointer';

// Switch to 5-way on arrow key press
document.addEventListener('keydown', (event) => {
  if ([37, 38, 39, 40].includes(event.keyCode)) {
    navigationMode = '5way';
  }
});

// Switch to pointer on mouse/pointer movement
document.addEventListener('pointermove', () => {
  navigationMode = 'pointer';
});

// Listen for webOS cursor state changes
document.addEventListener('cursorStateChange', (event) => {
  if (event.detail.visibility) {
    navigationMode = 'pointer';
  } else {
    navigationMode = '5way';
  }
});
```

### Spatial Navigation Algorithm

For 5-way navigation, use spatial algorithms based on element positions:

```javascript
function findNextFocusable(currentElement, direction, candidates) {
  const currentRect = currentElement.getBoundingClientRect();

  let bestCandidate = null;
  let bestScore = Infinity;

  for (const candidate of candidates) {
    if (candidate === currentElement) continue;

    const candidateRect = candidate.getBoundingClientRect();

    // Check if candidate is in the correct direction
    if (!isInDirection(currentRect, candidateRect, direction)) continue;

    // Calculate score (lower is better)
    const score = calculateNavigationScore(currentRect, candidateRect, direction);

    if (score < bestScore) {
      bestScore = score;
      bestCandidate = candidate;
    }
  }

  return bestCandidate;
}

function isInDirection(from, to, direction) {
  const fromCenterX = from.left + from.width / 2;
  const fromCenterY = from.top + from.height / 2;
  const toCenterX = to.left + to.width / 2;
  const toCenterY = to.top + to.height / 2;

  switch (direction) {
    case 'left': return toCenterX < fromCenterX;
    case 'right': return toCenterX > fromCenterX;
    case 'up': return toCenterY < fromCenterY;
    case 'down': return toCenterY > fromCenterY;
  }
}

function calculateNavigationScore(from, to, direction) {
  // Primary distance (in direction of navigation)
  const primaryDist = getPrimaryDistance(from, to, direction);

  // Perpendicular distance (how "off-axis" the element is)
  const perpDist = getPerpendicularDistance(from, to, direction);

  // Weight perpendicular more to prefer aligned elements
  return primaryDist + (perpDist * 2);
}
```

---

## Modal & Overlay Best Practices

### DO: Simple Solid Overlays

```tsx
// ✅ CORRECT - Works on all webOS versions
const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{
        transform: 'translateZ(0)',
        WebkitTransform: 'translateZ(0)',
      }}
    >
      {/* Simple solid backdrop */}
      <div
        className="fixed inset-0 bg-black"
        style={{
          opacity: 0.85,
          transform: 'translateZ(0)',
          WebkitTransform: 'translateZ(0)',
        }}
        onClick={onClose}
      />

      {/* Modal content */}
      <div
        className="relative z-10 bg-gray-900 rounded-lg p-6"
        style={{
          transform: 'translateZ(0)',
          WebkitTransform: 'translateZ(0)',
        }}
      >
        {children}
      </div>
    </div>
  );
};
```

### DON'T: Backdrop Blur or Complex Effects

```tsx
// ❌ WRONG - Causes flickering on webOS TV 6.x
<div className="backdrop-blur-sm bg-black/50" />
<div style={{ backdropFilter: 'blur(4px)' }} />

// ❌ WRONG - mix-blend-mode not supported
<div style={{ mixBlendMode: 'multiply' }} />

// ❌ WRONG - Complex filters are slow
<div style={{ filter: 'blur(10px) brightness(0.5)' }} />
```

### Focus Trapping in Modals

```javascript
// When modal opens, trap focus within it
function trapFocus(modalElement) {
  const focusableElements = modalElement.querySelectorAll(
    'button, [tabindex]:not([tabindex="-1"]), input, select, textarea, a[href]'
  );

  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  // Focus first element
  firstElement?.focus();

  // Handle Tab key to cycle within modal
  modalElement.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      lastElement?.focus();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      firstElement?.focus();
    }
  });
}
```

---

## appinfo.json Configuration

### Complete appinfo.json Example

```json
{
  "id": "com.example.myapp",
  "version": "1.0.0",
  "title": "My App",
  "vendor": "My Company",
  "type": "web",
  "main": "index.html",
  "icon": "icon.png",
  "largeIcon": "icon.png",
  "bgImage": "splash.png",

  "resolution": "1920x1080",
  "disableBackHistoryAPI": true,
  "uiRevision": "2",

  "requestedPermissions": [
    "network",
    "storage"
  ],

  "features": {
    "orientation": "landscape"
  },

  "logLevel": "debug"
}
```

### Key Settings Explained

| Setting | Value | Purpose |
|---------|-------|---------|
| `resolution` | `"1920x1080"` or `"3840x2160"` | Target display resolution |
| `disableBackHistoryAPI` | `true` | Allows custom back button handling |
| `uiRevision` | `"2"` | Enables hardware acceleration features |
| `requestedPermissions` | `["network", "storage"]` | App permissions |
| `logLevel` | `"debug"` | For development; remove for production |

### Resolution Considerations

```json
// For FHD TVs and scaling
"resolution": "1920x1080"

// For native 4K (larger assets, more memory)
"resolution": "3840x2160"
```

**Note:** If you declare 1920x1080 on a 4K TV, the app is upscaled. For best quality on all TVs, design at 1920x1080 with scalable assets.

---

## Build Configuration

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import legacy from '@vitejs/plugin-legacy';

export default defineConfig({
  base: './',
  plugins: [
    react(),
    legacy({
      targets: ['chrome 79'],
      modernPolyfills: true,
    }),
  ],
  build: {
    target: ['chrome79'],
  },
  esbuild: {
    target: 'chrome79',
  },
});
```

### Webpack Configuration

```javascript
// webpack.config.js
module.exports = {
  target: ['web', 'es5'],
  module: {
    rules: [
      {
        test: /\.(js|jsx|ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['@babel/preset-env', {
                targets: { chrome: '79' }
              }],
              '@babel/preset-react',
              '@babel/preset-typescript'
            ],
            plugins: [
              '@babel/plugin-transform-optional-chaining',
              '@babel/plugin-transform-nullish-coalescing-operator',
            ]
          }
        }
      }
    ]
  }
};
```

### PostCSS Configuration

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    'tailwindcss': {},
    'autoprefixer': {
      overrideBrowserslist: ['chrome >= 79']
    },
  }
};
```

---

## Testing Checklist

### Before Deploying to webOS TV

- [ ] **CSS Gap Property**
  - [ ] No `gap` in flexbox containers
  - [ ] Using margin-based spacing instead
  - [ ] Cards/items have proper spacing visually

- [ ] **Backdrop/Overlay**
  - [ ] No `backdrop-filter` usage
  - [ ] Modals use solid overlays
  - [ ] Hardware acceleration applied (`transform: translateZ(0)`)

- [ ] **Navigation**
  - [ ] 5-way navigation works (arrow keys)
  - [ ] Focus moves correctly between elements
  - [ ] Back button closes modals without exit dialog
  - [ ] Enter/OK key activates focused elements

- [ ] **Performance**
  - [ ] No excessive hardware-accelerated layers
  - [ ] Animations are smooth
  - [ ] No flickering when switching navigation modes

- [ ] **Build**
  - [ ] Targeting Chrome 79
  - [ ] Legacy polyfills included
  - [ ] No build warnings/errors
  - [ ] appinfo.json configured correctly

### Testing Both Navigation Modes

```
Test with Magic Remote (Pointer Mode):
1. Move cursor over elements
2. Click to select
3. Verify hover states work
4. Switch to 5-way (press arrow key)
5. Verify no flickering

Test with 5-Way (D-Pad Mode):
1. Press arrow keys to navigate
2. Verify focus ring visible
3. Press Enter to select
4. Open modal, verify it's visible
5. Press Back to close modal
6. Switch to pointer (move magic remote)
7. Verify no flickering
```

---

## Quick Reference: What Works / What Doesn't

### CSS

| Feature | webOS 6.x (Chrome 79) | Alternative |
|---------|----------------------|-------------|
| `display: flex` | ✅ | - |
| `display: grid` | ✅ | - |
| `gap` (flexbox) | ❌ | Use margin |
| `gap` (grid) | ⚠️ Limited | Use margin |
| `backdrop-filter` | ❌ Buggy | Solid overlay |
| `transform` | ✅ | - |
| `transition` | ✅ | - |
| `animation` | ✅ | Use -webkit- prefix |
| `position: fixed` | ✅ | - |
| `position: sticky` | ✅ | - |
| `opacity` | ✅ | - |
| `border-radius` | ✅ | - |
| `box-shadow` | ✅ | - |
| `filter: blur()` | ⚠️ Slow | Avoid on large areas |
| `clip-path` | ⚠️ Limited | Use overflow + border-radius |
| `aspect-ratio` | ❌ | Padding-bottom trick |
| `:is()` selector | ❌ | Individual selectors |
| `clamp()` | ✅ | - |
| `min()`/`max()` | ✅ | - |

### JavaScript

| Feature | webOS 6.x (Chrome 79) | Alternative |
|---------|----------------------|-------------|
| Arrow functions | ✅ | - |
| Classes | ✅ | - |
| Async/await | ✅ | - |
| Promises | ✅ | - |
| Template literals | ✅ | - |
| Destructuring | ✅ | - |
| Spread operator | ✅ | - |
| Map/Set | ✅ | - |
| Optional chaining (`?.`) | ❌ | `obj && obj.prop` |
| Nullish coalescing (`??`) | ❌ | `!= null ? x : y` |
| BigInt | ⚠️ Limited | Avoid |
| Dynamic import | ⚠️ Limited | Static imports |

### Remote Control

| Key | Code | Works |
|-----|------|-------|
| Left | 37 | ✅ |
| Up | 38 | ✅ |
| Right | 39 | ✅ |
| Down | 40 | ✅ |
| Enter/OK | 13 | ✅ |
| Back | 461 | ✅ (need stopPropagation) |
| Escape | 27 | ✅ |
| Color buttons | 403-406 | ✅ |
| Media buttons | Various | ✅ |

---

## Common Errors & Solutions

### "Navigation skips elements (e.g., p2 → p4)"

**Cause:** CSS `gap` not working, elements have no spacing
**Solution:** Use margin instead of gap

### "Modal not visible / flickering"

**Cause:** `backdrop-filter` not supported properly
**Solution:** Remove backdrop-blur, use solid overlay with hardware acceleration

### "Back button shows 'Exit app?' dialog"

**Cause:** Event not properly stopped
**Solution:** Add `event.stopPropagation()` in addition to `preventDefault()`

### "Layout looks wrong on TV but fine in browser"

**Cause:** CSS features not supported in Chromium 79
**Solution:** Check Chrome 79 support for all CSS properties used

### "App crashes or freezes"

**Cause:** Often memory issues or too many hardware-accelerated layers
**Solution:** Reduce use of `will-change`, limit simultaneous animations

---

## Additional Resources

- [webOS TV Developer Portal](https://webostv.developer.lge.com/)
- [webOS TV Developer Tools (CLI)](https://webostv.developer.lge.com/develop/tools/cli-dev-guide)
- [Chromium 79 Release Notes](https://developer.chrome.com/blog/new-in-chrome-79)
- [Can I Use - Browser Compatibility](https://caniuse.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-20 | 1.0 | Initial document created from development learnings |

---

## LLM Prompting Guide

When working on webOS TV projects, use these prompts to ensure compatibility:

### Initial Project Assessment

```
I'm working on a webOS TV app targeting webOS TV 6.x (Chromium 79).
Please review my code for compatibility issues, specifically checking for:
1. CSS gap property usage (not supported)
2. backdrop-filter usage (buggy)
3. Optional chaining (?.) or nullish coalescing (??) (not supported)
4. Any CSS features added after December 2019
```

### Code Review Prompt

```
Review this component for webOS TV 6.x (Chromium 79) compatibility:
- Check for unsupported CSS properties
- Verify hardware acceleration is applied to modals/overlays
- Ensure back button handling includes stopPropagation()
- Check for proper margin-based spacing instead of gap
```

### Debugging Prompt

```
I'm experiencing [issue] on webOS TV 6.x (Chromium 79).
The app works in modern Chrome but fails on the TV.
Common causes to check:
1. CSS gap property (use margin instead)
2. backdrop-filter (use solid overlay)
3. Missing -webkit- prefixes
4. Hardware acceleration issues (add transform: translateZ(0))
5. Back button not using stopPropagation()
```

---

## Code Snippets for Copy-Paste

### Gap Fallback CSS (Tailwind)

```css
/* Add to your global CSS for Chromium 79 compatibility */

/* Horizontal flex gaps */
.flex.gap-1 > * + * { margin-left: 0.25rem; }
.flex.gap-2 > * + * { margin-left: 0.5rem; }
.flex.gap-3 > * + * { margin-left: 0.75rem; }
.flex.gap-4 > * + * { margin-left: 1rem; }
.flex.gap-6 > * + * { margin-left: 1.5rem; }
.flex.gap-8 > * + * { margin-left: 2rem; }

/* Vertical flex gaps */
.flex.flex-col.gap-1 > * + * { margin-left: 0; margin-top: 0.25rem; }
.flex.flex-col.gap-2 > * + * { margin-left: 0; margin-top: 0.5rem; }
.flex.flex-col.gap-3 > * + * { margin-left: 0; margin-top: 0.75rem; }
.flex.flex-col.gap-4 > * + * { margin-left: 0; margin-top: 1rem; }
.flex.flex-col.gap-6 > * + * { margin-left: 0; margin-top: 1.5rem; }
.flex.flex-col.gap-8 > * + * { margin-left: 0; margin-top: 2rem; }
```

### Hardware Acceleration Mixin (CSS)

```css
/* Apply to modals, fixed elements, and animated content */
.hw-accelerate {
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
```

### WebOS-Compatible Modal (React)

```tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const WebOSModal: React.FC<ModalProps> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  const hwAccelerate = {
    transform: 'translateZ(0)',
    WebkitTransform: 'translateZ(0)',
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        ...hwAccelerate,
      }}
    >
      {/* Backdrop - NO backdrop-filter! */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'black',
          opacity: 0.85,
          ...hwAccelerate,
        }}
        onClick={onClose}
      />

      {/* Content */}
      <div
        style={{
          position: 'relative',
          zIndex: 10,
          backgroundColor: '#1a1a1a',
          borderRadius: '12px',
          padding: '24px',
          maxWidth: '90vw',
          ...hwAccelerate,
        }}
      >
        {children}
      </div>
    </div>
  );
};
```

### Keyboard Navigation Provider (React)

```tsx
const KEY_CODES = {
  LEFT: 37, UP: 38, RIGHT: 39, DOWN: 40,
  ENTER: 13, BACK: 461, ESCAPE: 27,
};

const useWebOSKeyboard = (handlers: {
  onBack?: () => boolean | void;
  onArrow?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  onSelect?: () => void;
}) => {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const { keyCode } = e;

      // Arrow keys
      if (keyCode === KEY_CODES.LEFT) handlers.onArrow?.('left');
      if (keyCode === KEY_CODES.RIGHT) handlers.onArrow?.('right');
      if (keyCode === KEY_CODES.UP) handlers.onArrow?.('up');
      if (keyCode === KEY_CODES.DOWN) handlers.onArrow?.('down');

      // Enter/OK
      if (keyCode === KEY_CODES.ENTER) {
        e.preventDefault();
        handlers.onSelect?.();
      }

      // Back button - CRITICAL: must stopPropagation
      if (keyCode === KEY_CODES.BACK || keyCode === KEY_CODES.ESCAPE) {
        e.preventDefault();
        e.stopPropagation(); // Prevents "Exit app?" dialog
        handlers.onBack?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handlers]);
};
```

### Safe Optional Chaining Helper

```typescript
// Since ?. is not supported in Chromium 79, use this helper
function get<T>(obj: any, path: string, defaultValue?: T): T | undefined {
  const keys = path.split('.');
  let result = obj;

  for (const key of keys) {
    if (result == null) return defaultValue;
    result = result[key];
  }

  return result !== undefined ? result : defaultValue;
}

// Usage:
// Instead of: user?.profile?.name
// Use: get(user, 'profile.name')
```

---

## Deployment Commands

### Build for webOS TV

```bash
# Build production bundle
npm run build

# Package for webOS (requires ares-cli)
ares-package dist -o .

# List connected devices
ares-setup-device --list

# Install on TV
ares-install com.example.app_1.0.0_all.ipk -d TV_NAME

# Launch app
ares-launch com.example.app -d TV_NAME

# View logs
ares-inspect com.example.app -d TV_NAME --open
```

### Development Workflow

```bash
# 1. Start dev server
npm run dev

# 2. Test in Chrome with DevTools
#    - Open DevTools (F12)
#    - Toggle device toolbar
#    - Set custom device: 1920x1080

# 3. Build and deploy to TV
npm run build && ares-package dist -o . && ares-install *.ipk -d TV_NAME

# 4. Debug on TV
ares-inspect com.example.app -d TV_NAME --open
```

---

## Troubleshooting Decision Tree

```
Problem: UI looks broken on TV
├── Are elements overlapping/no spacing?
│   └── Check for CSS `gap` usage → Replace with margin
├── Is modal invisible or flickering?
│   └── Check for `backdrop-filter` → Remove, use solid overlay
├── Are animations janky?
│   └── Add hardware acceleration (transform: translateZ(0))
└── Are styles missing?
    └── Check for missing -webkit- prefixes

Problem: Navigation not working
├── Arrow keys don't move focus?
│   └── Check spatial navigation algorithm
│   └── Verify elements have correct positions (check for gap issues)
├── Back button shows "Exit app?" dialog?
│   └── Add event.stopPropagation()
│   └── Ensure disableBackHistoryAPI: true in appinfo.json
└── Enter key not selecting?
    └── Check keyCode (should be 13)
    └── Verify event handler is attached

Problem: App crashes/freezes
├── Memory issues?
│   └── Reduce hardware-accelerated layers
│   └── Optimize images
├── JavaScript errors?
│   └── Check for ?. or ?? usage
│   └── Verify all ES features are transpiled
└── Build configuration wrong?
    └── Ensure targeting Chrome 79
    └── Verify Babel plugins installed
```

---

*This document is intended for use by LLMs assisting with webOS TV development. Update as new learnings are discovered.*
