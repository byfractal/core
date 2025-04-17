import React from "react";
import { Optimization, SemanticTag } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import {
  ActionMenu,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { SemanticTag as SemanticTagComponent } from "@/components/ui/semantic-tag";
import { File, Trash, Copy, ExternalLink } from "lucide-react";

interface ProjectCardProps {
  optimization: Optimization;
  onSelect: (optimization: Optimization) => void;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
  className?: string;
}

/**
 * ProjectCard Component
 *
 * Displays a card for a project optimization with title, timestamp, tags and actions
 */
export const ProjectCard: React.FC<ProjectCardProps> = ({
  optimization,
  onSelect,
  onDelete,
  onDuplicate,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-row items-center p-4 border border-figma-border rounded-md bg-figma-background cursor-pointer hover:bg-gray-50 transition-colors",
        className
      )}
      onClick={() => onSelect(optimization)}
    >
      {/* Project Icon */}
      <div className="flex-shrink-0 mr-4">
        <File className="h-6 w-6 text-figma-text-primary" />
      </div>

      {/* Project Info */}
      <div className="flex-grow">
        <div className="flex flex-row items-center justify-between">
          <h3 className="text-sm font-medium font-geist text-figma-text-primary">
            {optimization.title}
          </h3>
        </div>

        <div className="mt-1 text-sm font-normal text-figma-text-timestamp font-geist">
          {optimization.createdAt
            ? formatDate(optimization.createdAt)
            : "No date"}
        </div>

        {/* Tags */}
        {optimization.tags && optimization.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {optimization.tags.map((tag) => (
              <SemanticTagComponent
                key={`${optimization.id}-${tag.type}`}
                type={tag.type}
                size="sm"
              />
            ))}
          </div>
        )}
      </div>

      {/* More Actions Menu */}
      <div onClick={(e) => e.stopPropagation()}>
        <ActionMenu>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onDuplicate(optimization.id)}>
              <Copy className="mr-2 h-4 w-4" />
              <span>Duplicate</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onSelect(optimization)}>
              <ExternalLink className="mr-2 h-4 w-4" />
              <span>Open</span>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(optimization.id)}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash className="mr-2 h-4 w-4" />
              <span>Delete</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </ActionMenu>
      </div>
    </div>
  );
};

// New Project Card Component
interface NewProjectCardProps {
  onAddProject: () => void;
  className?: string;
}

export const NewProjectCard: React.FC<NewProjectCardProps> = ({
  onAddProject,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-row items-center p-4 border border-figma-border rounded-md bg-figma-background cursor-pointer hover:bg-gray-50 transition-colors",
        className
      )}
      onClick={onAddProject}
    >
      <div className="mr-4">
        <File className="h-6 w-6 text-figma-text-primary" />
      </div>
      <div className="flex-grow">
        <h3 className="text-sm font-medium font-geist text-figma-text-primary">
          New Optimization
        </h3>
      </div>
      <div className="bg-figma-text-primary text-figma-background px-3 py-1 rounded-md text-xs font-medium hover:opacity-90 transition-opacity">
        Add Project
      </div>
    </div>
  );
};
