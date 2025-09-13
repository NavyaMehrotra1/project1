'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Brain, 
  MessageCircle, 
  TrendingUp,
  TrendingDown,
  User,
  Bot,
  Lightbulb,
  Target,
  BarChart3
} from 'lucide-react'
import { aiTeachService, UserProfile, InteractionSignal } from '@/services/ai-teach-service'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: string
  concept?: string
  level_used?: string
}

interface ConversationalLearningProps {
  onProfileUpdate?: (profile: UserProfile) => void
}

export const ConversationalLearning: React.FC<ConversationalLearningProps> = ({
  onProfileUpdate
}) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [sessionStarted, setSessionStarted] = useState(false)

  useEffect(() => {
    initializeProfile()
  }, [])

  const initializeProfile = () => {
    // Try to load existing profile or create default
    const savedProfile = localStorage.getItem('ai-teach-profile')
    let profile: UserProfile
    
    if (savedProfile) {
      profile = JSON.parse(savedProfile)
    } else {
      profile = aiTeachService.createDefaultProfile(`user_${Date.now()}`)
      localStorage.setItem('ai-teach-profile', JSON.stringify(profile))
    }
    
    setUserProfile(profile)
    
    // Welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'ai',
      content: `Hi! I'm your AI M&A teacher. I'll adapt to your knowledge level as we chat. Feel free to ask me anything about mergers, acquisitions, or corporate finance. What would you like to learn about?`,
      timestamp: new Date().toISOString(),
      level_used: profile.current_level
    }
    
    setMessages([welcomeMessage])
    setSessionStarted(true)
  }

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || !userProfile) return

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsTyping(true)

    try {
      // Analyze user input for level signals
      const signals = aiTeachService.analyzeUserInput(currentMessage, 'conversational_learning')
      
      // Update user profile based on signals
      let updatedProfile = userProfile
      if (signals.length > 0) {
        updatedProfile = aiTeachService.updateUserLevel(userProfile, signals)
        setUserProfile(updatedProfile)
        localStorage.setItem('ai-teach-profile', JSON.stringify(updatedProfile))
        onProfileUpdate?.(updatedProfile)
        
        // Show level adjustment feedback
        if (updatedProfile.current_level !== userProfile.current_level) {
          toast.success(`Adjusted to ${updatedProfile.current_level} level based on your question`)
        }
      }

      // Generate AI response based on current level
      const aiResponse = await generateAIResponse(currentMessage, updatedProfile)
      
      const aiMessage: Message = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toISOString(),
        level_used: updatedProfile.current_level
      }

      setMessages(prev => [...prev, aiMessage])
      
    } catch (error) {
      console.error('Error processing message:', error)
      toast.error('Failed to process your question')
    } finally {
      setIsTyping(false)
    }
  }

  const generateAIResponse = async (question: string, profile: UserProfile): Promise<string> => {
    // Mock AI response generation based on level
    const level = profile.current_level
    const confidence = profile.level_confidence
    
    // Detect M&A concepts in the question
    const concepts = detectConcepts(question)
    
    if (concepts.length === 0) {
      return generateGeneralResponse(question, level)
    }
    
    return generateConceptResponse(concepts[0], question, level, confidence)
  }

  const detectConcepts = (question: string): string[] => {
    const conceptKeywords = {
      'merger': ['merger', 'merge', 'combining companies'],
      'acquisition': ['acquisition', 'acquire', 'buying company', 'takeover'],
      'valuation': ['valuation', 'value', 'worth', 'price', 'dcf'],
      'due_diligence': ['due diligence', 'dd', 'investigation', 'audit'],
      'synergy': ['synergy', 'synergies', 'cost savings', 'revenue enhancement'],
      'integration': ['integration', 'combine operations', 'merge systems']
    }
    
    const detected: string[] = []
    const lowerQuestion = question.toLowerCase()
    
    Object.entries(conceptKeywords).forEach(([concept, keywords]) => {
      if (keywords.some(keyword => lowerQuestion.includes(keyword))) {
        detected.push(concept)
      }
    })
    
    return detected
  }

  const generateConceptResponse = (concept: string, question: string, level: string, confidence: number): string => {
    const responses = {
      merger: {
        beginner: "A merger is when two companies decide to join together and become one new company. Think of it like two friends deciding to combine their lemonade stands into one bigger stand. Both companies agree to work together as equals.",
        intermediate: "A merger is a strategic combination where two companies of roughly equal size combine their operations to form a new entity. This typically involves share exchanges and requires approval from both sets of shareholders. The goal is usually to achieve synergies and competitive advantages.",
        expert: "Mergers involve complex structural considerations including share exchange ratios, governance structures, regulatory approvals, and integration planning. Key valuation methodologies include comparable company analysis, precedent transactions, and DCF models to determine fair exchange ratios."
      },
      acquisition: {
        beginner: "An acquisition is when one company buys another company. It's like when a big store buys a smaller store. The bigger company becomes the owner and makes the decisions.",
        intermediate: "An acquisition occurs when one company (the acquirer) purchases most or all of another company's (target) shares to gain control. This can be done through cash, stock, or a combination. The target company typically ceases to exist as an independent entity.",
        expert: "Acquisitions involve strategic and financial considerations including target identification, valuation analysis, deal structuring (asset vs. stock purchase), tax implications, financing arrangements, and post-acquisition integration planning. Due diligence is critical for risk assessment."
      },
      valuation: {
        beginner: "Valuation is figuring out how much a company is worth. It's like getting your house appraised - you look at similar houses and what they sold for to estimate the value.",
        intermediate: "Company valuation uses multiple methodologies: comparable company analysis (trading multiples), precedent transaction analysis, and discounted cash flow (DCF) models. Each method provides different perspectives on fair value.",
        expert: "Valuation in M&A requires sophisticated modeling including DCF analysis with terminal value calculations, sum-of-the-parts analysis for conglomerates, and control premium adjustments. Consider synergies, integration costs, and market conditions in final valuations."
      }
    }
    
    const conceptResponses = responses[concept as keyof typeof responses]
    if (!conceptResponses) {
      return `That's a great question about ${concept}. Let me explain based on your current level...`
    }
    
    let response = conceptResponses[level as keyof typeof conceptResponses] || conceptResponses.intermediate
    
    // Add confidence-based adjustments
    if (confidence < 0.5) {
      response += "\n\nI'm still learning about your knowledge level, so let me know if this explanation is too simple or complex!"
    }
    
    return response
  }

  const generateGeneralResponse = (question: string, level: string): string => {
    const generalResponses = [
      "That's an interesting question! Could you be more specific about which aspect of M&A you'd like to explore?",
      "I'd be happy to help with that. Are you thinking about this from a strategic, financial, or operational perspective?",
      "Great question! Let me know if you want me to focus on the basics or dive into more technical details."
    ]
    
    return generalResponses[Math.floor(Math.random() * generalResponses.length)]
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner': return 'text-green-400'
      case 'intermediate': return 'text-yellow-400'
      case 'expert': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!sessionStarted || !userProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white text-lg">Starting AI Teacher...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="relative z-10 h-screen flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">AI M&A Teacher</h1>
                <p className="text-gray-300">Conversational Learning</p>
              </div>
            </div>
            
            {/* Level Indicator */}
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-white font-medium">Current Level</div>
                <div className={`text-sm ${getLevelColor(userProfile.current_level)}`}>
                  {userProfile.current_level.charAt(0).toUpperCase() + userProfile.current_level.slice(1)}
                </div>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">Confidence</div>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-white/20 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${userProfile.level_confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-300 text-sm">{Math.round(userProfile.level_confidence * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.type === 'ai' && (
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-purple-400" />
                  </div>
                )}
                
                <div className={`max-w-2xl rounded-xl p-4 ${
                  message.type === 'user' 
                    ? 'bg-blue-500/20 text-blue-100 border border-blue-500/30' 
                    : 'bg-black/20 text-white border border-white/10'
                }`}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  {message.level_used && message.type === 'ai' && (
                    <div className="mt-2 pt-2 border-t border-white/10">
                      <span className={`text-xs ${getLevelColor(message.level_used)}`}>
                        Explained at {message.level_used} level
                      </span>
                    </div>
                  )}
                </div>

                {message.type === 'user' && (
                  <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-blue-400" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-purple-400" />
              </div>
              <div className="bg-black/20 rounded-xl p-4 border border-white/10">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-white/10">
          <div className="flex gap-3">
            <textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about M&A... (I'll adapt to your level as we chat)"
              className="flex-1 p-4 bg-black/20 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:border-blue-500/50 focus:outline-none resize-none"
              rows={2}
              disabled={isTyping}
            />
            <button
              onClick={handleSendMessage}
              disabled={!currentMessage.trim() || isTyping}
              className={`px-6 py-4 rounded-xl transition-all flex items-center gap-2 ${
                currentMessage.trim() && !isTyping
                  ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600'
                  : 'bg-gray-600/20 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
          
          {/* Quick Suggestions */}
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              "What's the difference between a merger and acquisition?",
              "How do you value a company?",
              "What is due diligence?",
              "Can you explain this more simply?",
              "Tell me more technical details"
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setCurrentMessage(suggestion)}
                className="px-3 py-1 bg-white/10 text-gray-300 rounded-full text-sm hover:bg-white/20 transition-all"
                disabled={isTyping}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
