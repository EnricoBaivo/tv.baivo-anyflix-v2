/**
 * Spatial Navigation Engine
 *
 * Provides algorithms for finding the nearest focusable element
 * based on spatial position and navigation direction.
 *
 * Used for webOS TV 5-way remote control navigation.
 */

import type { Direction } from "../contexts/FocusContext";

// Bounding box with center point
interface Rect {
  left: number;
  right: number;
  top: number;
  bottom: number;
  centerX: number;
  centerY: number;
  width: number;
  height: number;
}

/**
 * Get the bounding rectangle of an element with center point
 */
function getRect(element: HTMLElement): Rect {
  const rect = element.getBoundingClientRect();
  return {
    left: rect.left,
    right: rect.right,
    top: rect.top,
    bottom: rect.bottom,
    centerX: rect.left + rect.width / 2,
    centerY: rect.top + rect.height / 2,
    width: rect.width,
    height: rect.height,
  };
}

/**
 * Check if element B is in the given direction from element A
 */
function isInDirection(from: Rect, to: Rect, direction: Direction): boolean {
  switch (direction) {
    case "left":
      return to.centerX < from.centerX;
    case "right":
      return to.centerX > from.centerX;
    case "up":
      return to.centerY < from.centerY;
    case "down":
      return to.centerY > from.centerY;
    default:
      return false;
  }
}

/**
 * Calculate the distance between two points
 */
function distance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
}

/**
 * Calculate the perpendicular distance for navigation scoring
 *
 * For horizontal navigation (left/right): perpendicular distance is vertical difference
 * For vertical navigation (up/down): perpendicular distance is horizontal difference
 */
function perpendicularDistance(
  from: Rect,
  to: Rect,
  direction: Direction
): number {
  switch (direction) {
    case "left":
    case "right":
      // For horizontal navigation, perpendicular is vertical distance
      return Math.abs(to.centerY - from.centerY);
    case "up":
    case "down":
      // For vertical navigation, perpendicular is horizontal distance
      return Math.abs(to.centerX - from.centerX);
    default:
      return Infinity;
  }
}

/**
 * Calculate the primary axis distance (in direction of navigation)
 */
function primaryDistance(from: Rect, to: Rect, direction: Direction): number {
  switch (direction) {
    case "left":
      return from.left - to.right;
    case "right":
      return to.left - from.right;
    case "up":
      return from.top - to.bottom;
    case "down":
      return to.top - from.bottom;
    default:
      return Infinity;
  }
}

/**
 * Check if navigation in this direction is allowed by the axis constraint
 */
function isDirectionAllowed(
  direction: Direction,
  axis: "horizontal" | "vertical" | "both"
): boolean {
  if (axis === "both") return true;
  if (axis === "horizontal" && (direction === "left" || direction === "right"))
    return true;
  if (axis === "vertical" && (direction === "up" || direction === "down"))
    return true;
  return false;
}

/**
 * Score a candidate element for navigation
 *
 * Lower score = better candidate
 *
 * The algorithm prioritizes:
 * 1. Elements that are directly in line (low perpendicular distance)
 * 2. Elements that are close (low primary distance)
 * 3. Overall proximity
 */
function scoreCandidate(
  from: Rect,
  to: Rect,
  direction: Direction
): number {
  const perpDist = perpendicularDistance(from, to, direction);
  const primDist = primaryDistance(from, to, direction);

  // If element is not in the correct direction (negative primary distance), return Infinity
  if (primDist < 0) {
    return Infinity;
  }

  // Weight perpendicular distance more heavily to prefer aligned elements
  // This creates "lanes" for navigation
  const perpWeight = 2.0;
  const primWeight = 1.0;

  return perpDist * perpWeight + primDist * primWeight;
}

/**
 * Find the next focusable element in a given direction
 *
 * @param current - The currently focused element
 * @param direction - The direction to navigate
 * @param candidates - Array of potential target elements
 * @param axis - Navigation axis constraint ("horizontal", "vertical", or "both")
 * @returns The next element to focus, or null if none found
 */
