'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, GraduationCap, User, Bot, Loader2 } from 'lucide-react'
import { apiService } from '@/services/api'
import toast from 'react-hot-toast'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export function EducationChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI tutor for M&A and business deals. Ask me anything about mergers, acquisitions, partnerships, or any deal you'd like to understand better. I can explain concepts at beginner, intermediate, or expert levels.",
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [expertiseLevel, setExpertiseLevel] = useState<'beginner' | 'intermediate' | 'expert'>('intermediate')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await apiService.getEducationResponse({
        query: input,
        expertise_level: expertiseLevel,
        context: 'M&A education chat'
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Education chat error:', error)
      toast.error('Failed to get response')
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm sorry, I'm having trouble responding right now. Please try again later.",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const quickQuestions = [
    "What is the difference between a merger and an acquisition?",
    "How do companies value each other in M&A deals?",
    "What are the main reasons companies merge?",
    "Explain due diligence in simple terms",
    "What are synergies in M&A?",
    "How do hostile takeovers work?"
  ]

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
          <GraduationCap className="text-blue-500" />
          Education Mode
        </h1>
        <p className="text-gray-600">
          Learn about M&A deals, business concepts, and market dynamics with AI-powered explanations
        </p>
      </div>

      {/* Expertise Level Selector */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Expertise Level
        </label>
        <div className="flex gap-2">
          {(['beginner', 'intermediate', 'expert'] as const).map((level) => (
            <button
              key={level}
              onClick={() => setExpertiseLevel(level)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                expertiseLevel === level
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Quick Questions */}
      {messages.length === 1 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Questions to Get Started:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-md text-sm transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Bot size={16} className="text-blue-600" />
                </div>
              )}
              
              <div
                className={`max-w-[70%] p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className={`text-xs mt-1 ${
                  message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <User size={16} className="text-gray-600" />
                </div>
              )}
            </div>
          ))}
          
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Bot size={16} className="text-blue-600" />
              </div>
              <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin" />
                  Thinking...
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about M&A deals, business concepts, or specific companies..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={16} />
            </button>
          </div>
          <div className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  )
}
