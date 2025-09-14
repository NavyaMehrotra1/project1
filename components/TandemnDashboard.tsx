"use client"

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { 
  Activity, 
  Zap, 
  Eye, 
  Brain, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  Network,
  Cpu,
  Timer,
  Target,
  Layers
} from 'lucide-react'

interface ProcessingTask {
  id: string
  type: 'document' | 'confidence' | 'sentiment' | 'vision'
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  model: string
  startTime: number
  endTime?: number
  result?: any
}

interface PerformanceMetric {
  label: string
  withTandemn: number
  withoutTandemn: number
  unit: string
  improvement: number
}

const TandemnDashboard: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [tasks, setTasks] = useState<ProcessingTask[]>([])
  const [completedTasks, setCompletedTasks] = useState(0)
  const [totalProcessingTime, setTotalProcessingTime] = useState(0)
  const [currentDemo, setCurrentDemo] = useState<string | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Performance metrics for comparison
  const performanceMetrics: PerformanceMetric[] = [
    {
      label: "Document Processing Speed",
      withTandemn: 100,
      withoutTandemn: 10,
      unit: "docs/min",
      improvement: 900
    },
    {
      label: "Average Response Time", 
      withTandemn: 2.5,
      withoutTandemn: 15.0,
      unit: "seconds",
      improvement: 500
    },
    {
      label: "Parallel Processing Capacity",
      withTandemn: 50,
      withoutTandemn: 1,
      unit: "concurrent",
      improvement: 4900
    },
    {
      label: "Confidence Accuracy",
      withTandemn: 95,
      withoutTandemn: 78,
      unit: "%",
      improvement: 22
    }
  ]

  // Demo scenarios
  const demoScenarios = [
    {
      id: 'distributed-extraction',
      title: 'Distributed Document Extraction',
      description: 'Process 25 Microsoft-Activision articles in parallel',
      documents: 25,
      expectedTime: 30,
      models: ['GPT-4', 'Claude-3', 'GPT-3.5-turbo']
    },
    {
      id: 'confidence-fusion',
      title: 'Multi-Model Confidence Fusion',
      description: '4-perspective assessment of Apple-Tesla partnership rumors',
      documents: 5,
      expectedTime: 15,
      models: ['GPT-4 Financial', 'Claude-3 Legal', 'GPT-4 Market', 'GPT-3.5 Credibility']
    },
    {
      id: 'vision-analysis',
      title: 'Vision + Text Analysis',
      description: 'Extract deal data from investor presentation slides',
      documents: 8,
      expectedTime: 20,
      models: ['GPT-4 Vision', 'GPT-4 Text', 'Claude-3 Analysis']
    },
    {
      id: 'sentiment-orchestration',
      title: 'Real-Time Sentiment Orchestration',
      description: 'Analyze 500 social posts about Meta acquisition rumors',
      documents: 500,
      expectedTime: 45,
      models: ['GPT-3.5-turbo', 'GPT-4', 'Claude-3']
    }
  ]

  const startDemo = async (scenarioId: string) => {
    const scenario = demoScenarios.find(s => s.id === scenarioId)
    if (!scenario) return

    setCurrentDemo(scenarioId)
    setIsProcessing(true)
    setTasks([])
    setCompletedTasks(0)
    setTotalProcessingTime(0)

    // Create tasks for this scenario
    const newTasks: ProcessingTask[] = []
    
    for (let i = 0; i < scenario.documents; i++) {
      const taskTypes: ProcessingTask['type'][] = ['document', 'confidence', 'sentiment', 'vision']
      const randomType = taskTypes[Math.floor(Math.random() * taskTypes.length)]
      const randomModel = scenario.models[Math.floor(Math.random() * scenario.models.length)]
      
      newTasks.push({
        id: `task-${i}`,
        type: randomType,
        status: 'queued',
        progress: 0,
        model: randomModel,
        startTime: Date.now() + (i * 100) // Stagger start times
      })
    }

    setTasks(newTasks)

    // Simulate parallel processing
    const startTime = Date.now()
    
    intervalRef.current = setInterval(() => {
      setTasks(prevTasks => {
        const updatedTasks = prevTasks.map(task => {
          if (task.status === 'queued' && Date.now() >= task.startTime) {
            return { ...task, status: 'processing' as const }
          }
          
          if (task.status === 'processing') {
            const newProgress = Math.min(task.progress + Math.random() * 15, 100)
            
            if (newProgress >= 100) {
              return {
                ...task,
                status: 'completed' as const,
                progress: 100,
                endTime: Date.now(),
                result: generateMockResult(task.type)
              }
            }
            
            return { ...task, progress: newProgress }
          }
          
          return task
        })

        const completed = updatedTasks.filter(t => t.status === 'completed').length
        setCompletedTasks(completed)
        
        const currentTime = (Date.now() - startTime) / 1000
        setTotalProcessingTime(currentTime)

        // Stop when all tasks are completed
        if (completed === updatedTasks.length) {
          setIsProcessing(false)
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
          }
        }

        return updatedTasks
      })
    }, 200)
  }

  const generateMockResult = (type: ProcessingTask['type']) => {
    switch (type) {
      case 'document':
        return {
          events_extracted: Math.floor(Math.random() * 3) + 1,
          confidence: 0.85 + Math.random() * 0.1
        }
      case 'confidence':
        return {
          financial_confidence: 0.8 + Math.random() * 0.15,
          legal_confidence: 0.75 + Math.random() * 0.2,
          market_confidence: 0.82 + Math.random() * 0.13,
          credibility_confidence: 0.9 + Math.random() * 0.1
        }
      case 'sentiment':
        return {
          sentiment_score: (Math.random() - 0.5) * 2,
          market_impact: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)]
        }
      case 'vision':
        return {
          charts_processed: Math.floor(Math.random() * 5) + 1,
          data_points_extracted: Math.floor(Math.random() * 20) + 5
        }
      default:
        return {}
    }
  }

  const getTaskIcon = (type: ProcessingTask['type']) => {
    switch (type) {
      case 'document': return <Brain className="w-4 h-4" />
      case 'confidence': return <Target className="w-4 h-4" />
      case 'sentiment': return <TrendingUp className="w-4 h-4" />
      case 'vision': return <Eye className="w-4 h-4" />
    }
  }

  const getTaskColor = (type: ProcessingTask['type']) => {
    switch (type) {
      case 'document': return 'bg-blue-500'
      case 'confidence': return 'bg-green-500'
      case 'sentiment': return 'bg-purple-500'
      case 'vision': return 'bg-orange-500'
    }
  }

  const getStatusIcon = (status: ProcessingTask['status']) => {
    switch (status) {
      case 'queued': return <Clock className="w-4 h-4 text-gray-400" />
      case 'processing': return <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'failed': return <AlertCircle className="w-4 h-4 text-red-500" />
    }
  }

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-slate-50 to-blue-50 min-h-screen">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Tandemn Distributed AI Intelligence
        </h1>
        <p className="text-lg text-gray-600">
          Real-time M&A processing with distributed inference backend
        </p>
      </div>

      {/* Performance Comparison */}
      <Card className="border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Performance Impact: Before vs After Tandemn
          </CardTitle>
          <CardDescription>
            Quantifiable improvements with distributed inference
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {performanceMetrics.map((metric, index) => (
              <div key={index} className="bg-white p-4 rounded-lg border shadow-sm">
                <div className="text-sm font-medium text-gray-600 mb-2">
                  {metric.label}
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">Without Tandemn</span>
                    <span className="text-sm font-mono text-red-600">
                      {metric.withoutTandemn} {metric.unit}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">With Tandemn</span>
                    <span className="text-sm font-mono text-green-600 font-bold">
                      {metric.withTandemn} {metric.unit}
                    </span>
                  </div>
                  <div className="pt-2 border-t">
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      +{metric.improvement}% improvement
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Demo Scenarios */}
      <Card className="border-2 border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Interactive Demo Scenarios
          </CardTitle>
          <CardDescription>
            Click any scenario to see distributed processing in action
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {demoScenarios.map((scenario) => (
              <div
                key={scenario.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all ${
                  currentDemo === scenario.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
                onClick={() => !isProcessing && startDemo(scenario.id)}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">{scenario.title}</h3>
                  <Badge variant="outline">
                    {scenario.documents} docs
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">{scenario.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Timer className="w-4 h-4 text-gray-400" />
                    <span className="text-xs text-gray-500">~{scenario.expectedTime}s</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Layers className="w-4 h-4 text-gray-400" />
                    <span className="text-xs text-gray-500">{scenario.models.length} models</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {currentDemo && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Button
                  onClick={() => startDemo(currentDemo)}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  {isProcessing ? (
                    <>
                      <Activity className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Start Demo
                    </>
                  )}
                </Button>
                
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-blue-500" />
                    <span>Tasks: {completedTasks}/{tasks.length}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-green-500" />
                    <span>Time: {totalProcessingTime.toFixed(1)}s</span>
                  </div>
                </div>
              </div>

              {/* Real-time Processing Visualization */}
              {tasks.length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Network className="w-4 h-4" />
                    Distributed Processing Pipeline
                  </h4>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 max-h-96 overflow-y-auto">
                    {tasks.map((task) => (
                      <div
                        key={task.id}
                        className={`p-3 border rounded-lg transition-all ${
                          task.status === 'processing' ? 'border-blue-300 bg-blue-50' :
                          task.status === 'completed' ? 'border-green-300 bg-green-50' :
                          'border-gray-200 bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {getTaskIcon(task.type)}
                            <span className="text-xs font-medium capitalize">
                              {task.type}
                            </span>
                          </div>
                          {getStatusIcon(task.status)}
                        </div>
                        
                        <div className="text-xs text-gray-600 mb-2 truncate">
                          {task.model}
                        </div>
                        
                        <Progress value={task.progress} className="h-2 mb-2" />
                        
                        <div className="text-xs text-gray-500">
                          {task.progress.toFixed(0)}%
                        </div>
                        
                        {task.result && (
                          <div className="mt-2 pt-2 border-t text-xs">
                            {task.type === 'document' && (
                              <div>Events: {task.result.events_extracted}</div>
                            )}
                            {task.type === 'confidence' && (
                              <div>Avg: {(Object.values(task.result).reduce((a: any, b: any) => a + b, 0) / 4).toFixed(2)}</div>
                            )}
                            {task.type === 'sentiment' && (
                              <div>Sentiment: {task.result.sentiment_score > 0 ? '+' : ''}{task.result.sentiment_score.toFixed(2)}</div>
                            )}
                            {task.type === 'vision' && (
                              <div>Charts: {task.result.charts_processed}</div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Real-time Metrics */}
      {isProcessing && (
        <Card className="border-2 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 animate-pulse" />
              Live Processing Metrics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {((completedTasks / totalProcessingTime) * 60 || 0).toFixed(1)}
                </div>
                <div className="text-sm text-blue-700">Documents/minute</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {tasks.filter(t => t.status === 'processing').length}
                </div>
                <div className="text-sm text-green-700">Parallel processes</div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {totalProcessingTime.toFixed(1)}s
                </div>
                <div className="text-sm text-purple-700">Total time</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default TandemnDashboard
