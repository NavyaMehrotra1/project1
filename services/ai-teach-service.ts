/**
 * AI-Teach Service
 * Handles communication with AI-Teach backend API
 */

import { apiService } from './api'

export interface AssessmentQuestion {
  id: string
  question: string
  question_type: 'multiple_choice' | 'true_false' | 'open_ended'
  options?: string[]
  correct_answer?: string
  difficulty_level: number
  concept_area: string
  points: number
}

export interface UserProfile {
  user_id: string
  name: string
  background: string
  current_level: 'beginner' | 'intermediate' | 'expert'
  level_confidence: number // 0-1, how confident we are about the level
  background_assessment_score?: number // Optional now
  known_concepts: string[]
  learning_gaps: string[]
  learning_goals: string[]
  finance_background?: boolean
  business_background?: boolean
  previous_ma_experience?: boolean
  session_history: ConversationSession[]
  assessment_history: AssessmentResult[]
  interaction_signals: InteractionSignal[]
  created_at: string
  last_updated: string
}

export interface ConversationSession {
  session_id: string
  timestamp: string
  questions_asked: number
  concepts_discussed: string[]
  level_adjustments: LevelAdjustment[]
  duration_minutes: number
}

export interface InteractionSignal {
  timestamp: string
  signal_type: 'confusion' | 'understanding' | 'advanced_question' | 'basic_question' | 'request_simpler' | 'request_deeper'
  context: string
  concept?: string
  level_impact: number // -1 to 1, negative for confusion, positive for understanding
}

export interface LevelAdjustment {
  timestamp: string
  previous_level: string
  new_level: string
  reason: string
  confidence_change: number
}

export interface AssessmentResult {
  timestamp: string
  score: number
  level: string
  questions_answered: number
  time_taken: number
}

export interface LearningConcept {
  id: string
  name: string
  description: string
  difficulty_level: number
  prerequisites: string[]
  examples: string[]
  learning_objectives: string[]
  ma_context?: string
  real_world_examples: string[]
}

export interface ScenarioData {
  scenario_id: string
  title: string
  description: string
  companies_involved: string[]
  deal_type: string
  deal_value?: number
  industry: string
  complexity_level: number
  learning_objectives: string[]
  key_concepts: string[]
  discussion_points: string[]
}

export interface ExplanationRequest {
  user_id: string
  question: string
  context?: string
  user_level: 'beginner' | 'intermediate' | 'expert'
  preferred_style?: string
  graph_data?: any
}

export interface ExplanationResponse {
  explanation: string
  user_level: string
  confidence: number
  follow_up_topics: string[]
  prerequisite_check: boolean
  error?: string
}

class AITeachService {
  private baseUrl = '/api/ai-teach'

