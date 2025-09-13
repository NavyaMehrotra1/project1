'use client'

import { useState } from 'react'
import { Database, Download, Upload, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react'
import { apiService } from '@/services/api'
import toast from 'react-hot-toast'

interface DataIngestionProps {
  onDataUpdate: () => void
}

export function DataIngestion({ onDataUpdate }: DataIngestionProps) {
  const [loading, setLoading] = useState(false)
  const [newsQuery, setNewsQuery] = useState('merger acquisition')
  const [daysBack, setDaysBack] = useState(30)
  const [lastIngestion, setLastIngestion] = useState<any>(null)

  const handleIngestNews = async () => {
    setLoading(true)
    try {
      const result = await apiService.ingestNews(newsQuery, daysBack)
      setLastIngestion(result)
      onDataUpdate()
      toast.success(`Ingested ${result.news_count} news articles, extracted ${result.deals_extracted} deals`)
    } catch (error) {
      console.error('News ingestion error:', error)
      toast.error('Failed to ingest news data')
    } finally {
      setLoading(false)
    }
  }

  const dataSources = [
    {
      name: 'NewsAPI',
      description: 'Real-time M&A news from major publications',
      status: 'active',
      lastUpdate: '2 hours ago'
    },
    {
      name: 'Yahoo Finance',
      description: 'Company financial data and market information',
      status: 'active',
      lastUpdate: '1 hour ago'
    },
    {
      name: 'SEC Filings',
      description: 'Official regulatory filings and disclosures',
      status: 'pending',
      lastUpdate: 'Not configured'
    },
    {
      name: 'Crunchbase API',
      description: 'Startup funding and acquisition data',
      status: 'pending',
      lastUpdate: 'Not configured'
    }
  ]

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
          <Database className="text-green-500" />
          Data Ingestion
        </h1>
        <p className="text-gray-600">
          Import and process M&A data from various sources to keep your network graph up-to-date
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* News Ingestion */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Download className="text-blue-500" />
              News Data Ingestion
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Query
                </label>
                <input
                  type="text"
                  value={newsQuery}
                  onChange={(e) => setNewsQuery(e.target.value)}
                  placeholder="e.g., merger acquisition, IPO, partnership"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Days Back
                </label>
                <select
                  value={daysBack}
                  onChange={(e) => setDaysBack(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={7}>Last 7 days</option>
                  <option value={30}>Last 30 days</option>
                  <option value={90}>Last 90 days</option>
                  <option value={365}>Last year</option>
                </select>
              </div>

              <button
                onClick={handleIngestNews}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <>
                    <RefreshCw size={20} className="animate-spin" />
                    Ingesting Data...
                  </>
                ) : (
                  <>
                    <Download size={20} />
                    Ingest News Data
                  </>
                )}
              </button>
            </div>

            {lastIngestion && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle size={16} className="text-green-600" />
                  <span className="font-medium text-green-800">Last Ingestion Successful</span>
                </div>
                <div className="text-sm text-green-700">
                  <div>Articles processed: {lastIngestion.news_count}</div>
                  <div>Deals extracted: {lastIngestion.deals_extracted}</div>
                </div>
              </div>
            )}
          </div>

          {/* Manual Upload */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Upload className="text-purple-500" />
              Manual Data Upload
            </h2>

            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload size={32} className="mx-auto text-gray-400 mb-2" />
                <p className="text-gray-600 mb-2">Drop CSV files here or click to browse</p>
                <p className="text-xs text-gray-500">Supported formats: CSV, JSON, Excel</p>
                <input
                  type="file"
                  accept=".csv,.json,.xlsx,.xls"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="mt-2 inline-block px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 cursor-pointer transition-colors"
                >
                  Choose Files
                </label>
              </div>

              <div className="text-xs text-gray-500">
                <p className="font-medium mb-1">Expected CSV format:</p>
                <p>company1, company2, deal_type, deal_value, deal_date, description</p>
              </div>
            </div>
          </div>
        </div>

        {/* Data Sources Status */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Data Sources</h2>

            <div className="space-y-4">
              {dataSources.map((source, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium">{source.name}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        source.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {source.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">{source.description}</p>
                    <p className="text-xs text-gray-500">Last update: {source.lastUpdate}</p>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {source.status === 'active' ? (
                      <CheckCircle size={20} className="text-green-500" />
                    ) : (
                      <AlertCircle size={20} className="text-yellow-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API Configuration */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">API Configuration</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  NewsAPI Key
                </label>
                <input
                  type="password"
                  placeholder="Enter your NewsAPI key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Anthropic API Key
                </label>
                <input
                  type="password"
                  placeholder="Enter your Anthropic API key"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors">
                Save Configuration
              </button>
            </div>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> API keys are stored securely and used only for data ingestion. 
                See our privacy policy for more details.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
