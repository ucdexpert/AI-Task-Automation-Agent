interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
}

export default function Card({ children, className = '', title }: CardProps) {
  return (
    <div
      className={`bg-card rounded-xl border border-[rgba(255,255,255,0.08)] ${
        title ? 'p-5' : 'p-5'
      } ${className}`}
    >
      {title && (
        <h3 className="text-lg font-semibold text-text-primary mb-4">{title}</h3>
      )}
      {children}
    </div>
  );
}
