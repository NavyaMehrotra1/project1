'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Play, 
  RotateCcw, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Building,
  Globe,
  AlertTriangle,
  CheckCircle,
  Brain,
  Target,
  Zap
} from 'lucide-react'
import { UserProfile } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface ScenarioSimulatorProps {
  userProfile: UserProfile
  onBack: () => void
}

interface Scenario {
  id: string
  title: string
  description: string
  industry: string
  difficulty: string
  initial_situation: string
  key_factors: string[]
  decision_points: DecisionPoint[]
  learning_objectives: string[]
}

interface DecisionPoint {
  id: string
  question: string
  options: Option[]
  correct_option: string
  explanation: string
  impact_description: string
}

interface Option {
  id: string
  text: string
  impact: 'positive' | 'negative' | 'neutral'
  consequences: string[]
}

interface SimulationResult {
  score: number
  decisions: { [key: string]: string }
  feedback: string[]
  key_learnings: string[]
  next_steps: string[]
}

export const ScenarioSimulator: React.FC<ScenarioSimulatorProps> = ({
  userProfile,
  onBack
}) => {
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null)
  const [currentDecisionIndex, setCurrentDecisionIndex] = useState(0)
  const [userDecisions, setUserDecisions] = useState<{ [key: string]: string }>({})
  const [simulationComplete, setSimulationComplete] = useState(false)
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const [loading, setLoading] = useState(false)

  const scenarios: Scenario[] = [
    {
      id: 'tech_acquisition',
      title: 'Tech Startup Acquisition',
      description: 'Navigate the acquisition of a promising AI startup by a large tech company',
      industry: 'Technology',
      difficulty: userProfile.current_level === 'beginner' ? 'beginner' : 'intermediate',
      initial_situation: 'TechCorp is considering acquiring AI-Innovate, a 50-person startup with breakthrough machine learning technology. The startup is valued at $500M but has limited revenue.',
      key_factors: ['Technology IP', 'Talent retention', 'Cultural fit', 'Integration complexity', 'Market timing'],
      decision_points: [
        {
          id: 'valuation_approach',
          question: 'How should TechCorp approach the valuation of AI-Innovate?',
          options: [
            {
              id: 'revenue_multiple',
              text: 'Use traditional revenue multiples from comparable companies',
              impact: 'negative',
              consequences: ['May undervalue IP assets', 'Misses growth potential', 'Could lose deal to competitors']
            },
            {
              id: 'dcf_analysis',
              text: 'Perform detailed DCF analysis with growth projections',
              impact: 'positive',
              consequences: ['Captures future value potential', 'Provides negotiation framework', 'Justifies premium pricing']
            },
            {
              id: 'asset_based',
              text: 'Focus on tangible assets and current cash flows',
              impact: 'negative',
              consequences: ['Ignores key IP value', 'Underestimates strategic worth', 'Inappropriate for tech startups']
            }
          ],
          correct_option: 'dcf_analysis',
          explanation: 'For tech startups with valuable IP but limited current revenue, DCF analysis with growth projections better captures the strategic value and future potential.',
          impact_description: 'Proper valuation methodology is crucial for successful tech acquisitions'
        },
        {
          id: 'integration_strategy',
          question: 'What integration approach should TechCorp take post-acquisition?',
          options: [
            {
              id: 'full_integration',
              text: 'Immediately integrate all systems and processes',
              impact: 'negative',
              consequences: ['Risk of talent flight', 'Disrupts innovation culture', 'May destroy startup agility']
            },
            {
              id: 'autonomous_operation',
              text: 'Keep AI-Innovate as autonomous subsidiary',
              impact: 'positive',
              consequences: ['Preserves startup culture', 'Retains key talent', 'Maintains innovation speed']
            },
            {
              id: 'selective_integration',
              text: 'Integrate only back-office functions initially',
              impact: 'neutral',
              consequences: ['Moderate culture preservation', 'Some efficiency gains', 'Gradual transition approach']
            }
          ],
          correct_option: 'autonomous_operation',
          explanation: 'For innovative tech startups, maintaining autonomy initially helps preserve the culture and talent that made them valuable.',
          impact_description: 'Integration strategy significantly impacts talent retention and innovation preservation'
        }
      ],
      learning_objectives: [
        'Understand tech acquisition valuation challenges',
        'Learn integration strategies for startups',
        'Recognize importance of talent retention'
      ]
    },
    {
      id: 'healthcare_merger',
      title: 'Healthcare System Merger',
      description: 'Manage the merger of two regional healthcare systems to achieve scale and efficiency',
      industry: 'Healthcare',
      difficulty: userProfile.current_level === 'expert' ? 'expert' : 'intermediate',
      initial_situation: 'Regional Health Network and Community Medical Center are merging to create a $2B healthcare system serving 500,000 patients across three states.',
      key_factors: ['Regulatory approval', 'Patient care continuity', 'Cost synergies', 'Staff integration', 'Technology systems'],
      decision_points: [
        {
          id: 'regulatory_strategy',
          question: 'How should the merger address antitrust concerns?',
          options: [
            {
              id: 'market_dominance',
              text: 'Emphasize market dominance benefits for negotiating with insurers',
              impact: 'negative',
              consequences: ['Raises antitrust red flags', 'May trigger DOJ investigation', 'Could block merger approval']
            },
            {
              id: 'patient_benefits',
              text: 'Focus on improved patient outcomes and cost savings',
              impact: 'positive',
              consequences: ['Addresses public interest concerns', 'Supports regulatory approval', 'Demonstrates value creation']
            },
            {
              id: 'ignore_concerns',
              text: 'Proceed without addressing antitrust issues',
              impact: 'negative',
              consequences: ['High risk of regulatory challenge', 'Potential merger failure', 'Wasted resources and time']
            }
          ],
          correct_option: 'patient_benefits',
          explanation: 'Healthcare mergers must demonstrate clear patient benefits and public interest value to gain regulatory approval.',
          impact_description: 'Regulatory strategy is critical for healthcare merger success'
        }
      ],
      learning_objectives: [
        'Understand healthcare merger regulations',
        'Learn about patient care considerations',
        'Recognize synergy identification in healthcare'
      ]
    }
  ]

  const startSimulation = (scenario: Scenario) => {
    setSelectedScenario(scenario)
    setCurrentDecisionIndex(0)
    setUserDecisions({})
    setSimulationComplete(false)
    setSimulationResult(null)
    setShowExplanation(false)
  }

  const makeDecision = (decisionId: string, optionId: string) => {
    const newDecisions = { ...userDecisions, [decisionId]: optionId }
    setUserDecisions(newDecisions)
    setShowExplanation(true)
    
    // Auto-advance after showing explanation
    setTimeout(() => {
      if (currentDecisionIndex < selectedScenario!.decision_points.length - 1) {
        setCurrentDecisionIndex(currentDecisionIndex + 1)
        setShowExplanation(false)
      } else {
        completeSimulation(newDecisions)
      }
    }, 3000)
  }

  const completeSimulation = async (decisions: { [key: string]: string }) => {
    setLoading(true)
    
    // Calculate score based on correct decisions
    let correctDecisions = 0
    const feedback: string[] = []
    const keyLearnings: string[] = []
    
    selectedScenario!.decision_points.forEach(dp => {
      const userChoice = decisions[dp.id]
      const selectedOption = dp.options.find(opt => opt.id === userChoice)
      
      if (userChoice === dp.correct_option) {
        correctDecisions++
        feedback.push(`✓ ${dp.question}: Excellent choice! ${dp.explanation}`)
      } else {
        feedback.push(`✗ ${dp.question}: ${selectedOption?.consequences[0] || 'Suboptimal choice'}. ${dp.explanation}`)
      }
      
      keyLearnings.push(dp.impact_description)
    })
    
    const score = Math.round((correctDecisions / selectedScenario!.decision_points.length) * 100)
    
    const result: SimulationResult = {
      score,
      decisions,
      feedback,
      key_learnings: keyLearnings,
      next_steps: [
        'Review decision explanations',
        'Study related M&A concepts',
        'Try more advanced scenarios'
      ]
    }
    
    setSimulationResult(result)
    setSimulationComplete(true)
    setLoading(false)
    
    // Show completion toast
    if (score >= 80) {
      toast.success(`Excellent performance! Score: ${score}%`)
    } else if (score >= 60) {
      toast.success(`Good job! Score: ${score}%`)
    } else {
      toast.error(`Keep learning! Score: ${score}%`)
    }
  }

  const resetSimulation = () => {
    setSelectedScenario(null)
    setCurrentDecisionIndex(0)
    setUserDecisions({})
    setSimulationComplete(false)
    setSimulationResult(null)
    setShowExplanation(false)
  }

  if (!selectedScenario) {
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
              <h1 className="text-3xl font-bold text-white mb-2">M&A Scenario Simulator</h1>
              <p className="text-gray-300">Practice decision-making with realistic M&A scenarios</p>
            </div>
            
            <div className="text-gray-300 text-sm">
              Level: {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}
            </div>
          </div>

          {/* Scenario Selection */}
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Choose Your Scenario</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {scenarios.map((scenario) => (
                <motion.div
                  key={scenario.id}
                  whileHover={{ scale: 1.02 }}
                  className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-blue-500/30 transition-all"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                      <Target className="w-6 h-6 text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">{scenario.title}</h3>
                      <p className="text-gray-300 text-sm mb-3">{scenario.description}</p>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
                        <span className="flex items-center gap-1">
                          <Building className="w-3 h-3" />
                          {scenario.industry}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          scenario.difficulty === 'beginner' ? 'bg-green-500/20 text-green-300' :
                          scenario.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-300' :
                          'bg-red-500/20 text-red-300'
                        }`}>
                          {scenario.difficulty}
                        </span>
                      </div>
                      
                      <p className="text-gray-400 text-sm mb-4">{scenario.initial_situation}</p>
                      
                      <div className="mb-4">
                        <h4 className="text-white font-medium mb-2">Key Factors:</h4>
                        <div className="flex flex-wrap gap-2">
                          {scenario.key_factors.map((factor, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs"
                            >
                              {factor}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <button
                        onClick={() => startSimulation(scenario)}
                        className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all flex items-center justify-center gap-2"
                      >
                        <Play className="w-4 h-4" />
                        Start Simulation
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (simulationComplete && simulationResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>

        <div className="relative z-10 p-6">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-white mb-2">Simulation Complete!</h1>
              <p className="text-gray-300">{selectedScenario.title}</p>
            </div>

            {/* Score */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-8 border border-white/10 mb-6 text-center">
              <div className="w-24 h-24 mx-auto mb-4 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">{simulationResult.score}%</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Your Performance</h2>
              <p className="text-gray-300">
                {simulationResult.score >= 80 ? 'Outstanding! You demonstrated excellent M&A decision-making skills.' :
                 simulationResult.score >= 60 ? 'Good work! You made solid decisions with room for improvement.' :
                 'Keep learning! Review the feedback to improve your M&A knowledge.'}
              </p>
            </div>

            {/* Detailed Feedback */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  Decision Feedback
                </h3>
                <div className="space-y-3">
                  {simulationResult.feedback.map((feedback, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className={`w-5 h-5 rounded-full flex items-center justify-center mt-0.5 ${
                        feedback.startsWith('✓') ? 'bg-green-500/20' : 'bg-red-500/20'
                      }`}>
                        {feedback.startsWith('✓') ? 
                          <CheckCircle className="w-3 h-3 text-green-400" /> :
                          <AlertTriangle className="w-3 h-3 text-red-400" />
                        }
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {feedback.substring(2)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  Key Learnings
                </h3>
                <div className="space-y-3">
                  {simulationResult.key_learnings.map((learning, index) => (
                    <div key={index} className="flex items-start gap-3">
                      <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0" />
                      <p className="text-gray-300 text-sm">{learning}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-center gap-4">
              <button
                onClick={resetSimulation}
                className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Try Another Scenario
              </button>
              <button
                onClick={onBack}
                className="bg-white/10 text-white px-6 py-3 rounded-lg hover:bg-white/20 transition-all"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Active simulation view
  const currentDecision = selectedScenario.decision_points[currentDecisionIndex]
  const progress = ((currentDecisionIndex + 1) / selectedScenario.decision_points.length) * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-orange-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-red-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={resetSimulation}
            className="flex items-center gap-2 text-white hover:text-blue-300 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Exit Simulation
          </button>
          
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white">{selectedScenario.title}</h1>
            <p className="text-gray-300">Decision {currentDecisionIndex + 1} of {selectedScenario.decision_points.length}</p>
          </div>
          
          <div className="text-gray-300 text-sm">
            Progress: {Math.round(progress)}%
          </div>
        </div>

        {/* Progress Bar */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="w-full bg-white/10 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Decision Content */}
        <div className="max-w-4xl mx-auto">
          {!showExplanation ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black/20 backdrop-blur-md rounded-xl p-8 border border-white/10"
            >
              <h2 className="text-2xl font-bold text-white mb-6">{currentDecision.question}</h2>
              
              <div className="grid grid-cols-1 gap-4">
                {currentDecision.options.map((option) => (
                  <motion.button
                    key={option.id}
                    whileHover={{ scale: 1.01 }}
                    onClick={() => makeDecision(currentDecision.id, option.id)}
                    className="bg-white/5 border border-white/10 rounded-lg p-6 text-left hover:border-blue-500/30 transition-all group"
                  >
                    <div className="flex items-start gap-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        option.impact === 'positive' ? 'bg-green-500/20' :
                        option.impact === 'negative' ? 'bg-red-500/20' :
                        'bg-yellow-500/20'
                      }`}>
                        {option.impact === 'positive' ? <TrendingUp className="w-4 h-4 text-green-400" /> :
                         option.impact === 'negative' ? <TrendingDown className="w-4 h-4 text-red-400" /> :
                         <DollarSign className="w-4 h-4 text-yellow-400" />}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium mb-2 group-hover:text-blue-300 transition-colors">
                          {option.text}
                        </p>
                        <p className="text-gray-400 text-sm">
                          Click to select this option
                        </p>
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black/20 backdrop-blur-md rounded-xl p-8 border border-white/10"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-white mb-2">Decision Analysis</h2>
                <p className="text-gray-300">Understanding the impact of your choice</p>
              </div>
              
              <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-3">Explanation:</h3>
                <p className="text-gray-300 leading-relaxed mb-4">{currentDecision.explanation}</p>
                
                <div className="border-t border-white/10 pt-4">
                  <h4 className="text-white font-medium mb-2">Impact:</h4>
                  <p className="text-gray-400 text-sm">{currentDecision.impact_description}</p>
                </div>
              </div>
              
              <div className="text-center mt-6">
                <div className="animate-pulse text-gray-400">
                  {currentDecisionIndex < selectedScenario.decision_points.length - 1 ? 
                    'Moving to next decision...' : 
                    'Calculating final results...'
                  }
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}
