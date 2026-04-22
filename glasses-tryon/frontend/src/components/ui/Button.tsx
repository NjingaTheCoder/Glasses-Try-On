import { type ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/cn'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-semibold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed tracking-wide',
          {
            // Gold primary — the main CTA
            'bg-gold-400 text-white hover:bg-gold-500 focus:ring-gold-400 shadow-sm hover:shadow-gold active:scale-[0.98]':
              variant === 'primary',
            // Navy outline secondary
            'bg-white text-brand-800 border border-brand-200 hover:bg-brand-50 hover:border-brand-300 focus:ring-brand-400 shadow-sm':
              variant === 'secondary',
            // Ghost
            'text-brand-600 hover:text-brand-900 hover:bg-brand-50 focus:ring-brand-400':
              variant === 'ghost',
            // Navy filled outline
            'border border-brand-900 text-brand-900 hover:bg-brand-900 hover:text-white focus:ring-brand-500 transition-colors':
              variant === 'outline',
            // Danger
            'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm':
              variant === 'danger',
            'px-3 py-1.5 text-xs': size === 'sm',
            'px-5 py-2.5 text-sm': size === 'md',
            'px-7 py-3.5 text-base': size === 'lg',
          },
          className,
        )}
        {...props}
      />
    )
  },
)
Button.displayName = 'Button'
