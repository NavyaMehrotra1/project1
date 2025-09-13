'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExternalLink, Info, Shield, AlertCircle } from 'lucide-react'
import { CitationTooltip as CitationTooltipType } from '@/types'

interface CitationTooltipProps {
  citation: CitationTooltipType
  children: React.ReactNode
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

export const CitationTooltip: React.FC<CitationTooltipProps> = ({
  citation,
  children,
  position = 'top',
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  const handleMouseEnter = (e: React.MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY })
    setIsVisible(true)
  }

  const handleMouseLeave = () => {
    setIsVisible(false)
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-400'
    if (confidence >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return <Shield size={12} />
    if (confidence >= 0.6) return <Info size={12} />
    return <AlertCircle size={12} />
  }

  const getTooltipPosition = () => {
    const offset = 10
    switch (position) {
      case 'top':
        return { bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: `${offset}px` }
      case 'bottom':
        return { top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: `${offset}px` }
      case 'left':
        return { right: '100%', top: '50%', transform: 'translateY(-50%)', marginRight: `${offset}px` }
      case 'right':
        return { left: '100%', top: '50%', transform: 'translateY(-50%)', marginLeft: `${offset}px` }
      default:
        return { bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: `${offset}px` }
    }
  }

  return (
    <div 
      className={`relative inline-block ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 w-80 bg-gray-900 border border-gray-700 rounded-lg shadow-xl p-4"
            style={getTooltipPosition()}
          >
            {/* Arrow */}
            <div 
              className={`absolute w-2 h-2 bg-gray-900 border-gray-700 transform rotate-45 ${
                position === 'top' ? 'top-full left-1/2 -translate-x-1/2 -mt-1 border-b border-r' :
                position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 -mb-1 border-t border-l' :
                position === 'left' ? 'left-full top-1/2 -translate-y-1/2 -ml-1 border-t border-r' :
                'right-full top-1/2 -translate-y-1/2 -mr-1 border-b border-l'
              }`}
            />

            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`flex items-center gap-1 ${getConfidenceColor(citation.confidence)}`}>
                  {getConfidenceIcon(citation.confidence)}
                  <span className="text-xs font-medium">
                    {(citation.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
              </div>
              {citation.url && (
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink size={14} />
                </a>
              )}
            </div>

            {/* Content */}
            <div className="space-y-2">
              <p className="text-white text-sm leading-relaxed">
                {citation.content}
              </p>
              
              {/* Source */}
              <div className="pt-2 border-t border-gray-700">
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-xs">Source:</span>
                  <span className="text-gray-300 text-xs font-medium">
                    {citation.source}
                  </span>
                </div>
              </div>
            </div>

            {/* Confidence Bar */}
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span>Reliability</span>
                <span>{(citation.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-1.5">
                <div 
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    citation.confidence >= 0.8 ? 'bg-green-400' :
                    citation.confidence >= 0.6 ? 'bg-yellow-400' : 'bg-red-400'
                  }`}
                  style={{ width: `${citation.confidence * 100}%` }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Hook for creating citation tooltips from data
export const useCitationTooltips = () => {
  const createCitation = (
    content: string,
    source: string,
    confidence: number = 0.8,
    url?: string
  ): CitationTooltipType => ({
    id: `citation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    content,
    source,
    confidence,
    url
  })

  const wrapWithCitation = (
    text: string,
    citation: CitationTooltipType,
    className: string = 'border-b border-dotted border-blue-400 cursor-help'
  ) => (
    <CitationTooltip citation={citation}>
      <span className={className}>{text}</span>
    </CitationTooltip>
  )

  return { createCitation, wrapWithCitation }
}
