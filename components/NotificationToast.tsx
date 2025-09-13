'use client';

import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { X, Bell, TrendingUp, Building2, Users } from 'lucide-react';

interface Notification {
  id: string;
  title: string;
  message: string;
  priority: string;
  created_at: string;
  read: boolean;
  notification_type: string;
}

interface NotificationToastProps {
  onNotificationRead?: (id: string) => void;
}

const NotificationToast: React.FC<NotificationToastProps> = ({ onNotificationRead }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [visibleNotifications, setVisibleNotifications] = useState<Notification[]>([]);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  // Fetch notifications from API
  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/ma-agent/notifications?unread_only=true');
      if (response.ok) {
        const data = await response.json();
        
        // Filter for new notifications since last check
        const newNotifications = data.filter((notif: Notification) => 
          new Date(notif.created_at) > lastCheck
        );
        
        if (newNotifications.length > 0) {
          setNotifications(data);
          
          // Show new notifications as toasts
          newNotifications.forEach((notif: Notification) => {
            showToast(notif);
          });
          
          setLastCheck(new Date());
        }
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  // Show toast notification
  const showToast = (notification: Notification) => {
    setVisibleNotifications(prev => [...prev, notification]);
    
    // Auto-hide after 5 seconds for low priority, 10 seconds for high priority
    const hideDelay = notification.priority === 'high' ? 10000 : 5000;
    
    setTimeout(() => {
      hideToast(notification.id);
    }, hideDelay);
  };

  // Hide toast notification
  const hideToast = (notificationId: string) => {
    setVisibleNotifications(prev => 
      prev.filter(notif => notif.id !== notificationId)
    );
  };

  // Mark notification as read
  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(`/api/ma-agent/notifications/${notificationId}/read`, {
        method: 'POST'
      });
      
      hideToast(notificationId);
      
      if (onNotificationRead) {
        onNotificationRead(notificationId);
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Get icon for notification type
  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'new_event':
        return <Building2 className="w-5 h-5" />;
      case 'impact_analysis':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <Bell className="w-5 h-5" />;
    }
  };

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-green-500 bg-green-50';
      default:
        return 'border-blue-500 bg-blue-50';
    }
  };

  // Poll for new notifications every 30 seconds
  useEffect(() => {
    fetchNotifications(); // Initial fetch
    
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [lastCheck]);

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {visibleNotifications.map((notification) => (
        <Alert
          key={notification.id}
          className={`${getPriorityColor(notification.priority)} border-2 shadow-lg animate-in slide-in-from-right duration-300`}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 mt-0.5">
              {getNotificationIcon(notification.notification_type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-semibold text-gray-900">
                    {notification.title}
                  </h4>
                  <Badge 
                    variant={notification.priority === 'high' ? 'destructive' : 'secondary'}
                    className="text-xs"
                  >
                    {notification.priority}
                  </Badge>
                </div>
                
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={() => hideToast(notification.id)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              <AlertDescription className="text-sm text-gray-700 mt-1">
                {notification.message}
              </AlertDescription>
              
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-gray-500">
                  {new Date(notification.created_at).toLocaleTimeString()}
                </span>
                
                <Button
                  size="sm"
                  variant="outline"
                  className="h-6 text-xs px-2"
                  onClick={() => markAsRead(notification.id)}
                >
                  Mark Read
                </Button>
              </div>
            </div>
          </div>
        </Alert>
      ))}
    </div>
  );
};

export default NotificationToast;
