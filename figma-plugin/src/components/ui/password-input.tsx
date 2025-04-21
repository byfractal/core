import * as React from "react";
import { cn } from "@/lib/utils";
import { EyeIcon, EyeOffIcon } from "lucide-react";

export interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, error, label, ...props }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);

    return (
      <div className="relative w-full flex flex-col gap-2">
        {label && (
          <label className="text-sm font-medium text-[#0F172A]">
            {label}
          </label>
        )}
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            className={cn(
              "flex h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#0F172A]",
              "ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium",
              "placeholder:text-[#848484] focus-visible:outline-none focus-visible:ring-2",
              "focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
              "shadow-[0px_1px_5px_0px_rgba(0,0,0,0.07)] pr-10",
              error ? "border-red-500 focus-visible:ring-red-500" : "focus-visible:ring-primary",
              className
            )}
            ref={ref}
            {...props}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-2.5 text-[#848484] hover:text-[#0F172A] focus:outline-none"
          >
            {showPassword ? (
              <EyeOffIcon className="h-5 w-5 stroke-[1.5px]" />
            ) : (
              <EyeIcon className="h-5 w-5 stroke-[1.5px]" />
            )}
          </button>
        </div>
        {error && (
          <p className="mt-1 text-xs text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

PasswordInput.displayName = "PasswordInput";

export { PasswordInput }; 