'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Home, 
  Brain, 
  BarChart3, 
  Users,
  BookOpen,
  Zap
} from 'lucide-react'

export const Navigation: React.FC = () => {
  const pathname = usePathname()

  const navItems = [
    {
      href: '/',
      label: 'Graph View',
      icon: BarChart3,
      description: 'Interactive M&A network visualization'
    },
    {
      href: '/ai-teach',
      label: 'AI Teacher',
      icon: Brain,
      description: 'Adaptive M&A learning system'
    },
    {
      href: '/ma-agent',
      label: 'M&A Agent',
      icon: Users,
      description: 'AI-powered deal analysis'
    },
    {
      href: '/demo',
      label: 'Demo',
      icon: Zap,
      description: 'Feature demonstrations'
    }
  ]

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">DealFlow AI</span>
          </Link>

          {/* Navigation Items */}
          <div className="flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon

              return (
                <Link key={item.href} href={item.href}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`relative flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      isActive
                        ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                    
                    {/* Tooltip */}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-3 py-2 bg-black/90 text-white text-sm rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      {item.description}
                    </div>
                  </motion.div>
                </Link>
              )
            })}
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-gray-300 text-sm">Live</span>
          </div>
        </div>
      </div>
    </nav>
  )
}
