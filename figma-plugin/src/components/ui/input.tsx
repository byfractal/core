import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, label, ...props }, ref) => {
    return (
      <div className="relative w-full flex flex-col gap-2">
        {label && (
          <label className="text-sm font-medium text-[#0F172A]">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#0F172A]",
            "ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-[#848484] focus-visible:outline-none focus-visible:ring-2",
            "focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            "shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)]",
            error ? "border-red-500 focus-visible:ring-red-500" : "focus-visible:ring-primary",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="mt-1 text-xs text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export { Input }; 