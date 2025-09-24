import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const TaskContext = createContext();

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const useTask = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
};

export const TaskProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load tasks and projects when user is authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      loadTasks();
      loadProjects();
    } else {
      setTasks([]);
      setProjects([]);
    }
  }, [isAuthenticated, user]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/tasks/`, {
        withCredentials: true
      });
      setTasks(response.data || []);
    } catch (error) {
      console.error('Error loading tasks:', error);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects/`, {
        withCredentials: true
      });
      setProjects(response.data || []);
    } catch (error) {
      console.error('Error loading projects:', error);
      setProjects([]);
    }
  };

  const createTask = async (taskData) => {
    try {
      setLoading(true);
      
      // Validate required fields
      if (!taskData.title?.trim()) {
        throw new Error('Task title is required');
      }

      const payload = {
        title: taskData.title.trim(),
        description: taskData.description?.trim() || '',
        priority: taskData.priority || 'medium',
        due_date: taskData.dueDate || null,
        project_id: taskData.projectId || null,
        tags: taskData.tags || []
      };

      const response = await axios.post(`${API}/tasks/`, payload, {
        withCredentials: true
      });

      // Add new task to local state
      setTasks(prevTasks => [response.data, ...prevTasks]);
      
      return { success: true, task: response.data };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to create task';
      return { success: false, message };
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

      const payload = {};
      if (updates.title !== undefined) payload.title = updates.title.trim();
      if (updates.description !== undefined) payload.description = updates.description?.trim() || '';
      if (updates.status !== undefined) payload.status = updates.status;
      if (updates.priority !== undefined) payload.priority = updates.priority;
      if (updates.dueDate !== undefined) payload.due_date = updates.dueDate;
      if (updates.projectId !== undefined) payload.project_id = updates.projectId;
      if (updates.tags !== undefined) payload.tags = updates.tags;

      const response = await axios.put(`${API}/tasks/${taskId}`, payload, {
        withCredentials: true
      });

      // Update local state
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId ? response.data : task
        )
      );

      return { success: true, task: response.data };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to update task';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      setLoading(true);
      
      await axios.delete(`${API}/tasks/${taskId}`, {
        withCredentials: true
      });

      // Remove from local state
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to delete task';
      return { success: false, message };
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

  const createProject = async (projectData) => {
    try {
      setLoading(true);
      
      if (!projectData.name?.trim()) {
        throw new Error('Project name is required');
      }

      const payload = {
        name: projectData.name.trim(),
        description: projectData.description?.trim() || '',
        priority: projectData.priority || 'medium',
        due_date: projectData.dueDate || null,
        team_members: projectData.teamMembers || []
      };

      const response = await axios.post(`${API}/projects/`, payload, {
        withCredentials: true
      });

      setProjects(prevProjects => [response.data, ...prevProjects]);
      
      return { success: true, project: response.data };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to create project';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const updateProject = async (projectId, updates) => {
    try {
      setLoading(true);
      
      if (updates.name !== undefined && !updates.name?.trim()) {
        throw new Error('Project name is required');
      }

      const payload = {};
      if (updates.name !== undefined) payload.name = updates.name.trim();
      if (updates.description !== undefined) payload.description = updates.description?.trim() || '';
      if (updates.status !== undefined) payload.status = updates.status;
      if (updates.priority !== undefined) payload.priority = updates.priority;
      if (updates.progress !== undefined) payload.progress = updates.progress;
      if (updates.dueDate !== undefined) payload.due_date = updates.dueDate;
      if (updates.teamMembers !== undefined) payload.team_members = updates.teamMembers;

      const response = await axios.put(`${API}/projects/${projectId}`, payload, {
        withCredentials: true
      });

      setProjects(prevProjects => 
        prevProjects.map(project => 
          project.id === projectId ? response.data : project
        )
      );

      return { success: true, project: response.data };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to update project';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      setLoading(true);
      
      await axios.delete(`${API}/projects/${projectId}`, {
        withCredentials: true
      });

      setProjects(prevProjects => prevProjects.filter(project => project.id !== projectId));
      
      // Also remove tasks associated with this project
      setTasks(prevTasks => prevTasks.filter(task => task.project_id !== projectId));
      
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Failed to delete project';
      return { success: false, message };
    } finally {
      setLoading(false);
    }
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const getTasksByPriority = (priority) => {
    return tasks.filter(task => task.priority === priority);
  };

  const getTasksByProject = (projectId) => {
    return tasks.filter(task => task.project_id === projectId);
  };

  const getTaskStats = () => {
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(t => t.status === 'completed').length;
    const pendingTasks = tasks.filter(t => t.status === 'pending').length;
    const inProgressTasks = tasks.filter(t => t.status === 'in-progress').length;
    
    const overdueTasks = tasks.filter(t => {
      if (t.status === 'completed' || !t.due_date) return false;
      return new Date(t.due_date) < new Date();
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
    projects,
    loading,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskStatus,
    createProject,
    updateProject,
    deleteProject,
    getTasksByStatus,
    getTasksByPriority,
    getTasksByProject,
    getTaskStats,
    refreshTasks: loadTasks,
    refreshProjects: loadProjects
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};