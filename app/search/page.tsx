'use client';

import VectorSearchPanel from '../../components/VectorSearchPanel';

export default function SearchPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Semantic Search
        </h1>
        <p className="text-gray-600">
          Search companies and relationships using natural language powered by vector embeddings
        </p>
      </div>
      
      <VectorSearchPanel />
    </div>
  );
}
