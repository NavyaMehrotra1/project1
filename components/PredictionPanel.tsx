'use client'

import { useState } from 'react'
import { TrendingUp, Eye, EyeOff, RefreshCw, Sparkles } from 'lucide-react'

interface PredictionPanelProps {
  onTogglePredictions: () => void
  showPredictions: boolean
  onRefresh: () => void
}

export function PredictionPanel({ onTogglePredictions, showPredictions, onRefresh }: PredictionPanelProps) {
  const [isGenerating, setIsGenerating] = useState(false)

  const handleTogglePredictions = async () => {
    if (!showPredictions) {
      setIsGenerating(true)
      await onTogglePredictions()
      setIsGenerating(false)
    } else {
      onTogglePredictions()
    }
  }

  return (
    <div className="graph-controls">
      <div className="bg-white rounded-lg shadow-lg p-4 space-y-3">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <TrendingUp size={18} />
          AI Predictions
        </h3>
        
        <div className="space-y-2">
          <button
            onClick={handleTogglePredictions}
            disabled={isGenerating}
            className={`
              w-full flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-all
              ${showPredictions 
                ? 'bg-yellow-100 text-yellow-800 border border-yellow-300' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
              }
              ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            {isGenerating ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                Generating...
              </>
            ) : showPredictions ? (
              <>
                <EyeOff size={16} />
                Hide Predictions
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Show Predictions
              </>
            )}
          </button>

          <button
            onClick={onRefresh}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            <RefreshCw size={16} />
            Refresh Data
          </button>
        </div>

        {showPredictions && (
          <div className="text-xs text-yellow-700 bg-yellow-50 p-2 rounded">
            <div className="flex items-center gap-1 mb-1">
              <Eye size={12} />
              Prediction Mode Active
            </div>
            Dashed lines show AI-predicted future deals
          </div>
        )}
      </div>
    </div>
  )
}
