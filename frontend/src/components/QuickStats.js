import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const QuickStats = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    todayTasks: 0,
    overdueTasks: 0,
    completionStreak: 0,
    weeklyScore: 0,
    weekProgress: { completed: 0, total: 7 }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchQuickStats();
    }
  }, [user]);

  const fetchQuickStats = async () => {
    try {
      const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${BACKEND_URL}/api/tasks`, {
        credentials: 'include'
      });

      if (response.ok) {
        const tasks = await response.json();
        calculateStats(tasks);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (tasks) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 6 * 24 * 60 * 60 * 1000);

    let todayTasks = 0;
    let overdueTasks = 0;
    let completedThisWeek = 0;
    let totalTasks = tasks.length;
    let completedTasks = 0;

    // Calculate completion streak (simplified - days with completed tasks)
    const recentCompletions = new Set();

    tasks.forEach(task => {
      // Count completed tasks
      if (task.status === 'completed') {
        completedTasks++;
        
        // Track recent completions for streak calculation
        if (task.updated_at) {
          const completedDate = new Date(task.updated_at);
          if (completedDate >= weekAgo) {
            const dayKey = completedDate.toDateString();
            recentCompletions.add(dayKey);
            completedThisWeek++;
          }
        }
      }

      // Count today's tasks (due today or created today)
      if (task.due_date) {
        const dueDate = new Date(task.due_date);
        const dueDateOnly = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
        
        if (dueDateOnly.getTime() === today.getTime()) {
          todayTasks++;
        }
        
        // Count overdue tasks
        if (dueDateOnly < today && task.status !== 'completed') {
          overdueTasks++;
        }
      }
    });

    // Calculate weekly score
    const weeklyScore = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    // Simple streak calculation (days with completions this week)
    const completionStreak = recentCompletions.size;

    setStats({
      todayTasks,
      overdueTasks,
      completionStreak,
      weeklyScore,
      weekProgress: { completed: completedThisWeek, total: 7 }
    });
  };

  if (loading) {
    return (
      <div className="px-4 pb-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-4 border border-blue-100">
          <div className="animate-pulse">
            <div className="h-4 bg-blue-200 rounded w-24 mb-3"></div>
            <div className="space-y-2">
              <div className="h-3 bg-blue-200 rounded"></div>
              <div className="h-3 bg-blue-200 rounded"></div>
              <div className="h-3 bg-blue-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const progressPercentage = stats.weekProgress.total > 0 
    ? (stats.weekProgress.completed / stats.weekProgress.total) * 100 
    : 0;

  return (
    <div className="px-4 pb-4">
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-4 border border-blue-100">
        <h3 className="text-sm font-semibold text-gray-800 mb-3 flex items-center">
          <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Quick Stats
        </h3>
        
        <div className="space-y-3">
          {/* Today's Tasks */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Today's Tasks</span>
            </div>
            <span className="text-sm font-semibold text-gray-800">{stats.todayTasks}</span>
          </div>
          
          {/* Overdue Items */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Overdue</span>
            </div>
            <span className={`text-sm font-semibold ${stats.overdueTasks > 0 ? 'text-red-600' : 'text-gray-800'}`}>
              {stats.overdueTasks}
            </span>
          </div>
          
          {/* Completion Streak */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-orange-400 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Active Days</span>
            </div>
            <span className="text-sm font-semibold text-orange-600">{stats.completionStreak}/7</span>
          </div>
          
          {/* Weekly Score */}
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
              <span className="text-xs text-gray-600">Completion Rate</span>
            </div>
            <span className="text-sm font-semibold text-purple-600">{stats.weeklyScore}%</span>
          </div>
        </div>
        
        {/* Mini Progress Bar */}
        <div className="mt-3 pt-3 border-t border-blue-200">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-500">Week Activity</span>
            <span className="text-xs font-medium text-gray-700">
              {stats.weekProgress.completed}/{stats.weekProgress.total} days
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-1.5">
            <div 
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" 
              style={{width: `${Math.min(progressPercentage, 100)}%`}}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickStats;