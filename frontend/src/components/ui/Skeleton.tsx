import React from 'react';

/** Placeholder blocks shown while a page loads, shaped like the content that will replace them. */
export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`skeleton ${className}`} aria-hidden="true" />
);

export const PageSkeleton: React.FC<{ variant?: 'cards' | 'list' | 'article'; label?: string }> = ({
  variant = 'list',
  label = 'Loading',
}) => (
  <div className="w-full pt-24 pb-16 min-h-screen" role="status" aria-label={label}>
    <div className={`mx-auto px-4 sm:px-6 lg:px-8 ${variant === 'article' ? 'max-w-4xl' : 'max-w-7xl'}`}>
      <Skeleton className="h-3 w-40 mb-3" />
      <Skeleton className="h-8 w-72 max-w-full mb-6" />
      {variant === 'cards' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-2xl" />
          ))}
        </div>
      )}
      {variant === 'list' && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-2xl" />
            ))}
          </div>
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-2xl" />
            ))}
          </div>
        </>
      )}
      {variant === 'article' && (
        <div className="space-y-4">
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-40 rounded-2xl" />
          <Skeleton className="h-40 rounded-2xl" />
        </div>
      )}
      <span className="sr-only">{label}…</span>
    </div>
  </div>
);
