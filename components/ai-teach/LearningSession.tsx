'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  Brain, 
  CheckCircle, 
  Clock, 
  BookOpen,
  MessageCircle,
  Lightbulb,
  Target,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import { aiTeachService, UserProfile, LearningConcept, ExplanationResponse } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface LearningSessionProps {
  userProfile: UserProfile
  onBack: () => void
  onProfileUpdate: (profile: UserProfile) => void
}

export const LearningSession: React.FC<LearningSessionProps> = ({
  userProfile,
  onBack,
  onProfileUpdate
}) => {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentConcept, setCurrentConcept] = useState<LearningConcept | null>(null)
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [explaining, setExplaining] = useState(false)
  const [userQuestion, setUserQuestion] = useState('')
  const [sessionStartTime] = useState(new Date())
  const [conceptsLearned, setConceptsLearned] = useState<string[]>([])
  const [showQuiz, setShowQuiz] = useState(false)
  const [quizAnswer, setQuizAnswer] = useState('')

  useEffect(() => {
    startSession()
  }, [])

  const startSession = async () => {
    try {
      setLoading(true)
      // Mock session start for now
      const mockSessionId = `session_${Date.now()}`
      setSessionId(mockSessionId)
      
      // Get first concept based on user level
      await loadNextConcept()
      
    } catch (error) {
      console.error('Error starting session:', error)
      toast.error('Failed to start learning session')
    } finally {
      setLoading(false)
    }
  }

  const loadNextConcept = async () => {
    try {
      // Mock concept loading based on user level
      const mockConcepts = getMockConceptsForLevel(userProfile.current_level)
      const availableConcepts = mockConcepts.filter(c => !conceptsLearned.includes(c.id))
      
      if (availableConcepts.length === 0) {
        toast.success('Congratulations! You\'ve completed all concepts for your level.')
        return
      }
      
      const nextConcept = availableConcepts[0]
      setCurrentConcept(nextConcept)
      
      // Get AI explanation for the concept
      await explainConcept(nextConcept)
      
    } catch (error) {
      console.error('Error loading next concept:', error)
      toast.error('Failed to load next concept')
    }
  }

  const explainConcept = async (concept: LearningConcept) => {
    try {
      setExplaining(true)
      
      // Mock AI explanation
      const mockExplanation: ExplanationResponse = {
        explanation: generateMockExplanation(concept, userProfile.current_level),
        user_level: userProfile.current_level,
        confidence: 0.9,
        follow_up_topics: concept.prerequisites.slice(0, 3),
        prerequisite_check: false
      }
      
      setExplanation(mockExplanation)
      
    } catch (error) {
      console.error('Error getting explanation:', error)
      toast.error('Failed to get explanation')
    } finally {
      setExplaining(false)
    }
  }

  const handleUserQuestion = async () => {
    if (!userQuestion.trim()) return
    
    try {
      setExplaining(true)
      
      // Mock AI response to user question
      const mockResponse: ExplanationResponse = {
        explanation: `Great question! Let me explain that in the context of ${currentConcept?.name}. ${userQuestion.includes('example') ? 'Here are some real-world examples...' : 'This relates to the concept because...'}`,
        user_level: userProfile.current_level,
        confidence: 0.85,
        follow_up_topics: ['related_concept_1', 'related_concept_2'],
        prerequisite_check: false
      }
      
      setExplanation(mockResponse)
      setUserQuestion('')
      
    } catch (error) {
      console.error('Error getting AI response:', error)
      toast.error('Failed to get AI response')
    } finally {
      setExplaining(false)
    }
  }

  const handleConceptComplete = () => {
    if (!currentConcept) return
    
    setConceptsLearned(prev => [...prev, currentConcept.id])
    
    // Update user profile
    const updatedProfile = {
      ...userProfile,
      known_concepts: [...userProfile.known_concepts, currentConcept.id]
    }
    onProfileUpdate(updatedProfile)
    localStorage.setItem('ai-teach-profile', JSON.stringify(updatedProfile))
    
    toast.success(`Concept "${currentConcept.name}" completed!`)
    
    // Load next concept
    setTimeout(() => {
      loadNextConcept()
      setShowQuiz(false)
      setQuizAnswer('')
    }, 1000)
  }

  const getMockConceptsForLevel = (level: string): LearningConcept[] => {
    const allConcepts: LearningConcept[] = [
      {
        id: 'company_basics',
        name: 'Company Fundamentals',
        description: 'Understanding what companies are and how they operate',
        difficulty_level: 1,
        prerequisites: [],
        examples: ['Apple Inc.', 'Microsoft Corporation'],
        learning_objectives: ['Understand corporate structure', 'Know business basics'],
        ma_context: 'Foundation for understanding M&A transactions',
        real_world_examples: ['Public vs private companies']
      },
      {
        id: 'merger_vs_acquisition',
        name: 'Mergers vs Acquisitions',
        description: 'Key differences between mergers and acquisitions',
        difficulty_level: 2,
        prerequisites: ['company_basics'],
        examples: ['Disney + Pixar (acquisition)', 'Exxon + Mobil (merger)'],
        learning_objectives: ['Distinguish merger from acquisition'],
        ma_context: 'Fundamental M&A transaction types',
        real_world_examples: ['Facebook acquiring Instagram']
      },
      {
        id: 'due_diligence',
        name: 'Due Diligence Process',
        description: 'Comprehensive investigation before M&A transactions',
        difficulty_level: 3,
        prerequisites: ['merger_vs_acquisition'],
        examples: ['Financial DD', 'Legal DD', 'Commercial DD'],
        learning_objectives: ['Understand DD process', 'Know DD types'],
        ma_context: 'Critical risk assessment phase in M&A',
        real_world_examples: ['Microsoft acquisition of LinkedIn']
      }
    ]
    
    return allConcepts.filter(c => {
      if (level === 'beginner') return c.difficulty_level <= 2
      if (level === 'intermediate') return c.difficulty_level <= 3
      return true
    })
  }

  const generateMockExplanation = (concept: LearningConcept, level: string): string => {
    const explanations = {
      beginner: `Let me explain ${concept.name} in simple terms. ${concept.description} Think of it like this: ${concept.examples[0] || 'a real-world example'}. This is important in M&A because ${concept.ma_context}`,
      intermediate: `${concept.name} is ${concept.description}. In M&A context, ${concept.ma_context}. Key examples include ${concept.examples.join(', ')}. This concept is essential because it ${concept.learning_objectives[0]}`,
      expert: `${concept.name}: ${concept.description}. Strategic implications in M&A: ${concept.ma_context}. Advanced considerations include ${concept.learning_objectives.join(', ')}. Real-world applications: ${concept.real_world_examples.join(', ')}`
    }
    
    return explanations[level as keyof typeof explanations] || explanations.intermediate
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Starting Learning Session...</p>
        </div>
      </div>
    )
  }

  const sessionDuration = Math.floor((new Date().getTime() - sessionStartTime.getTime()) / 60000)

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-white hover:text-blue-300 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Dashboard
          </button>
          
          <div className="text-center">
            <h1 className="text-2xl font-bold text-white">Learning Session</h1>
            <p className="text-gray-300">Level: {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}</p>
          </div>
          
          <div className="flex items-center gap-4 text-gray-300">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{sessionDuration}m</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span>{conceptsLearned.length}</span>
            </div>
          </div>
        </div>

        {/* Session Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6 max-w-4xl mx-auto">
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
            <div className="text-2xl font-bold text-blue-400">{conceptsLearned.length}</div>
            <div className="text-gray-300 text-sm">Concepts Learned</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
            <div className="text-2xl font-bold text-green-400">{sessionDuration}</div>
            <div className="text-gray-300 text-sm">Minutes</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
            <div className="text-2xl font-bold text-purple-400">{userProfile.current_level}</div>
            <div className="text-gray-300 text-sm">Level</div>
          </div>
          <div className="bg-black/20 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
            <div className="text-2xl font-bold text-orange-400">{userProfile.known_concepts.length}</div>
            <div className="text-gray-300 text-sm">Total Known</div>
          </div>
        </div>

        {/* Main Content */}
        {currentConcept && (
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Concept Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Current Concept */}
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <BookOpen className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-white mb-2">{currentConcept.name}</h2>
                    <p className="text-gray-300 mb-4">{currentConcept.description}</p>
                    
                    {/* Learning Objectives */}
                    <div className="mb-4">
                      <h3 className="text-white font-semibold mb-2">Learning Objectives:</h3>
                      <ul className="space-y-1">
                        {currentConcept.learning_objectives.map((objective, index) => (
                          <li key={index} className="flex items-center gap-2 text-gray-300">
                            <Target className="w-4 h-4 text-green-400" />
                            {objective}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Explanation */}
              {explanation && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10"
                >
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                      <Brain className="w-5 h-5 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-semibold mb-2">AI Teacher Explanation</h3>
                      {explaining ? (
                        <div className="flex items-center gap-2 text-gray-400">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400"></div>
                          Generating explanation...
                        </div>
                      ) : (
                        <div className="text-gray-300 leading-relaxed">
                          {explanation.explanation}
                        </div>
                      )}
                    </div>
                  </div>

                  {explanation.follow_up_topics.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-white/10">
                      <h4 className="text-white font-medium mb-2">Related Topics:</h4>
                      <div className="flex flex-wrap gap-2">
                        {explanation.follow_up_topics.map((topic, index) => (
                          <span
                            key={index}
                            className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm"
                          >
                            {topic.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Examples */}
              {currentConcept.examples.length > 0 && (
                <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    Examples
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {currentConcept.examples.map((example, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <p className="text-gray-300">{example}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quiz Section */}
              {!showQuiz ? (
                <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <div className="text-center">
                    <h3 className="text-white font-semibold mb-4">Ready to test your understanding?</h3>
                    <button
                      onClick={() => setShowQuiz(true)}
                      className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-blue-600 transition-all flex items-center gap-2 mx-auto"
                    >
                      <Play className="w-4 h-4" />
                      Take Quick Quiz
                    </button>
                  </div>
                </div>
              ) : (
                <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                  <h3 className="text-white font-semibold mb-4">Quick Understanding Check</h3>
                  <p className="text-gray-300 mb-4">
                    In your own words, explain what {currentConcept.name} means and why it's important in M&A:
                  </p>
                  <textarea
                    value={quizAnswer}
                    onChange={(e) => setQuizAnswer(e.target.value)}
                    placeholder="Type your explanation here..."
                    className="w-full p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none mb-4"
                    rows={4}
                  />
                  <div className="flex gap-3">
                    <button
                      onClick={handleConceptComplete}
                      disabled={!quizAnswer.trim()}
                      className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
                        quizAnswer.trim()
                          ? 'bg-gradient-to-r from-green-500 to-blue-500 text-white hover:from-green-600 hover:to-blue-600'
                          : 'bg-gray-600/20 text-gray-500 cursor-not-allowed'
                      }`}
                    >
                      <CheckCircle className="w-4 h-4" />
                      Complete Concept
                    </button>
                    <button
                      onClick={() => setShowQuiz(false)}
                      className="px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
                    >
                      Skip Quiz
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Ask AI */}
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                  <MessageCircle className="w-5 h-5 text-blue-400" />
                  Ask AI Teacher
                </h3>
                <textarea
                  value={userQuestion}
                  onChange={(e) => setUserQuestion(e.target.value)}
                  placeholder="Ask any question about this concept..."
                  className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none mb-3"
                  rows={3}
                />
                <button
                  onClick={handleUserQuestion}
                  disabled={!userQuestion.trim() || explaining}
                  className={`w-full py-2 rounded-lg transition-all ${
                    userQuestion.trim() && !explaining
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-gray-600/20 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {explaining ? 'Getting Answer...' : 'Ask Question'}
                </button>
              </div>

              {/* Progress */}
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4">Session Progress</h3>
                <div className="space-y-3">
                  {conceptsLearned.map((conceptId, index) => (
                    <div key={conceptId} className="flex items-center gap-2 text-green-400">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-sm">Concept {index + 1} completed</span>
                    </div>
                  ))}
                  {currentConcept && (
                    <div className="flex items-center gap-2 text-blue-400">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">Currently learning: {currentConcept.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
                <h3 className="text-white font-semibold mb-4">Session Actions</h3>
                <div className="space-y-3">
                  <button
                    onClick={() => currentConcept && explainConcept(currentConcept)}
                    className="w-full py-2 bg-purple-500/20 text-purple-300 rounded-lg hover:bg-purple-500/30 transition-all flex items-center justify-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Re-explain Concept
                  </button>
                  <button
                    onClick={loadNextConcept}
                    className="w-full py-2 bg-green-500/20 text-green-300 rounded-lg hover:bg-green-500/30 transition-all flex items-center justify-center gap-2"
                  >
                    <ArrowLeft className="w-4 h-4 rotate-180" />
                    Next Concept
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