  async startAssessment(userId: string): Promise<AssessmentQuestion[]> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to start assessment')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error starting assessment:', error)
      throw error
    }
  }

  async submitAssessmentResponse(
    userId: string,
    questionId: string,
    response: string
  ): Promise<{ next_question?: AssessmentQuestion; completed?: boolean }> {
    try {
      const res = await fetch(`${this.baseUrl}/assessment/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          question_id: questionId,
          response: response,
        }),
      })
      
      if (!res.ok) {
        throw new Error('Failed to submit response')
      }
      
      return await res.json()
    } catch (error) {
      console.error('Error submitting response:', error)
      throw error
    }
  }

  async completeAssessment(userId: string, responses: any[]): Promise<UserProfile> {
    try {
      const response = await fetch(`${this.baseUrl}/assessment/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          responses: responses,
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to complete assessment')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error completing assessment:', error)
      throw error
    }
  }

  async startLearningSession(userId: string): Promise<{ session_id: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/learning/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to start learning session')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error starting learning session:', error)
      throw error
    }
  }

  async getNextConcept(sessionId: string): Promise<LearningConcept | null> {
    try {
      const response = await fetch(`${this.baseUrl}/learning/next-concept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to get next concept')
      }
      
      const data = await response.json()
      return data.concept || null
    } catch (error) {
      console.error('Error getting next concept:', error)
      throw error
    }
  }

  async explainConcept(request: ExplanationRequest): Promise<ExplanationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })
      
      if (!response.ok) {
        throw new Error('Failed to get explanation')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting explanation:', error)
      throw error
    }
  }

  async getCaseStudies(userLevel: string): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/case-studies?level=${userLevel}`)
      
      if (!response.ok) {
        throw new Error('Failed to get case studies')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting case studies:', error)
      throw error
    }
  }

  async getScenarios(userLevel: string): Promise<ScenarioData[]> {
    try {
      const response = await fetch(`${this.baseUrl}/scenarios?level=${userLevel}`)
      
      if (!response.ok) {
        throw new Error('Failed to get scenarios')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting scenarios:', error)
      throw error
    }
  }

  async runScenarioSimulation(
    scenarioId: string,
    userInputs: Record<string, any>,
    userId: string
  ): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/scenarios/simulate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_id: scenarioId,
          user_inputs: userInputs,
          user_id: userId,
        }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to run simulation')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error running simulation:', error)
      throw error
    }
  }

  async getUserProfile(userId: string): Promise<UserProfile | null> {
    try {
      const response = await fetch(`${this.baseUrl}/profile/${userId}`)
      
      if (!response.ok) {
        if (response.status === 404) {
          return null // No profile found
        }
        throw new Error('Failed to get user profile')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting user profile:', error)
      throw error
    }
  }

  async updateUserProfile(userId: string, updates: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await fetch(`${this.baseUrl}/profile/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      })
      
      if (!response.ok) {
        throw new Error('Failed to update user profile')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error updating user profile:', error)
      throw error
    }
  }

  // Create a default user profile for immediate Q&A
  createDefaultProfile(userId: string): UserProfile {
    return {
      user_id: userId,
      name: 'New Learner',
      background: 'Starting M&A learning journey',
      current_level: 'beginner', // Start with beginner, will adapt
      level_confidence: 0.3, // Low confidence initially
      known_concepts: [],
      learning_gaps: [],
      learning_goals: [],
      session_history: [],
      assessment_history: [],
      interaction_signals: [],
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString()
    }
  }

  // Analyze user input for level signals
  analyzeUserInput(input: string, context: string): InteractionSignal[] {
    const signals: InteractionSignal[] = []
    const timestamp = new Date().toISOString()
    
    // Confusion signals
    if (input.toLowerCase().includes('i don\'t understand') || 
        input.toLowerCase().includes('confused') ||
        input.toLowerCase().includes('what does that mean') ||
        input.toLowerCase().includes('can you explain')) {
      signals.push({
        timestamp,
        signal_type: 'confusion',
        context: input,
        level_impact: -0.2
      })
    }
    
    // Request for simpler explanation
    if (input.toLowerCase().includes('simpler') ||
        input.toLowerCase().includes('basic') ||
        input.toLowerCase().includes('eli5') ||
        input.toLowerCase().includes('explain like')) {
      signals.push({
        timestamp,
        signal_type: 'request_simpler',
        context: input,
        level_impact: -0.3
      })
    }
    
    // Advanced questions
    if (input.toLowerCase().includes('dcf') ||
        input.toLowerCase().includes('ebitda multiple') ||
        input.toLowerCase().includes('synergy valuation') ||
        input.toLowerCase().includes('accretion') ||
        input.toLowerCase().includes('dilution')) {
      signals.push({
        timestamp,
        signal_type: 'advanced_question',
        context: input,
        level_impact: 0.4
      })
    }
    
    // Request for deeper explanation
    if (input.toLowerCase().includes('more detail') ||
        input.toLowerCase().includes('deeper') ||
        input.toLowerCase().includes('technical') ||
        input.toLowerCase().includes('how exactly')) {
      signals.push({
        timestamp,
        signal_type: 'request_deeper',
        context: input,
        level_impact: 0.2
      })
    }
    
    return signals
  }

  // Update user level based on interaction signals
  updateUserLevel(profile: UserProfile, signals: InteractionSignal[]): UserProfile {
    if (signals.length === 0) return profile
    
    let levelImpact = 0
    signals.forEach(signal => {
      levelImpact += signal.level_impact
    })
    
    // Update confidence and potentially level
    const newConfidence = Math.max(0.1, Math.min(1.0, profile.level_confidence + (Math.abs(levelImpact) * 0.1)))
    
    let newLevel = profile.current_level
    const levelOrder = ['beginner', 'intermediate', 'expert']
    const currentIndex = levelOrder.indexOf(profile.current_level)
    
    // Significant negative impact - move to simpler level
    if (levelImpact < -0.4 && currentIndex > 0 && profile.level_confidence > 0.6) {
      newLevel = levelOrder[currentIndex - 1] as 'beginner' | 'intermediate' | 'expert'
    }
    
    // Significant positive impact - move to advanced level
    if (levelImpact > 0.5 && currentIndex < 2 && profile.level_confidence > 0.7) {
      newLevel = levelOrder[currentIndex + 1] as 'beginner' | 'intermediate' | 'expert'
    }
    
    return {
      ...profile,
      current_level: newLevel,
      level_confidence: newConfidence,
      interaction_signals: [...profile.interaction_signals, ...signals],
      last_updated: new Date().toISOString()
    }
  }

  // Mock implementations for development (remove when backend is ready)
  async mockStartAssessment(userId: string): Promise<AssessmentQuestion[]> {
    return [
      {
        id: 'basic_1',
        question: 'What is the primary difference between a merger and an acquisition?',
        question_type: 'multiple_choice',
        options: [
          'There is no difference - they\'re the same thing',
          'In a merger, companies combine as equals; in acquisition, one buys another',
          'Mergers are always hostile; acquisitions are friendly',
          'Mergers involve cash; acquisitions involve stock'
        ],
        correct_answer: 'In a merger, companies combine as equals; in acquisition, one buys another',
        difficulty_level: 1,
        concept_area: 'basic_concepts',
        points: 1
      },
      {
        id: 'basic_2',
        question: 'What does "due diligence" mean in M&A?',
        question_type: 'multiple_choice',
        options: [
          'The legal requirement to announce deals publicly',
          'The process of investigating a company before buying it',
          'The duty of directors to shareholders',
          'The timeline for completing a transaction'
        ],
        correct_answer: 'The process of investigating a company before buying it',
        difficulty_level: 1,
        concept_area: 'process',
        points: 1
      }
    ]
  }

  async mockCompleteAssessment(userId: string, responses: any[]): Promise<UserProfile> {
    // Calculate score based on responses
    const score = Math.random() * 40 + 60 // Mock score between 60-100
    
    let level: 'beginner' | 'intermediate' | 'expert' = 'beginner'
    if (score > 80) level = 'expert'
    else if (score > 70) level = 'intermediate'
    
    return {
      user_id: userId,
      name: 'AI-Teach User',
      background: 'Learning M&A fundamentals through AI-powered adaptive education',
      current_level: level,
      level_confidence: 0.7, // Moderate confidence from assessment
      background_assessment_score: score,
      known_concepts: ['merger_vs_acquisition', 'due_diligence'],
      learning_gaps: ['valuation', 'synergies'],
      learning_goals: ['Master M&A fundamentals', 'Understand deal structures', 'Learn valuation methods'],
      finance_background: Math.random() > 0.5,
      business_background: Math.random() > 0.3,
      previous_ma_experience: Math.random() > 0.7,
      session_history: [],
      assessment_history: [{
        timestamp: new Date().toISOString(),
        score: Math.round(score),
        level: level,
        questions_answered: 10,
        time_taken: 300
      }],
      interaction_signals: [],
      created_at: new Date().toISOString(),
      last_updated: new Date().toISOString()
    }
  }
}

export const aiTeachService = new AITeachService()
