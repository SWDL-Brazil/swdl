import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = true }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-navy/5 p-6',
        hover && 'transition-all duration-300 hover:shadow-elevated hover:-translate-y-1',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardImageProps {
  src?: string;
  alt: string;
  className?: string;
  fallback?: React.ReactNode;
}

export function CardImage({ src, alt, className, fallback }: CardImageProps) {
  if (!src) {
    return (
      <div
        className={cn(
          'bg-surface-alt flex items-center justify-center text-4xl',
          className
        )}
      >
        {fallback || '📰'}
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={cn('object-cover', className)}
      loading="lazy"
    />
  );
}
