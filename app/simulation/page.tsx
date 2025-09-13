'use client';

import EnhancedGraphWithSimulation from '../../components/EnhancedGraphWithSimulation';

export default function SimulationPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Impact Simulation Lab
        </h1>
        <p className="text-gray-600">
          Explore "what if" scenarios and see their real-time impact on the startup ecosystem
        </p>
      </div>
      
      <EnhancedGraphWithSimulation />
    </div>
  );
}
