import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'navy' | 'ghost' | 'ghost-white';
  children: React.ReactNode;
}

export function Button({ variant = 'primary', className, children, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        'btn',
        variant === 'primary' && 'btn-primary',
        variant === 'navy' && 'btn-navy',
        variant === 'ghost' && 'btn-ghost',
        variant === 'ghost-white' && 'btn-ghost-white',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

interface LinkButtonProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  variant?: 'primary' | 'navy' | 'ghost' | 'ghost-white';
  children: React.ReactNode;
}

export function LinkButton({ variant = 'primary', className, children, ...props }: LinkButtonProps) {
  return (
    <a
      className={cn(
        'btn',
        variant === 'primary' && 'btn-primary',
        variant === 'navy' && 'btn-navy',
        variant === 'ghost' && 'btn-ghost',
        variant === 'ghost-white' && 'btn-ghost-white',
        className
      )}
      {...props}
    >
      {children}
    </a>
  );
}
