'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, 
  User, 
  TrendingUp, 
  Award, 
  Clock,
  BookOpen,
  Target,
  BarChart3,
  Calendar,
  Edit3,
  Save,
  X
} from 'lucide-react'
import { UserProfile as UserProfileType } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface UserProfileProps {
  userProfile: UserProfileType
  onBack: () => void
  onProfileUpdate: (profile: UserProfileType) => void
}

interface LearningStats {
  total_sessions: number
  total_time_minutes: number
  concepts_mastered: number
  assessments_completed: number
  scenarios_completed: number
  current_streak: number
  last_activity: string
}

export const UserProfile: React.FC<UserProfileProps> = ({
  userProfile,
  onBack,
  onProfileUpdate
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedProfile, setEditedProfile] = useState<UserProfileType>(userProfile)
  const [learningStats, setLearningStats] = useState<LearningStats>({
    total_sessions: 0,
    total_time_minutes: 0,
    concepts_mastered: 0,
    assessments_completed: 0,
    scenarios_completed: 0,
    current_streak: 0,
    last_activity: 'Never'
  })

  useEffect(() => {
    loadLearningStats()
  }, [])

  const loadLearningStats = () => {
    // Mock learning statistics - in real implementation, this would come from backend
    const mockStats: LearningStats = {
      total_sessions: Math.floor(Math.random() * 20) + 5,
      total_time_minutes: Math.floor(Math.random() * 300) + 60,
      concepts_mastered: userProfile.known_concepts.length,
      assessments_completed: userProfile.assessment_history.length,
      scenarios_completed: Math.floor(Math.random() * 5) + 1,
      current_streak: Math.floor(Math.random() * 7) + 1,
      last_activity: new Date().toLocaleDateString()
    }
    setLearningStats(mockStats)
  }

  const handleSaveProfile = () => {
    // Validate required fields
    if (!editedProfile.name.trim()) {
      toast.error('Name is required')
      return
    }

    // Update profile
    onProfileUpdate(editedProfile)
    localStorage.setItem('ai-teach-profile', JSON.stringify(editedProfile))
    
    setIsEditing(false)
    toast.success('Profile updated successfully!')
  }

  const handleCancelEdit = () => {
    setEditedProfile(userProfile)
    setIsEditing(false)
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'text-green-400 bg-green-500/20'
      case 'intermediate': return 'text-yellow-400 bg-yellow-500/20'
      case 'expert': return 'text-red-400 bg-red-500/20'
      default: return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getProgressPercentage = () => {
    const totalConcepts = 50 // Mock total available concepts
    return Math.min((userProfile.known_concepts.length / totalConcepts) * 100, 100)
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
            <h1 className="text-3xl font-bold text-white mb-2">User Profile</h1>
            <p className="text-gray-300">Track your learning progress and achievements</p>
          </div>
          
          <button
            onClick={() => setIsEditing(!isEditing)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              isEditing 
                ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30' 
                : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'
            }`}
          >
            {isEditing ? <X className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
            {isEditing ? 'Cancel' : 'Edit Profile'}
          </button>
        </div>

        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Profile Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <div className="flex items-start gap-6">
                <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <User className="w-10 h-10 text-white" />
                </div>
                
                <div className="flex-1">
                  {isEditing ? (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-white font-medium mb-2">Name</label>
                        <input
                          type="text"
                          value={editedProfile.name}
                          onChange={(e) => setEditedProfile({...editedProfile, name: e.target.value})}
                          className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-white font-medium mb-2">Background</label>
                        <textarea
                          value={editedProfile.background}
                          onChange={(e) => setEditedProfile({...editedProfile, background: e.target.value})}
                          rows={3}
                          className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-white font-medium mb-2">Learning Goals</label>
                        <textarea
                          value={editedProfile.learning_goals.join('\n')}
                          onChange={(e) => setEditedProfile({
                            ...editedProfile, 
                            learning_goals: e.target.value.split('\n').filter(goal => goal.trim())
                          })}
                          rows={3}
                          placeholder="Enter each goal on a new line"
                          className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none"
                        />
                      </div>
                      
                      <div className="flex gap-3">
                        <button
                          onClick={handleSaveProfile}
                          className="flex items-center gap-2 bg-green-500/20 text-green-300 px-4 py-2 rounded-lg hover:bg-green-500/30 transition-all"
                        >
                          <Save className="w-4 h-4" />
                          Save Changes
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="flex items-center gap-2 bg-gray-500/20 text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-500/30 transition-all"
                        >
                          <X className="w-4 h-4" />
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">{userProfile.name}</h2>
                      <div className="flex items-center gap-3 mb-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getLevelColor(userProfile.current_level)}`}>
                          {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}
                        </span>
                        <span className="text-gray-400 text-sm">
                          Member since {new Date(userProfile.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      
                      <div className="mb-4">
                        <h3 className="text-white font-medium mb-2">Background:</h3>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {userProfile.background || 'No background information provided.'}
                        </p>
                      </div>
                      
                      <div>
                        <h3 className="text-white font-medium mb-2">Learning Goals:</h3>
                        {userProfile.learning_goals.length > 0 ? (
                          <ul className="space-y-1">
                            {userProfile.learning_goals.map((goal, index) => (
                              <li key={index} className="flex items-center gap-2 text-gray-300 text-sm">
                                <Target className="w-3 h-3 text-blue-400" />
                                {goal}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-gray-400 text-sm">No learning goals set.</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Learning Progress */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                Learning Progress
              </h3>
              
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-300">Overall Progress</span>
                  <span className="text-white font-medium">{Math.round(getProgressPercentage())}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-green-500 to-blue-500 h-3 rounded-full transition-all duration-1000"
                    style={{ width: `${getProgressPercentage()}%` }}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{userProfile.known_concepts.length}</div>
                  <div className="text-gray-300 text-sm">Concepts Known</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{userProfile.assessment_history.length}</div>
                  <div className="text-gray-300 text-sm">Assessments</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400">{learningStats.total_sessions}</div>
                  <div className="text-gray-300 text-sm">Sessions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-400">{Math.floor(learningStats.total_time_minutes / 60)}h</div>
                  <div className="text-gray-300 text-sm">Study Time</div>
                </div>
              </div>
            </div>

            {/* Assessment History */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                Assessment History
              </h3>
              
              {userProfile.assessment_history.length > 0 ? (
                <div className="space-y-3">
                  {userProfile.assessment_history.slice(-5).map((assessment, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center">
                          <BookOpen className="w-4 h-4 text-purple-400" />
                        </div>
                        <div>
                          <div className="text-white font-medium">Assessment #{index + 1}</div>
                          <div className="text-gray-400 text-sm">
                            {new Date(assessment.timestamp).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-medium">{assessment.score}%</div>
                        <div className={`text-sm ${
                          assessment.level === 'beginner' ? 'text-green-400' :
                          assessment.level === 'intermediate' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {assessment.level}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-400">No assessments completed yet</p>
                  <p className="text-gray-500 text-sm">Take your first assessment to get started!</p>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar Stats */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-400" />
                Quick Stats
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Current Streak</span>
                  <span className="text-orange-400 font-bold">{learningStats.current_streak} days</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Scenarios Completed</span>
                  <span className="text-green-400 font-bold">{learningStats.scenarios_completed}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Last Activity</span>
                  <span className="text-blue-400 font-bold">{learningStats.last_activity}</span>
                </div>
              </div>
            </div>

            {/* Achievements */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-yellow-400" />
                Achievements
              </h3>
              
              <div className="space-y-3">
                {userProfile.known_concepts.length >= 5 && (
                  <div className="flex items-center gap-3 p-3 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                    <Award className="w-6 h-6 text-yellow-400" />
                    <div>
                      <div className="text-white font-medium">Quick Learner</div>
                      <div className="text-yellow-300 text-sm">Learned 5+ concepts</div>
                    </div>
                  </div>
                )}
                
                {userProfile.assessment_history.length >= 3 && (
                  <div className="flex items-center gap-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                    <Target className="w-6 h-6 text-blue-400" />
                    <div>
                      <div className="text-white font-medium">Assessment Pro</div>
                      <div className="text-blue-300 text-sm">Completed 3+ assessments</div>
                    </div>
                  </div>
                )}
                
                {learningStats.current_streak >= 7 && (
                  <div className="flex items-center gap-3 p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                    <Calendar className="w-6 h-6 text-green-400" />
                    <div>
                      <div className="text-white font-medium">Consistent Learner</div>
                      <div className="text-green-300 text-sm">7+ day streak</div>
                    </div>
                  </div>
                )}
                
                {(userProfile.known_concepts.length < 5 && userProfile.assessment_history.length < 3 && learningStats.current_streak < 7) && (
                  <div className="text-center py-6">
                    <Award className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-gray-400">No achievements yet</p>
                    <p className="text-gray-500 text-sm">Keep learning to unlock achievements!</p>
                  </div>
                )}
              </div>
            </div>

            {/* Activity Summary */}
            <div className="bg-black/20 backdrop-blur-md rounded-xl p-6 border border-white/10">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-400" />
                Activity Summary
              </h3>
              
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Study Time</span>
                  <span className="text-white">{Math.floor(learningStats.total_time_minutes / 60)}h {learningStats.total_time_minutes % 60}m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Average Session</span>
                  <span className="text-white">{Math.round(learningStats.total_time_minutes / Math.max(learningStats.total_sessions, 1))}m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Concepts per Session</span>
                  <span className="text-white">{(userProfile.known_concepts.length / Math.max(learningStats.total_sessions, 1)).toFixed(1)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
