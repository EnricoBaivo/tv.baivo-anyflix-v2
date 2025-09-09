import { cn } from "@/lib/utils";

export const BoldH1 = ({
  children,
  ...props
}: {
  children: React.ReactNode;
  props?: React.HTMLAttributes<HTMLHeadingElement>;
}) => {
  return (
    <h1
      className="text-4xl md:text-6xl lg:text-7xl font-black text-white mb-6 leading-none uppercase tracking-tight"
      {...props}
    >
      {children}
    </h1>
  );
};

export const BoldH2 = ({ children }: { children: React.ReactNode }) => {
  return (
    <h2 className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight tracking-wide">
      {children}
    </h2>
  );
};

export const BoldH3 = ({ children }: { children: React.ReactNode }) => {
  return (
    <h3 className="text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold text-white mb-4 leading-tight tracking-wide">
      {children}
    </h3>
  );
};

// Netflix-style movie title in cards
export const MediaTitle = ({ children }: { children: React.ReactNode }) => {
  return (
    <h3 className="text-anyflix-red  text-xl md:text-2xl lg:text-3xl xl:text-4xl font-bold text-white mb-2 leading-tight">
      {children}
    </h3>
  );
};

// Netflix-style section title
export const SectionTitle = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <h2
      className={cn(
        "text-lg md:text-xl lg:text-2xl xl:text-3xl font-semibold text-white mb-4 leading-tight",
        className
      )}
    >
      {children}
    </h2>
  );
};

// Netflix-style metadata text
export const MetadataText = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="text-sm md:text-base lg:text-lg text-gray-300 leading-relaxed">
      {children}
    </div>
  );
};

// Netflix-style description text
export const DescriptionText = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  return (
    <p className="text-sm md:text-base lg:text-lg xl:text-xl text-white leading-relaxed">
      {children}
    </p>
  );
};
