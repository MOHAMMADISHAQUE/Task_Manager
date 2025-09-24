import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const TaskContext = createContext();

export const useTask = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
};

export const TaskProvider = ({ children }) => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load tasks from localStorage on component mount
  useEffect(() => {
    if (user) {
      const savedTasks = localStorage.getItem(`tasks_${user.id}`);
      if (savedTasks) {
        try {
          setTasks(JSON.parse(savedTasks));
        } catch (error) {
          console.error('Error loading tasks from localStorage:', error);
        }
      }
    }
  }, [user]);

  // Save tasks to localStorage whenever tasks change
  useEffect(() => {
    if (user && tasks.length >= 0) {
      localStorage.setItem(`tasks_${user.id}`, JSON.stringify(tasks));
    }
  }, [tasks, user]);

  const createTask = async (taskData) => {
    try {
      setLoading(true);
      
      // Validate required fields
      if (!taskData.title?.trim()) {
        throw new Error('Task title is required');
      }

      const newTask = {
        id: Date.now().toString(), // Simple ID generation
        title: taskData.title.trim(),
        description: taskData.description?.trim() || '',
        priority: taskData.priority || 'medium',
        status: 'pending',
        dueDate: taskData.dueDate || null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        userId: user.id
      };

      setTasks(prevTasks => [newTask, ...prevTasks]);
      return { success: true, task: newTask };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setLoading(false);
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      setLoading(true);
      
      // Validate required fields
      if (updates.title !== undefined && !updates.title?.trim()) {
        throw new Error('Task title is required');
      }

      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId 
            ? { 
                ...task, 
                ...updates, 
                title: updates.title?.trim() || task.title,
                description: updates.description?.trim() ?? task.description,
                updatedAt: new Date().toISOString() 
              }
            : task
        )
      );

      return { success: true };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setLoading(true);
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      return { success: true };
    } catch (error) {
      return { success: false, message: error.message };
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskStatus = async (taskId) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return { success: false, message: 'Task not found' };

    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    return updateTask(taskId, { status: newStatus });
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const getTasksByPriority = (priority) => {
    return tasks.filter(task => task.priority === priority);
  };

  const getTaskStats = () => {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const pendingTasks = tasks.filter(t => t.status === 'pending').length;
    const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length;
    const overdueTasks = tasks.filter(t => {
      if (t.status === 'completed' || !t.dueDate) return false;
      return new Date(t.dueDate) < new Date();
    }).length;

    return {
      totalTasks,
      completedTasks,
      pendingTasks,
      inProgressTasks,
      overdueTasks,
      completionRate: totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
    };
  };

  const value = {
    tasks,
    loading,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskStatus,
    getTasksByStatus,
    getTasksByPriority,
    getTaskStats
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};