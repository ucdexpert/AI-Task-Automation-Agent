export default function LoadingSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-label="Loading content">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 bg-[rgba(255,255,255,0.05)] rounded w-3/4"></div>
          <div className="h-3 bg-[rgba(255,255,255,0.05)] rounded w-1/2"></div>
          <div className="h-3 bg-[rgba(255,255,255,0.05)] rounded w-2/3"></div>
        </div>
      ))}
      <span className="sr-only">Loading...</span>
    </div>
  );
}
