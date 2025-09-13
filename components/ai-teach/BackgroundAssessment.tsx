'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  ArrowRight, 
  CheckCircle, 
  Clock, 
  Target,
  Brain,
  BookOpen,
  TrendingUp
} from 'lucide-react'
import { aiTeachService, AssessmentQuestion, UserProfile } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface BackgroundAssessmentProps {
  onComplete: (profile: UserProfile) => void
  onBack: () => void
}

export const BackgroundAssessment: React.FC<BackgroundAssessmentProps> = ({
  onComplete,
  onBack
}) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([])
  const [responses, setResponses] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [userId, setUserId] = useState('')

  useEffect(() => {
    initializeAssessment()
  }, [])

  const initializeAssessment = async () => {
    try {
      setLoading(true)
      
      // Get or create user ID
      let id = localStorage.getItem('ai-teach-user-id')
      if (!id) {
        id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        localStorage.setItem('ai-teach-user-id', id)
      }
      setUserId(id)

      // For now, use mock questions (replace with actual API call when backend is ready)
      const assessmentQuestions = await aiTeachService.mockStartAssessment(id)
      setQuestions(assessmentQuestions)
      
    } catch (error) {
      console.error('Error initializing assessment:', error)
      toast.error('Failed to load assessment questions')
    } finally {
      setLoading(false)
    }
  }

  const handleResponse = (questionId: string, response: string) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: response
    }))
  }

  const handleNext = () => {
    const currentQuestion = questions[currentStep]
    if (!responses[currentQuestion.id]) {
      toast.error('Please answer the question before continuing')
      return
    }
    
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = async () => {
    try {
      setSubmitting(true)
      
      // Convert responses to array format
      const responseArray = questions.map(q => ({
        question_id: q.id,
        question: q.question,
        response: responses[q.id] || '',
        correct: q.correct_answer === responses[q.id]
      }))

      // Complete assessment (using mock for now)
      const profile = await aiTeachService.mockCompleteAssessment(userId, responseArray)
      
      toast.success('Assessment completed successfully!')
      onComplete(profile)
      
    } catch (error) {
      console.error('Error completing assessment:', error)
      toast.error('Failed to complete assessment')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Assessment...</p>
        </div>
      </div>
    )
  }

  const currentQuestion = questions[currentStep]
  const progress = ((currentStep + 1) / questions.length) * 100

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
            <h1 className="text-3xl font-bold text-white mb-2">Background Assessment</h1>
            <p className="text-gray-300">Help us understand your M&A knowledge level</p>
          </div>
          
          <div className="flex items-center gap-2 text-gray-300">
            <Clock className="w-5 h-5" />
            <span>{currentStep + 1} of {questions.length}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="bg-black/20 rounded-full h-2 backdrop-blur-md border border-white/10">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm text-gray-400">
            <span>Getting Started</span>
            <span>Assessment Complete</span>
          </div>
        </div>

        {/* Question Card */}
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="bg-black/20 backdrop-blur-md rounded-xl p-8 border border-white/10"
            >
              {/* Question Header */}
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-blue-400" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-blue-300 text-sm font-medium">
                      Question {currentStep + 1}
                    </span>
                    <span className="text-gray-400 text-sm">
                      • {currentQuestion.concept_area.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <h2 className="text-xl font-semibold text-white leading-relaxed">
                    {currentQuestion.question}
                  </h2>
                </div>
              </div>

              {/* Answer Options */}
              <div className="space-y-3 mb-8">
                {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options?.map((option, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    onClick={() => handleResponse(currentQuestion.id, option)}
                    className={`w-full text-left p-4 rounded-lg border transition-all ${
                      responses[currentQuestion.id] === option
                        ? 'bg-blue-500/20 border-blue-500/50 text-white'
                        : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                        responses[currentQuestion.id] === option
                          ? 'border-blue-400 bg-blue-500'
                          : 'border-gray-400'
                      }`}>
                        {responses[currentQuestion.id] === option && (
                          <CheckCircle className="w-4 h-4 text-white" />
                        )}
                      </div>
                      <span>{option}</span>
                    </div>
                  </motion.button>
                ))}

                {currentQuestion.question_type === 'true_false' && (
                  <div className="flex gap-4">
                    {['True', 'False'].map((option) => (
                      <motion.button
                        key={option}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleResponse(currentQuestion.id, option)}
                        className={`flex-1 p-4 rounded-lg border transition-all ${
                          responses[currentQuestion.id] === option
                            ? 'bg-blue-500/20 border-blue-500/50 text-white'
                            : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20'
                        }`}
                      >
                        <div className="flex items-center justify-center gap-3">
                          <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                            responses[currentQuestion.id] === option
                              ? 'border-blue-400 bg-blue-500'
                              : 'border-gray-400'
                          }`}>
                            {responses[currentQuestion.id] === option && (
                              <CheckCircle className="w-4 h-4 text-white" />
                            )}
                          </div>
                          <span className="font-medium">{option}</span>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                )}

                {currentQuestion.question_type === 'open_ended' && (
                  <textarea
                    value={responses[currentQuestion.id] || ''}
                    onChange={(e) => handleResponse(currentQuestion.id, e.target.value)}
                    placeholder="Type your answer here..."
                    className="w-full p-4 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none"
                    rows={4}
                  />
                )}
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between">
                <button
                  onClick={handlePrevious}
                  disabled={currentStep === 0}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
                    currentStep === 0
                      ? 'bg-gray-600/20 text-gray-500 cursor-not-allowed'
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                  }`}
                >
                  <ArrowLeft className="w-4 h-4" />
                  Previous
                </button>

                <div className="flex items-center gap-2 text-gray-400">
                  {questions.map((_, index) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full transition-all ${
                        index === currentStep
                          ? 'bg-blue-400 w-8'
                          : index < currentStep
                          ? 'bg-green-400'
                          : 'bg-gray-600'
                      }`}
                    />
                  ))}
                </div>

                <button
                  onClick={handleNext}
                  disabled={!responses[currentQuestion.id] || submitting}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
                    !responses[currentQuestion.id] || submitting
                      ? 'bg-gray-600/20 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600'
                  }`}
                >
                  {submitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      Completing...
                    </>
                  ) : currentStep === questions.length - 1 ? (
                    <>
                      Complete Assessment
                      <CheckCircle className="w-4 h-4" />
                    </>
                  ) : (
                    <>
                      Next
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Assessment Info */}
        <div className="max-w-4xl mx-auto mt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-black/10 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
              <Brain className="w-8 h-8 text-blue-400 mx-auto mb-2" />
              <h3 className="text-white font-medium mb-1">Adaptive</h3>
              <p className="text-gray-400 text-sm">Questions adapt to your responses</p>
            </div>
            
            <div className="bg-black/10 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
              <BookOpen className="w-8 h-8 text-green-400 mx-auto mb-2" />
              <h3 className="text-white font-medium mb-1">Comprehensive</h3>
              <p className="text-gray-400 text-sm">Covers all M&A knowledge areas</p>
            </div>
            
            <div className="bg-black/10 backdrop-blur-md rounded-lg p-4 border border-white/10 text-center">
              <TrendingUp className="w-8 h-8 text-purple-400 mx-auto mb-2" />
              <h3 className="text-white font-medium mb-1">Personalized</h3>
              <p className="text-gray-400 text-sm">Creates your custom learning path</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
