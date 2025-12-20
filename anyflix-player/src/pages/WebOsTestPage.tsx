import { useState, useCallback } from "react";
import { FocusProvider, useFocusContext } from "../contexts/FocusContext";
import { KeyboardNavigationProvider } from "../providers/KeyboardNavigationProvider";
import { FocusZone } from "../components/navigation/FocusZone";
import { FocusableItem } from "../components/navigation/FocusableItem";
import { cn } from "../lib/utils";

// Demo card data
const POPULAR_SHOWS = [
  { id: "p1", title: "Attack on Titan", color: "bg-red-600" },
  { id: "p2", title: "Demon Slayer", color: "bg-orange-600" },
  { id: "p3", title: "My Hero Academia", color: "bg-blue-600" },
  { id: "p4", title: "One Piece", color: "bg-yellow-600" },
  { id: "p5", title: "Jujutsu Kaisen", color: "bg-purple-600" },
  { id: "p6", title: "Chainsaw Man", color: "bg-pink-600" },
  { id: "p7", title: "Spy x Family", color: "bg-green-600" },
];

const LATEST_UPDATES = [
  { id: "l1", title: "Frieren", color: "bg-teal-600" },
  { id: "l2", title: "Solo Leveling", color: "bg-indigo-600" },
  { id: "l3", title: "Oshi no Ko", color: "bg-rose-600" },
  { id: "l4", title: "Mashle", color: "bg-amber-600" },
  { id: "l5", title: "Blue Lock", color: "bg-cyan-600" },
];

// Demo card component
interface DemoCardProps {
  id: string;
  title: string;
  color: string;
  onSelect?: () => void;
}

const DemoCard = ({ id, title, color, onSelect }: DemoCardProps) => {
  return (
    <FocusableItem
      id={id}
      onSelect={onSelect}
      className={cn(
        "flex-shrink-0 w-48 h-32 rounded-lg flex items-center justify-center cursor-pointer",
        color
      )}
    >
      <span className="text-white font-semibold text-center px-2">{title}</span>
    </FocusableItem>
  );
};

// Demo button component
interface DemoButtonProps {
  id: string;
  label: string;
  onSelect?: () => void;
  variant?: "primary" | "secondary";
}

const DemoButton = ({ id, label, onSelect, variant = "secondary" }: DemoButtonProps) => {
  return (
    <FocusableItem
      id={id}
      onSelect={onSelect}
      className={cn(
        "px-6 py-3 rounded-lg font-semibold cursor-pointer text-center min-w-[120px]",
        variant === "primary"
          ? "bg-primary text-white hover:bg-primary/90"
          : "bg-gray-700 text-white hover:bg-gray-600"
      )}
    >
      {label}
    </FocusableItem>
  );
};

// Modal component with focus trapping
interface DemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const DemoModal = ({ isOpen, onClose }: DemoModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal content */}
      <FocusZone
        id="modal-zone"
        type="modal"
        isModal
        trapFocus
        className="relative z-10 bg-gray-900 rounded-xl p-6 w-[500px] max-w-[90vw] border border-gray-700"
      >
        <h2 className="text-2xl font-bold text-white mb-4">Modal Dialog</h2>

        <p className="text-gray-300 mb-6">
          Focus is trapped within this modal. Use arrow keys to navigate between
          buttons. Press <kbd className="px-2 py-1 bg-gray-700 rounded">Back</kbd> or{" "}
          <kbd className="px-2 py-1 bg-gray-700 rounded">Escape</kbd> to close.
        </p>

        <div className="flex gap-4 justify-end">
          <DemoButton
            id="modal-cancel"
            label="Cancel"
            onSelect={onClose}
          />
          <DemoButton
            id="modal-confirm"
            label="Confirm"
            variant="primary"
            onSelect={() => {
              alert("Confirmed!");
              onClose();
            }}
          />
        </div>
      </FocusZone>
    </div>
  );
};

// Navigation info display
const NavigationInfo = () => {
  const { navigationMode, focusedElementId, activeZoneId } = useFocusContext();

  return (
    <div className="fixed top-4 right-4 bg-gray-900/90 backdrop-blur-sm rounded-lg p-4 text-sm text-gray-300 z-40 border border-gray-700">
      <h3 className="font-semibold text-white mb-2">Navigation Debug</h3>
      <div className="space-y-1">
        <p>
          Mode:{" "}
          <span className={cn(
            "font-mono px-2 py-0.5 rounded",
            navigationMode === "5way" ? "bg-green-600 text-white" : "bg-blue-600 text-white"
          )}>
            {navigationMode}
          </span>
        </p>
        <p>
          Zone: <span className="font-mono text-yellow-400">{activeZoneId || "none"}</span>
        </p>
        <p>
          Focused: <span className="font-mono text-cyan-400">{focusedElementId || "none"}</span>
        </p>
      </div>
    </div>
  );
};

