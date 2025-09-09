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
  return <h2 className="text-xl font-bold">{children}</h2>;
};

export const BoldH3 = ({ children }: { children: React.ReactNode }) => {
  return <h3 className="text-lg font-bold">{children}</h3>;
};
