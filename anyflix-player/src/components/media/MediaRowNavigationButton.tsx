import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { getFocusClasses, getWebOSProps } from "@/lib/webos-focus";
import { useWebOSFocus } from "@/hooks/useWebOSFocus";

interface MediaRowNavigationButtonProps {
  direction: "left" | "right";
  onClick: () => void;
  ariaLabel: string;
  title: string;
}

const MediaRowNavigationButton = ({ direction, onClick, ariaLabel, title }: MediaRowNavigationButtonProps) => {
  const { focusProps, navigationMode } = useWebOSFocus({
    onEnter: onClick,
  });

  const isLeft = direction === "left";
  const Icon = isLeft ? ChevronLeft : ChevronRight;

  return (
    <button
      {...focusProps}
      {...getWebOSProps()}
      onClick={onClick}
      className={cn(
        "absolute top-1/2 -translate-y-1/2 z-10 bg-black/50 text-white p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 hover:bg-black/70 focus:opacity-100",
        isLeft ? "left-0 rounded-r-md" : "right-0 rounded-l-md",
        getFocusClasses("button", navigationMode)
      )}
      aria-label={ariaLabel}
      title={title}
    >
      <Icon className="h-6 w-6" />
    </button>
  );
};

export default MediaRowNavigationButton;
