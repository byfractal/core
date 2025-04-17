import React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { SemanticTagType } from "@/types";

// Define the tag variants using CVA
const tagVariants = cva(
  "inline-flex items-center justify-center rounded-md text-xs font-medium ring-offset-background transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 px-2 py-1",
  {
    variants: {
      variant: {
        default: "bg-primary/10 text-primary",
        layout: "bg-blue-100 text-blue-800",
        friction: "bg-red-100 text-red-800",
        navigation: "bg-purple-100 text-purple-800",
        conversion: "bg-green-100 text-green-800",
        performance: "bg-orange-100 text-orange-800",
        accessibility: "bg-yellow-100 text-yellow-800",
        mobile: "bg-indigo-100 text-indigo-800",
        desktop: "bg-gray-100 text-gray-800",
        ux: "bg-pink-100 text-pink-800",
        ui: "bg-teal-100 text-teal-800",
        branding: "bg-amber-100 text-amber-800",
        error: "bg-red-100 text-red-800",
        warning: "bg-amber-100 text-amber-800",
        success: "bg-green-100 text-green-800",
        info: "bg-blue-100 text-blue-800",
      },
      size: {
        default: "h-6 text-xs",
        sm: "h-5 text-xs",
        lg: "h-7 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

// Map tag types to variants
const tagTypeToVariant = {
  Layout: "layout",
  Friction: "friction",
  Navigation: "navigation",
  Conversion: "conversion",
  Performance: "performance",
  Accessibility: "accessibility",
  Mobile: "mobile",
  Desktop: "desktop",
  performance: "performance",
  accessibility: "accessibility",
  ux: "ux",
  ui: "ui",
  branding: "branding",
  error: "error",
  warning: "warning",
  success: "success",
  info: "info",
} as const;

// Component props
export interface SemanticTagProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof tagVariants> {
  type: SemanticTagType;
}

/**
 * SemanticTag Component
 *
 * Small semantic tag representing optimization category (e.g. Layout, Friction).
 * Used to group issues by type. Appears in both InsightCard and ProjectOverviewPage.
 */
const SemanticTag = React.forwardRef<HTMLDivElement, SemanticTagProps>(
  ({ className, type, size, ...props }, ref) => {
    // Determine variant based on tag type, default to 'default' if not found
    const variant = (tagTypeToVariant[type as keyof typeof tagTypeToVariant] ||
      "default") as any;

    return (
      <div
        ref={ref}
        className={cn(tagVariants({ variant, size, className }))}
        {...props}
      >
        {type}
      </div>
    );
  }
);

SemanticTag.displayName = "SemanticTag";

export { SemanticTag, tagVariants };
