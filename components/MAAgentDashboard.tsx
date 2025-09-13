'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Play, 
  Square, 
  Activity, 
  TrendingUp, 
  Bell, 
  Eye,
  Clock,
  Building2,
  AlertTriangle
} from 'lucide-react';

interface MAEvent {
  id: string;
  event_type: string;
  status: string;
  primary_company: { name: string };
  secondary_company?: { name: string };
  title: string;
  description: string;
  deal_value?: number;
  confidence_score: number;
  discovered_at: string;
}

interface AgentActivity {
  id: string;
  timestamp: string;
  activity_type: string;
  description: string;
  events_found: number;
  events_updated: number;
  execution_time: number;
  status: string;
}

interface Notification {
  id: string;
  title: string;
  message: string;
  priority: string;
  created_at: string;
  read: boolean;
}

interface DashboardData {
  status: {
    is_running: boolean;
    last_search_time?: string;
    monitoring_interval: number;
  };
  statistics: {
    total_events: number;
    events_today: number;
    high_confidence_events: number;
    unread_notifications: number;
    event_types_today: Record<string, number>;
  };
  recent_events: MAEvent[];
  notifications: Notification[];
  activities: AgentActivity[];
}

const MAAgentDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [agentLoading, setAgentLoading] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/ma-agent/dashboard');
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      setDashboardData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const startAgent = async () => {
    setAgentLoading(true);
    try {
      const response = await fetch('/api/ma-agent/start', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to start agent');
      await fetchDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start agent');
    } finally {
      setAgentLoading(false);
    }
  };

  const stopAgent = async () => {
    setAgentLoading(true);
    try {
      const response = await fetch('/api/ma-agent/stop', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to stop agent');
      await fetchDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop agent');
    } finally {
      setAgentLoading(false);
    }
  };

  const markNotificationRead = async (notificationId: string) => {
    try {
      await fetch(`/api/ma-agent/notifications/${notificationId}/read`, { method: 'POST' });
      await fetchDashboardData();
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const formatEventType = (eventType: string) => {
    return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatCurrency = (value: number) => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(1)}B`;
    } else if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(1)}M`;
    }
    return `$${value.toLocaleString()}`;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="m-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!dashboardData) return null;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">M&A Intelligence Agent</h1>
          <p className="text-gray-600">Real-time monitoring of mergers, acquisitions, and strategic partnerships</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${dashboardData.status.is_running ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm font-medium">
              {dashboardData.status.is_running ? 'Running' : 'Stopped'}
            </span>
          </div>
          <Button
            onClick={dashboardData.status.is_running ? stopAgent : startAgent}
            disabled={agentLoading}
            variant={dashboardData.status.is_running ? "destructive" : "default"}
            className="flex items-center space-x-2"
          >
            {dashboardData.status.is_running ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{dashboardData.status.is_running ? 'Stop' : 'Start'} Agent</span>
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Building2 className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Events</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.total_events}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Events Today</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.events_today}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Eye className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Confidence</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.high_confidence_events}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Bell className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Notifications</p>
                <p className="text-2xl font-bold text-gray-900">{dashboardData.statistics.unread_notifications}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Events */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building2 className="w-5 h-5" />
              <span>Recent M&A Events</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.recent_events.slice(0, 5).map((event) => (
                <div key={event.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{event.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        {event.primary_company.name}
                        {event.secondary_company && ` → ${event.secondary_company.name}`}
                      </p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Badge variant="outline">{formatEventType(event.event_type)}</Badge>
                        {event.deal_value && (
                          <Badge variant="secondary">{formatCurrency(event.deal_value)}</Badge>
                        )}
                        <Badge 
                          variant={event.confidence_score > 0.7 ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {Math.round(event.confidence_score * 100)}% confidence
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {dashboardData.recent_events.length === 0 && (
                <p className="text-gray-500 text-center py-8">No recent events found</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bell className="w-5 h-5" />
              <span>Recent Notifications</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboardData.notifications.slice(0, 5).map((notification) => (
                <div 
                  key={notification.id} 
                  className={`p-3 rounded-lg border ${notification.read ? 'bg-gray-50' : 'bg-blue-50'}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h5 className="font-medium text-gray-900">{notification.title}</h5>
                        <Badge className={getPriorityColor(notification.priority)}>
                          {notification.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(notification.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!notification.read && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => markNotificationRead(notification.id)}
                      >
                        Mark Read
                      </Button>
                    )}
                  </div>
                </div>
              ))}
              {dashboardData.notifications.length === 0 && (
                <p className="text-gray-500 text-center py-8">No notifications</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Activities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Agent Activity Log</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {dashboardData.activities.slice(0, 10).map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4 py-2">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'completed' ? 'bg-green-500' : 
                  activity.status === 'failed' ? 'bg-red-500' : 'bg-yellow-500'
                }`}></div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      <span>{activity.execution_time.toFixed(2)}s</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 mt-1">
                    <p className="text-xs text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                    {activity.events_found > 0 && (
                      <Badge variant="outline" className="text-xs">
                        {activity.events_found} events found
                      </Badge>
                    )}
                    {activity.events_updated > 0 && (
                      <Badge variant="secondary" className="text-xs">
                        {activity.events_updated} new
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {dashboardData.activities.length === 0 && (
              <p className="text-gray-500 text-center py-8">No recent activities</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MAAgentDashboard;
