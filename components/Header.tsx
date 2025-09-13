'use client'

import { useState } from 'react'
import { Search, Bell, Settings, User } from 'lucide-react'

interface HeaderProps {
  selectedCompany: string | null
  onCompanySelect: (companyId: string | null) => void
  companies: { id: string; name: string }[]
}

export function Header({ selectedCompany, onCompanySelect, companies }: HeaderProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearch, setShowSearch] = useState(false)

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800">
            {selectedCompany ? 
              companies.find(c => c.id === selectedCompany)?.name || 'Company Profile' :
              'M&A Network Intelligence'
            }
          </h2>
          {selectedCompany && (
            <button
              onClick={() => onCompanySelect(null)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              ← Back to Graph
            </button>
          )}
        </div>

        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <button
              onClick={() => setShowSearch(!showSearch)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Search size={20} />
            </button>
            
            {showSearch && (
              <div className="absolute right-0 top-12 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                <div className="p-3">
                  <input
                    type="text"
                    placeholder="Search companies..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                </div>
                
                {searchQuery && (
                  <div className="max-h-60 overflow-y-auto">
                    {filteredCompanies.length > 0 ? (
                      filteredCompanies.map(company => (
                        <button
                          key={company.id}
                          onClick={() => {
                            onCompanySelect(company.id)
                            setShowSearch(false)
                            setSearchQuery('')
                          }}
                          className="w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors"
                        >
                          <div className="font-medium">{company.name}</div>
                        </button>
                      ))
                    ) : (
                      <div className="px-4 py-2 text-gray-500">No companies found</div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Notifications */}
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
            <Bell size={20} />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
          </button>

          {/* Settings */}
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <Settings size={20} />
          </button>

          {/* User */}
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <User size={20} />
          </button>
        </div>
      </div>

      {/* Close search overlay */}
      {showSearch && (
        <div 
          className="fixed inset-0 z-40"
          onClick={() => setShowSearch(false)}
        />
      )}
    </header>
  )
}