export function findNextFocusable(
  current: HTMLElement,
  direction: Direction,
  candidates: HTMLElement[],
  axis: "horizontal" | "vertical" | "both" = "both"
): HTMLElement | null {
  // Check if direction is allowed by axis constraint
  if (!isDirectionAllowed(direction, axis)) {
    return null;
  }

  const currentRect = getRect(current);
  let bestCandidate: HTMLElement | null = null;
  let bestScore = Infinity;

  for (const candidate of candidates) {
    // Skip the current element
    if (candidate === current) continue;

    // Skip hidden or disabled elements
    if (!isElementFocusable(candidate)) continue;

    const candidateRect = getRect(candidate);

    // Skip if not in the correct direction
    if (!isInDirection(currentRect, candidateRect, direction)) continue;

    const score = scoreCandidate(currentRect, candidateRect, direction);

    if (score < bestScore) {
      bestScore = score;
      bestCandidate = candidate;
    }
  }

  return bestCandidate;
}

/**
 * Find the nearest element in a zone from a given source element
 *
 * Used when navigating between zones (e.g., moving from one row to another)
 * Uses horizontal distance (for vertical zone transitions) to find the
 * element most aligned with the source.
 *
 * @param from - The source element
 * @param candidates - Array of elements in the target zone
 * @returns The nearest element, or null if none found
 */
export function findNearestInZone(
  from: HTMLElement,
  candidates: HTMLElement[]
): HTMLElement | null {
  if (candidates.length === 0) return null;

  const fromRect = getRect(from);
  let nearest: HTMLElement | null = null;
  let nearestDist = Infinity;

  for (const candidate of candidates) {
    if (!isElementFocusable(candidate)) continue;

    const candidateRect = getRect(candidate);

    // Calculate horizontal distance (for smart positioning when moving between rows)
    const horizDist = Math.abs(candidateRect.centerX - fromRect.centerX);

    if (horizDist < nearestDist) {
      nearestDist = horizDist;
      nearest = candidate;
    }
  }

  return nearest;
}

/**
 * Find the first focusable element in a list
 */
export function findFirstFocusable(
  candidates: HTMLElement[]
): HTMLElement | null {
  for (const candidate of candidates) {
    if (isElementFocusable(candidate)) {
      return candidate;
    }
  }
  return null;
}

/**
 * Find the last focusable element in a list
 */
export function findLastFocusable(
  candidates: HTMLElement[]
): HTMLElement | null {
  for (let i = candidates.length - 1; i >= 0; i--) {
    if (isElementFocusable(candidates[i])) {
      return candidates[i];
    }
  }
  return null;
}

/**
 * Check if an element is focusable
 */
export function isElementFocusable(element: HTMLElement): boolean {
  // Check if element exists and is visible
  if (!element || !element.offsetParent) return false;

  // Check for disabled attribute
  if (element.hasAttribute("disabled")) return false;

  // Check for tabindex -1
  const tabIndex = element.getAttribute("tabindex");
  if (tabIndex === "-1") return false;

  // Check for aria-disabled
  if (element.getAttribute("aria-disabled") === "true") return false;

  // Check for data-webos-focusable false
  if (element.getAttribute("data-webos-focusable") === "false") return false;

  return true;
}

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selector = [
    '[tabindex]:not([tabindex="-1"])',
    "[data-webos-focusable]:not([data-webos-focusable='false'])",
    'button:not([disabled])',
    'a[href]',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
  ].join(", ");

  const elements = container.querySelectorAll<HTMLElement>(selector);
  return Array.from(elements).filter(isElementFocusable);
}

/**
 * Calculate the visual order of elements (left-to-right, top-to-bottom)
 */
export function sortByVisualOrder(elements: HTMLElement[]): HTMLElement[] {
  return [...elements].sort((a, b) => {
    const rectA = getRect(a);
    const rectB = getRect(b);

    // First sort by row (top position)
    const rowDiff = rectA.top - rectB.top;
    if (Math.abs(rowDiff) > 10) {
      return rowDiff;
    }

    // Then sort by column (left position)
    return rectA.left - rectB.left;
  });
}

// Export types
export type { Rect };
