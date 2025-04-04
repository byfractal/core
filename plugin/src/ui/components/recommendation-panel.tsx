import * as React from "react";
import { DesignChangesCollectionInterface } from "../../types/design-changes";

interface RecommendationPanelProps {
  recommendations: DesignChangesCollectionInterface | null;
  onApply: (collectionId: string) => void;
  isApplying: boolean;
  applyResults: { success: number; failed: number; total: number } | null;
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({
  recommendations,
  onApply,
  isApplying,
  applyResults,
}) => {
  if (!recommendations) {
    return (
      <div className="p-4 text-center">
        <p className="text-gray-500">No recommendations available yet</p>
      </div>
    );
  }

  const { title, description, changes, metrics } = recommendations;

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>

      <div className="p-4 border-b border-gray-200 flex gap-4">
        <div className="bg-gray-100 rounded-lg p-3 flex-1">
          <span className="block text-xs text-gray-500">Impact Score</span>
          <span className="block text-lg font-medium">
            {metrics?.expectedImprovementScore || 0}/100
          </span>
        </div>

        <div className="bg-gray-100 rounded-lg p-3 flex-1">
          <span className="block text-xs text-gray-500">Changes</span>
          <span className="block text-lg font-medium">{changes.length}</span>
        </div>

        <div className="bg-gray-100 rounded-lg p-3 flex-1">
          <span className="block text-xs text-gray-500">Priority</span>
          <span className="block text-lg font-medium">
            {metrics?.priority || "LOW"}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <h3 className="font-medium mb-2">Impact Areas</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          {metrics?.impactAreas.map((area) => (
            <span
              key={area}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {area}
            </span>
          ))}
        </div>

        <h3 className="font-medium mb-2 mt-4">Proposed Changes</h3>
        <div className="space-y-3">
          {changes.map((change) => (
            <div
              key={change.id}
              className="border border-gray-200 rounded-md p-3"
            >
              <div className="flex justify-between items-start">
                <span className="inline-block px-2 py-1 text-xs rounded-md bg-gray-200">
                  {change.action}
                </span>
                <span className="text-xs text-gray-500">
                  {change.targetId
                    ? `#${change.targetId.slice(0, 8)}`
                    : "New Element"}
                </span>
              </div>

              <p className="text-sm mt-2">{change.metadata?.reasonForChange}</p>

              <div className="mt-2 text-xs text-gray-600">
                Expected: {change.metadata?.expectedImprovement}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-200 p-4">
        {applyResults && (
          <div className="mb-3 text-sm">
            Applied {applyResults.success} of {applyResults.total} changes
            {applyResults.failed > 0 && (
              <span className="text-red-500">
                {" "}
                ({applyResults.failed} failed)
              </span>
            )}
          </div>
        )}

        <button
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md font-medium disabled:bg-blue-300"
          onClick={() => onApply(recommendations.id)}
          disabled={isApplying}
        >
          {isApplying ? "Applying..." : "Apply Recommendations"}
        </button>
      </div>
    </div>
  );
};