// Main test page content
const WebOsTestPageContent = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [lastAction, setLastAction] = useState<string>("");

  const handleCardSelect = useCallback((title: string) => {
    setLastAction(`Selected: ${title}`);
  }, []);

  const handleBack = useCallback(() => {
    if (isModalOpen) {
      setIsModalOpen(false);
      return true;
    }
    setLastAction("Back button pressed");
    return false;
  }, [isModalOpen]);

  return (
    <KeyboardNavigationProvider onBack={handleBack}>
      <div className="min-h-screen bg-background text-white p-8 overflow-hidden">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">
            WebOS Navigation Test
          </h1>
          <p className="text-gray-400">
            Use arrow keys to navigate, Enter to select, Back/Escape to go back
          </p>
          {lastAction && (
            <p className="mt-2 text-green-400 font-mono">{lastAction}</p>
          )}
        </div>

        {/* Navigation info */}
        <NavigationInfo />

        {/* Row 1: Popular Shows */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Popular Shows (Row 1)
          </h2>
          <FocusZone
            id="popular-row"
            type="row"
            priority={0}
            rememberFocus
            navigationAxis="horizontal"
            className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide"
          >
            {POPULAR_SHOWS.map((show, index) => (
              <DemoCard
                key={show.id}
                id={show.id}
                title={show.title}
                color={show.color}
                onSelect={() => handleCardSelect(show.title)}
              />
            ))}
          </FocusZone>
        </section>

        {/* Row 2: Latest Updates */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Latest Updates (Row 2)
          </h2>
          <FocusZone
            id="latest-row"
            type="row"
            priority={1}
            rememberFocus
            navigationAxis="horizontal"
            className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide"
          >
            {LATEST_UPDATES.map((show) => (
              <DemoCard
                key={show.id}
                id={show.id}
                title={show.title}
                color={show.color}
                onSelect={() => handleCardSelect(show.title)}
              />
            ))}
          </FocusZone>
        </section>

        {/* Row 3: Action Buttons */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Action Buttons (Row 3)
          </h2>
          <FocusZone
            id="button-row"
            type="row"
            priority={2}
            rememberFocus
            navigationAxis="horizontal"
            className="flex gap-4"
          >
            <DemoButton
              id="btn-modal"
              label="Open Modal"
              variant="primary"
              onSelect={() => setIsModalOpen(true)}
            />
            <DemoButton
              id="btn-settings"
              label="Settings"
              onSelect={() => setLastAction("Settings clicked")}
            />
            <DemoButton
              id="btn-about"
              label="About"
              onSelect={() => setLastAction("About clicked")}
            />
          </FocusZone>
        </section>

        {/* Instructions */}
        <section className="mt-12 p-6 bg-gray-900 rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">
            Navigation Instructions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
            <div>
              <h3 className="font-semibold text-white mb-2">Arrow Keys</h3>
              <ul className="space-y-1 text-sm">
                <li>
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">←</kbd>{" "}
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">→</kbd> Move
                  within row
                </li>
                <li>
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">↑</kbd>{" "}
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">↓</kbd> Move
                  between rows
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-2">Action Keys</h3>
              <ul className="space-y-1 text-sm">
                <li>
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">Enter</kbd> /
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">OK</kbd>{" "}
                  Select item
                </li>
                <li>
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">Back</kbd> /
                  <kbd className="px-2 py-0.5 bg-gray-700 rounded">Escape</kbd>{" "}
                  Close modal / Go back
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-400">
            <p>
              <strong>Focus Memory:</strong> Each row remembers the last focused
              card. When you navigate back to a row, it will return to the
              previously focused item.
            </p>
            <p className="mt-2">
              <strong>Smart Positioning:</strong> When moving between rows,
              focus moves to the nearest card based on horizontal position.
            </p>
          </div>
        </section>

        {/* Modal */}
        <DemoModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </div>
    </KeyboardNavigationProvider>
  );
};

// Main component with FocusProvider wrapper
const WebOsTestPage = () => {
  return (
    <FocusProvider>
      <WebOsTestPageContent />
    </FocusProvider>
  );
};

export default WebOsTestPage;
