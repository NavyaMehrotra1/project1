'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Search, 
  BookOpen, 
  Building, 
  TrendingUp,
  Users,
  DollarSign,
  FileText,
  ExternalLink,
  Lightbulb
} from 'lucide-react'
import { UserProfile } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface ConceptExplorerProps {
  userProfile: UserProfile
  onBack: () => void
}

interface MATerminology {
  [key: string]: {
    definition: string
    beginner_explanation: string
    intermediate_explanation: string
    expert_explanation: string
    examples: string[]
    related_terms: string[]
  }
}

interface CaseStudy {
  id: string
  title: string
  deal_value: number
  deal_type: string
  industry: string
  difficulty: string
  summary: string
  key_concepts: string[]
  outcomes: string[]
}

export const ConceptExplorer: React.FC<ConceptExplorerProps> = ({
  userProfile,
  onBack
}) => {
  const [activeTab, setActiveTab] = useState<'search' | 'cases' | 'industries'>('search')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedConcept, setSelectedConcept] = useState<string | null>(null)
  const [selectedCase, setSelectedCase] = useState<CaseStudy | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null)

  const maTerminology: MATerminology = {
    merger: {
      definition: "A combination of two companies where they agree to go forward as a single new company",
      beginner_explanation: "When two companies decide to join together and become one bigger company",
      intermediate_explanation: "A strategic combination where two companies of similar size combine to form a new entity",
      expert_explanation: "A transaction where two companies combine through share exchange, creating synergies and market consolidation",
      examples: ["Exxon + Mobil", "Disney + ABC", "AT&T + Time Warner"],
      related_terms: ["acquisition", "consolidation", "horizontal merger"]
    },
    acquisition: {
      definition: "When one company purchases most or all of another company's shares to gain control",
      beginner_explanation: "When a bigger company buys a smaller company to own it completely",
      intermediate_explanation: "A transaction where one company (acquirer) purchases another company (target) to gain control",
      expert_explanation: "Strategic purchase of target company assets or equity to achieve operational control and integration",
      examples: ["Facebook + Instagram", "Amazon + Whole Foods", "Microsoft + LinkedIn"],
      related_terms: ["takeover", "buyout", "strategic acquisition"]
    },
    synergy: {
      definition: "The concept that the value of combined companies will be greater than the sum of separate parts",
      beginner_explanation: "When two companies work better together than apart, like 1+1=3",
      intermediate_explanation: "Cost savings and revenue enhancements achieved through combining operations",
      expert_explanation: "Quantifiable value creation through operational efficiencies, market expansion, and strategic advantages",
      examples: ["Cost synergies", "Revenue synergies", "Tax synergies"],
      related_terms: ["value creation", "economies of scale", "cross-selling"]
    },
    "due diligence": {
      definition: "Investigation or audit of a potential investment or product to confirm facts",
      beginner_explanation: "Checking everything about a company before buying it, like inspecting a house before purchase",
      intermediate_explanation: "Comprehensive review of target company's financials, operations, and legal status",
      expert_explanation: "Systematic risk assessment covering financial, legal, commercial, and operational aspects of target",
      examples: ["Financial DD", "Legal DD", "Commercial DD", "IT DD"],
      related_terms: ["investigation", "audit", "risk assessment"]
    },
    valuation: {
      definition: "The analytical process of determining the current worth of an asset or company",
      beginner_explanation: "Figuring out how much a company is worth, like appraising a house",
      intermediate_explanation: "Using financial models to determine fair value for M&A transactions",
      expert_explanation: "Application of DCF, comparable company, and precedent transaction methodologies",
      examples: ["DCF analysis", "Trading multiples", "Transaction multiples"],
      related_terms: ["enterprise value", "equity value", "fair value"]
    }
  }

  const caseStudies: CaseStudy[] = [
    {
      id: "disney_pixar",
      title: "Disney Acquires Pixar (2006)",
      deal_value: 7.4,
      deal_type: "acquisition",
      industry: "entertainment",
      difficulty: "beginner",
      summary: "Disney acquired Pixar to revitalize its animation division and gain access to cutting-edge technology",
      key_concepts: ["strategic acquisition", "creative synergies", "cultural integration"],
      outcomes: [
        "Successful integration of creative teams",
        "Multiple successful film releases",
        "Technology transfer to Disney animation"
      ]
    },
    {
      id: "microsoft_linkedin",
      title: "Microsoft Acquires LinkedIn (2016)",
      deal_value: 26.2,
      deal_type: "acquisition",
      industry: "technology",
      difficulty: "intermediate",
      summary: "Microsoft's largest acquisition to expand into professional networking and enterprise services",
      key_concepts: ["strategic fit", "platform integration", "enterprise value"],
      outcomes: [
        "Successful revenue growth acceleration",
        "Integration with Microsoft Office suite",
        "Expansion of enterprise customer base"
      ]
    }
  ]

  const industries = {
    technology: {
      key_drivers: ["Digital transformation", "Platform consolidation", "Talent acquisition"],
      common_deal_types: ["Strategic acquisitions", "Acqui-hires", "Platform integrations"],
      examples: ["Microsoft + GitHub", "Salesforce + Slack", "Adobe + Figma"]
    },
    healthcare: {
      key_drivers: ["Cost reduction", "Scale economies", "Regulatory compliance"],
      common_deal_types: ["Horizontal mergers", "Vertical integration", "Portfolio optimization"],
      examples: ["CVS + Aetna", "UnitedHealth + Optum", "Anthem + Cigna (failed)"]
    },
    "financial services": {
      key_drivers: ["Digital disruption", "Regulatory efficiency", "Market expansion"],
      common_deal_types: ["Bank mergers", "Fintech acquisitions", "Cross-border deals"],
      examples: ["JPMorgan + Bear Stearns", "Wells Fargo + Wachovia", "PayPal + Venmo"]
    }
  }

  const filteredTerms = Object.keys(maTerminology).filter(term =>
    term.toLowerCase().includes(searchTerm.toLowerCase()) ||
    maTerminology[term].definition.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getExplanationForLevel = (term: string): string => {
    const termData = maTerminology[term]
    if (!termData) return ''
    
    const levelKey = `${userProfile.current_level}_explanation` as keyof typeof termData
    return termData[levelKey] || termData.definition
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-white hover:text-blue-300 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
          
          <div className="text-center">
            <h1 className="text-3xl font-bold text-white mb-2">M&A Concept Explorer</h1>
            <p className="text-gray-300">Discover terminology, case studies, and industry insights</p>
          </div>
          
          <div className="text-gray-300 text-sm">
            Level: {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-black/20 backdrop-blur-md rounded-xl p-2 border border-white/10">
            <div className="flex gap-2">
              {[
                { id: 'search', label: 'Search Terms', icon: Search },
                { id: 'cases', label: 'Case Studies', icon: FileText },
                { id: 'industries', label: 'Industries', icon: Building }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as any)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
                    activeTab === id
                      ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-6xl mx-auto">
          <AnimatePresence mode="wait">
            {activeTab === 'search' && (
              <motion.div
                key="search"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Search Bar */}
                <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search M&A terms and concepts..."
                      className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Terms Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredTerms.map((term) => (
                    <motion.div
                      key={term}
                      whileHover={{ scale: 1.02 }}
                      className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-blue-500/30 transition-all cursor-pointer"
                      onClick={() => setSelectedConcept(selectedConcept === term ? null : term)}
                    >
                      <div className="flex items-start gap-3 mb-3">
                        <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                          <BookOpen className="w-5 h-5 text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-white font-semibold capitalize">{term}</h3>
                          <p className="text-gray-400 text-sm mt-1">
                            {maTerminology[term].definition.slice(0, 80)}...
                          </p>
                        </div>
                      </div>
                      
                      {selectedConcept === term && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="border-t border-white/10 pt-4 mt-4"
                        >
                          <div className="mb-4">
                            <h4 className="text-white font-medium mb-2">Explanation for {userProfile.current_level}s:</h4>
                            <p className="text-gray-300 text-sm leading-relaxed">
                              {getExplanationForLevel(term)}
                            </p>
                          </div>
                          
                          <div className="mb-4">
                            <h4 className="text-white font-medium mb-2">Examples:</h4>
                            <div className="flex flex-wrap gap-2">
                              {maTerminology[term].examples.map((example, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs"
                                >
                                  {example}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-white font-medium mb-2">Related Terms:</h4>
                            <div className="flex flex-wrap gap-2">
                              {maTerminology[term].related_terms.map((relatedTerm, index) => (
                                <button
                                  key={index}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    setSearchTerm(relatedTerm)
                                    setSelectedConcept(null)
                                  }}
                                  className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs hover:bg-purple-500/30 transition-colors"
                                >
                                  {relatedTerm}
                                </button>
                              ))}
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'cases' && (
              <motion.div
                key="cases"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {caseStudies.map((caseStudy) => (
                    <motion.div
                      key={caseStudy.id}
                      whileHover={{ scale: 1.01 }}
                      className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-green-500/30 transition-all cursor-pointer"
                      onClick={() => setSelectedCase(selectedCase?.id === caseStudy.id ? null : caseStudy)}
                    >
                      <div className="flex items-start gap-4 mb-4">
                        <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                          <TrendingUp className="w-6 h-6 text-green-400" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-white font-semibold mb-2">{caseStudy.title}</h3>
                          <div className="flex items-center gap-4 text-sm text-gray-400 mb-2">
                            <span className="flex items-center gap-1">
                              <DollarSign className="w-3 h-3" />
                              ${caseStudy.deal_value}B
                            </span>
                            <span className="flex items-center gap-1">
                              <Building className="w-3 h-3" />
                              {caseStudy.industry}
                            </span>
                            <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                              {caseStudy.difficulty}
                            </span>
                          </div>
                          <p className="text-gray-300 text-sm">{caseStudy.summary}</p>
                        </div>
                      </div>

                      {selectedCase?.id === caseStudy.id && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="border-t border-white/10 pt-4 mt-4 space-y-4"
                        >
                          <div>
                            <h4 className="text-white font-medium mb-2">Key Concepts:</h4>
                            <div className="flex flex-wrap gap-2">
                              {caseStudy.key_concepts.map((concept, index) => (
                                <span
                                  key={index}
                                  className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm"
                                >
                                  {concept.replace('_', ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-white font-medium mb-2">Outcomes:</h4>
                            <ul className="space-y-1">
                              {caseStudy.outcomes.map((outcome, index) => (
                                <li key={index} className="flex items-start gap-2 text-gray-300 text-sm">
                                  <Lightbulb className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                                  {outcome}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'industries' && (
              <motion.div
                key="industries"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {Object.entries(industries).map(([industry, data]) => (
                    <motion.div
                      key={industry}
                      whileHover={{ scale: 1.02 }}
                      className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-orange-500/30 transition-all cursor-pointer"
                      onClick={() => setSelectedIndustry(selectedIndustry === industry ? null : industry)}
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                          <Building className="w-5 h-5 text-orange-400" />
                        </div>
                        <h3 className="text-white font-semibold capitalize">{industry.replace('_', ' ')}</h3>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <h4 className="text-white font-medium mb-2">Key Drivers:</h4>
                          <ul className="space-y-1">
                            {data.key_drivers.map((driver, index) => (
                              <li key={index} className="text-gray-300 text-sm flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-orange-400 rounded-full" />
                                {driver}
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="text-white font-medium mb-2">Common Deal Types:</h4>
                          <div className="flex flex-wrap gap-2">
                            {data.common_deal_types.map((dealType, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 bg-orange-500/20 text-orange-300 rounded text-xs"
                              >
                                {dealType}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 className="text-white font-medium mb-2">Notable Examples:</h4>
                          <ul className="space-y-1">
                            {data.examples.map((example, index) => (
                              <li key={index} className="text-gray-300 text-sm flex items-center gap-2">
                                <ExternalLink className="w-3 h-3 text-blue-400" />
                                {example}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
