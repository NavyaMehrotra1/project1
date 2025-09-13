'use client';

import ExtraordinaryLeaderboard from '../../components/ExtraordinaryLeaderboard';

export default function ExtraordinaryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Extraordinary Companies
        </h1>
        <p className="text-gray-600">
          Discover the most extraordinary companies based on comprehensive research and scoring
        </p>
      </div>
      
      <ExtraordinaryLeaderboard />
    </div>
  );
}
