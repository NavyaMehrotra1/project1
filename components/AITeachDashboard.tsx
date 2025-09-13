'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Brain, 
  BookOpen, 
  Target, 
  Users, 
  BarChart3,
  User,
  ArrowRight,
  Play,
  CheckCircle,
  Clock,
  TrendingUp,
  MessageCircle,
  GraduationCap,
  Lightbulb,
  Award
} from 'lucide-react'
import { ConversationalLearning } from './ConversationalLearning'
import { aiTeachService, UserProfile } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface UserProfileData {
  user_id: string
  current_level: 'beginner' | 'intermediate' | 'expert'
  background_assessment_score: number
  known_concepts: string[]
  learning_gaps: string[]
  finance_background: boolean
  business_background: boolean
  previous_ma_experience: boolean
  session_history: any[]
  created_at: string
}

export const AITeachDashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<'dashboard' | 'assessment' | 'chat'>('dashboard')
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Check if user has existing profile
    const savedProfile = localStorage.getItem('ai-teach-profile')
    if (savedProfile) {
      setUserProfile(JSON.parse(savedProfile))
    }
  }, [])

  const handleStartAssessment = () => {
    setActiveView('assessment')
  }

  const handleStartChat = () => {
    setActiveView('chat')
  }

  const handleAssessmentComplete = (profile: UserProfile) => {
    setUserProfile(profile)
    localStorage.setItem('ai-teach-profile', JSON.stringify(profile))
    toast.success('Assessment completed! Your learning profile has been created.')
    setActiveView('dashboard')
  }

  const renderDashboard = () => (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 p-6">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center gap-3 mb-4"
          >
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">AI Teacher</h1>
          </motion.div>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-gray-300 text-lg max-w-2xl mx-auto"
          >
            Master M&A concepts with personalized AI-powered learning
          </motion.p>
        </div>

        {/* User Status */}
        {userProfile && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-black/20 backdrop-blur-md rounded-xl p-6 mb-8 border border-white/10 max-w-4xl mx-auto"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-semibold">Welcome back, {userProfile.user_id}!</h3>
                  <p className="text-gray-300 text-sm">
                    Level: {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)} • 
                    Confidence: {Math.round((userProfile.level_confidence || 0) * 100)}%
                  </p>
                  <p className="text-white/80 text-sm">
                    Assessment Score: {userProfile.background_assessment_score || 'Not taken'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setActiveView('chat')}
                className="text-blue-300 hover:text-blue-200 transition-colors"
              >
                Continue Learning
              </button>
            </div>
          </motion.div>
        )}

        {/* Main Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-12">
          {/* Start Chat Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.02 }}
            className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-green-500/30 transition-all cursor-pointer"
            onClick={handleStartChat}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-500 rounded-lg flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-white text-xl font-semibold">Start Learning Chat</h3>
            </div>
            <p className="text-gray-300 mb-4">
              Ask M&A questions immediately! The AI will learn your level as you chat.
            </p>
            <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-3 mb-4">
              <p className="text-blue-200 text-sm">
                ✨ No assessment required - start asking questions right away!
              </p>
            </div>
            <button
              className="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white py-3 px-6 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2"
            >
              <MessageCircle className="w-4 h-4" />
              Start Chatting
            </button>
          </motion.div>

          {/* Assessment Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            whileHover={{ scale: 1.02 }}
            className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-blue-500/30 transition-all cursor-pointer"
            onClick={handleStartAssessment}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                <Target className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold">Background Assessment</h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              Determine your M&A knowledge level and create a personalized learning path
            </p>
            <div className="flex items-center justify-between">
              <span className="text-blue-300 text-sm">
                {userProfile ? 'Retake Assessment' : 'Start Assessment'}
              </span>
              <ArrowRight className="w-4 h-4 text-blue-400" />
            </div>
          </motion.div>

          {/* Learning Session Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            whileHover={{ scale: 1.02 }}
            className={`bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-green-500/30 transition-all cursor-pointer ${
              !userProfile ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={handleStartChat}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-white font-semibold">Learning Session</h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              Interactive M&A concepts with AI-powered explanations adapted to your level
            </p>
            <div className="flex items-center justify-between">
              <span className="text-green-300 text-sm">
                {userProfile ? 'Continue Learning' : 'Complete Assessment First'}
              </span>
              <Play className="w-4 h-4 text-green-400" />
            </div>
          </motion.div>

          {/* Concept Explorer Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.02 }}
            className={`bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-purple-500/30 transition-all cursor-pointer ${
              !userProfile ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={() => userProfile && setActiveView('chat')}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold">Concept Explorer</h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              Explore M&A terminology, case studies, and industry contexts
            </p>
            <div className="flex items-center justify-between">
              <span className="text-purple-300 text-sm">Explore Concepts</span>
              <Lightbulb className="w-4 h-4 text-purple-400" />
            </div>
          </motion.div>

          {/* Scenario Simulator Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.02 }}
            className={`bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10 hover:border-orange-500/30 transition-all cursor-pointer ${
              !userProfile ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={() => userProfile && setActiveView('chat')}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-orange-400" />
              </div>
              <h3 className="text-white font-semibold">Scenario Simulator</h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              Practice with interactive M&A scenarios and what-if simulations
            </p>
            <div className="flex items-center justify-between">
              <span className="text-orange-300 text-sm">Run Simulations</span>
              <Users className="w-4 h-4 text-orange-400" />
            </div>
          </motion.div>
        </div>

        {/* Features Overview */}
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            Why Choose AI-Teach?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Target className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Adaptive Learning</h3>
              <p className="text-gray-400 text-sm">
                Content automatically adjusts to your knowledge level and background
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Brain className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">AI-Powered</h3>
              <p className="text-gray-400 text-sm">
                Claude AI provides personalized explanations and educational feedback
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <CheckCircle className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Real Examples</h3>
              <p className="text-gray-400 text-sm">
                Learn from actual M&A deals and industry case studies
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-500/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Award className="w-6 h-6 text-orange-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Interactive</h3>
              <p className="text-gray-400 text-sm">
                Hands-on scenarios and simulations for experiential learning
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen">
      <AnimatePresence mode="wait">
        {activeView === 'dashboard' && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {renderDashboard()}
          </motion.div>
        )}
        
        {activeView === 'assessment' && (
          <motion.div
            key="assessment"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <BackgroundAssessment
              onComplete={handleAssessmentComplete}
              onBack={() => setActiveView('dashboard')}
            />
          </motion.div>
        )}
        
        {activeView === 'chat' && (
          <motion.div
            key="chat"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <ConversationalLearning />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
