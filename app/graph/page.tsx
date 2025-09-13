'use client';

import ExtraordinaryGraphVisualization from '../../components/ExtraordinaryGraphVisualization';

export default function GraphPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Network Graph Visualization
        </h1>
        <p className="text-gray-600">
          Interactive network visualization with extraordinary company highlighting and logos
        </p>
      </div>
      
      <ExtraordinaryGraphVisualization />
    </div>
  );
}
