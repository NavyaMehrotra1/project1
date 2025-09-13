'use client';

import { useParams } from 'next/navigation';
import ExtraordinaryProfile from '../../../components/ExtraordinaryProfile';

export default function ExtraordinaryProfilePage() {
  const params = useParams();
  const entityName = decodeURIComponent(params.entity as string);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Extraordinary Profile
        </h1>
        <p className="text-gray-600">
          Deep research and analysis of what makes this entity extraordinary
        </p>
      </div>
      
      <ExtraordinaryProfile entityName={entityName} />
    </div>
  );
}
