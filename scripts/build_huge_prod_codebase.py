import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_f(rel_path, content):
    p = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Generated {rel_path} ({len(content.splitlines())} lines)")

def generate_frontend_ui():
    ui_components = {
        "Button.tsx": """
import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  className,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-xl transition focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/30 focus:ring-indigo-500',
    secondary: 'bg-slate-800 hover:bg-slate-700 text-white shadow focus:ring-slate-700',
    outline: 'border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 focus:ring-indigo-500',
    ghost: 'hover:bg-slate-100 text-slate-700 focus:ring-slate-400',
    danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-600/30 focus:ring-rose-500',
    success: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md shadow-emerald-600/30 focus:ring-emerald-500'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-xs',
    lg: 'px-6 py-3 text-sm',
    icon: 'p-2'
  };

  return (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
      {...props}
    >
      {isLoading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
      ) : leftIcon ? (
        <span className="mr-2">{leftIcon}</span>
      ) : null}
      {children}
      {!isLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
});

Button.displayName = 'Button';
""",
        "Input.tsx": """
import React, { InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftElement?: React.ReactNode;
  rightElement?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  className,
  label,
  error,
  helperText,
  leftElement,
  rightElement,
  id,
  ...props
}, ref) => {
  const inputId = id || props.name;

  return (
    <div className="w-full space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-[11px] font-semibold text-slate-700">
          {label}
        </label>
      )}
      <div className="relative rounded-xl shadow-sm">
        {leftElement && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            {leftElement}
          </div>
        )}
        <input
          ref={ref}
          id={inputId}
          className={twMerge(clsx(
            'block w-full text-xs rounded-xl border border-slate-200 bg-slate-50 p-2.5 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white',
            leftElement && 'pl-9',
            rightElement && 'pr-9',
            error && 'border-rose-300 focus:ring-rose-500 text-rose-900 bg-rose-50/20',
            className
          ))}
          {...props}
        />
        {rightElement && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400">
            {rightElement}
          </div>
        )}
      </div>
      {error ? (
        <p className="text-[10px] text-rose-600 font-medium">{error}</p>
      ) : helperText ? (
        <p className="text-[10px] text-slate-500">{helperText}</p>
      ) : null}
    </div>
  );
});

Input.displayName = 'Input';
""",
        "Badge.tsx": """
import React, { HTMLAttributes } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'default',
  size = 'md',
  dot = false,
  children,
  ...props
}) => {
  const variants = {
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    primary: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    secondary: 'bg-slate-800 text-white border-slate-700',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-sky-50 text-sky-700 border-sky-200'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[9px]',
    md: 'px-2.5 py-1 text-[10px]',
    lg: 'px-3 py-1.5 text-xs'
  };

  return (
    <span
      className={twMerge(clsx(
        'inline-flex items-center gap-1.5 font-bold uppercase tracking-wider rounded-full border',
        variants[variant],
        sizes[size],
        className
      ))}
      {...props}
    >
      {dot && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
      {children}
    </span>
  );
};
""",
        "Card.tsx": """
import React, { HTMLAttributes } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  className,
  header,
  footer,
  children,
  ...props
}) => {
  return (
    <div
      className={twMerge(clsx(
        'bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col justify-between',
        className
      ))}
      {...props}
    >
      {header && (
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
          {header}
        </div>
      )}
      <div className="p-5 flex-1">
        {children}
      </div>
      {footer && (
        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50">
          {footer}
        </div>
      )}
    </div>
  );
};
""",
        "Modal.tsx": """
import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  maxWidth = 'md'
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidths = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" onClick={onClose} />
      <div className={`relative bg-white rounded-2xl w-full ${maxWidths[maxWidth]} shadow-2xl overflow-hidden z-10 animate-in fade-in zoom-in-95`}>
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900">{title}</h3>
          <button onClick={onClose} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
};
""",
        "Table.tsx": """
import React, { TableHTMLAttributes } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export const Table: React.FC<TableHTMLAttributes<HTMLTableElement>> = ({ className, children, ...props }) => (
  <div className="w-full overflow-x-auto">
    <table className={twMerge(clsx('w-full text-left text-xs', className))} {...props}>
      {children}
    </table>
  </div>
);

export const TableHeader: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className, children, ...props }) => (
  <thead className={twMerge(clsx('bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[10px] tracking-wider', className))} {...props}>
    {children}
  </thead>
);

export const TableBody: React.FC<React.HTMLAttributes<HTMLTableSectionElement>> = ({ className, children, ...props }) => (
  <tbody className={twMerge(clsx('divide-y divide-slate-100 font-medium text-slate-700', className))} {...props}>
    {children}
  </tbody>
);

export const TableRow: React.FC<React.HTMLAttributes<HTMLTableRowElement>> = ({ className, children, ...props }) => (
  <tr className={twMerge(clsx('hover:bg-slate-50/80 transition', className))} {...props}>
    {children}
  </tr>
);

export const TableHead: React.FC<React.ThHTMLAttributes<HTMLTableCellElement>> = ({ className, children, ...props }) => (
  <th className={twMerge(clsx('px-6 py-3', className))} {...props}>
    {children}
  </th>
);

export const TableCell: React.FC<React.TdHTMLAttributes<HTMLTableCellElement>> = ({ className, children, ...props }) => (
  <td className={twMerge(clsx('px-6 py-4', className))} {...props}>
    {children}
  </td>
);
""",
        "Tabs.tsx": """
import React, { useState } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  content: React.ReactNode;
  badge?: string | number;
}

export interface TabsProps {
  items: TabItem[];
  defaultTabId?: string;
  onChange?: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({ items, defaultTabId, onChange, className }) => {
  const [activeTab, setActiveTab] = useState(defaultTabId || items[0]?.id);

  const handleSelect = (id: string) => {
    setActiveTab(id);
    if (onChange) onChange(id);
  };

  const currentItem = items.find((i) => i.id === activeTab);

  return (
    <div className={twMerge(clsx('space-y-4', className))}>
      <div className="flex items-center gap-2 border-b border-slate-200">
        {items.map((tab) => {
          const isActive = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              onClick={() => handleSelect(tab.id)}
              className={clsx(
                'flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition -mb-px',
                isActive
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-500 hover:text-slate-900 hover:border-slate-300'
              )}
            >
              {tab.icon}
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold">
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
      <div>
        {currentItem?.content}
      </div>
    </div>
  );
};
""",
        "Alert.tsx": """
import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface AlertProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  children: React.ReactNode;
  onDismiss?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  onDismiss,
  className
}) => {
  const icons = {
    info: <Info className="h-4 w-4 text-sky-600 shrink-0" />,
    success: <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />,
    warning: <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />,
    error: <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
  };

  const styles = {
    info: 'bg-sky-50 border-sky-200 text-sky-900',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    error: 'bg-rose-50 border-rose-200 text-rose-900'
  };

  return (
    <div className={twMerge(clsx('p-4 rounded-2xl border flex items-start gap-3 text-xs', styles[type], className))}>
      {icons[type]}
      <div className="flex-1 space-y-0.5">
        {title && <h5 className="font-bold">{title}</h5>}
        <div className="opacity-90">{children}</div>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="p-1 hover:opacity-75">
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
};
""",
        "Switch.tsx": """
import React from 'react';
import { clsx } from 'clsx';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  description?: string;
  disabled?: boolean;
}

export const Switch: React.FC<SwitchProps> = ({ checked, onChange, label, description, disabled = false }) => {
  return (
    <label className={clsx('flex items-center justify-between gap-3 cursor-pointer select-none', disabled && 'opacity-50 cursor-not-allowed')}>
      {(label || description) && (
        <div>
          {label && <p className="text-xs font-semibold text-slate-900">{label}</p>}
          {description && <p className="text-[11px] text-slate-500">{description}</p>}
        </div>
      )}
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={clsx(
          'relative inline-flex h-5 w-9 shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600',
          checked ? 'bg-indigo-600' : 'bg-slate-200'
        )}
      >
        <span
          className={clsx(
            'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
            checked ? 'translate-x-4' : 'translate-x-0'
          )}
        />
      </button>
    </label>
  );
};
""",
        "Progress.tsx": """
import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface ProgressProps {
  value: number;
  max?: number;
  label?: string;
  showPercent?: boolean;
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  className?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  label,
  showPercent = true,
  variant = 'primary',
  className
}) => {
  const percent = Math.min(100, Math.max(0, (value / max) * 100));

  const variants = {
    primary: 'bg-indigo-600',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500'
  };

  return (
    <div className={twMerge(clsx('space-y-1.5', className))}>
      {(label || showPercent) && (
        <div className="flex items-center justify-between text-xs font-semibold">
          {label && <span className="text-slate-600">{label}</span>}
          {showPercent && <span className="font-mono text-slate-900">{Math.round(percent)}%</span>}
        </div>
      )}
      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-300', variants[variant])}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
};
""",
        "Avatar.tsx": """
import React from 'react';
import { clsx } from 'clsx';

export interface AvatarProps {
  name: string;
  src?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  status?: 'online' | 'busy' | 'offline' | 'away';
}

export const Avatar: React.FC<AvatarProps> = ({ name, src, size = 'md', status }) => {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const sizes = {
    sm: 'w-7 h-7 text-[10px]',
    md: 'w-9 h-9 text-xs',
    lg: 'w-12 h-12 text-sm',
    xl: 'w-16 h-16 text-base'
  };

  const statusColors = {
    online: 'bg-emerald-500 ring-white ring-2',
    busy: 'bg-rose-500 ring-white ring-2',
    away: 'bg-amber-500 ring-white ring-2',
    offline: 'bg-slate-400 ring-white ring-2'
  };

  return (
    <div className="relative inline-block">
      <div className={clsx('rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white font-bold flex items-center justify-center shadow overflow-hidden', sizes[size])}>
        {src ? <img src={src} alt={name} className="w-full h-full object-cover" /> : initials}
      </div>
      {status && (
        <span className={clsx('absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full', statusColors[status])} />
      )}
    </div>
  );
};
"""
    }

    for name, content in ui_components.items():
        write_f(f"frontend/src/components/ui/{name}", content)

    print("UI Components generated.")

generate_frontend_ui()
