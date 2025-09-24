import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Dialog, DialogContent, DialogTrigger } from "../components/ui/dialog";
import { 
  CheckSquare, 
  Clock, 
  Users, 
  TrendingUp,
  Plus,
  Calendar,
  AlertCircle,
  Target,
  Zap
} from "lucide-react";
import { useTask } from "../contexts/TaskContext";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../hooks/use-toast";
import TaskCard from "../components/TaskCard";
import TaskForm from "../components/TaskForm";

const Dashboard = () => {
  const { tasks, getTaskStats } = useTask();
  const { loginWithEmergent } = useAuth();
  const { toast } = useToast();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [emergentLoading, setEmergentLoading] = useState(false);
  
  // Handle Emergent Auth callback on dashboard
  useEffect(() => {
    const handleEmergentCallback = async () => {
      const hash = window.location.hash;
      const urlParams = new URLSearchParams(hash.substring(1));
      const sessionId = urlParams.get('session_id');
      
      if (sessionId) {
        setEmergentLoading(true);
        const result = await loginWithEmergent(sessionId);
        
        if (result.success) {
          toast({
            title: "Welcome to SmartTask AI! 🎉",
            description: "You have been successfully logged in with Google.",
          });
          
          // Clean the URL
          window.history.replaceState({}, document.title, window.location.pathname);
        } else {
          toast({
            title: "Login Failed",
            description: result.message,
            variant: "destructive",
          });
        }
        setEmergentLoading(false);
      }
    };

    handleEmergentCallback();
  }, [loginWithEmergent, toast]);

  const stats = getTaskStats();
  const recentTasks = tasks.slice(0, 6);
  const upcomingTasks = tasks
    .filter(task => task.due_date && task.status !== 'completed')
    .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    .slice(0, 5);

  const handleTaskFormSuccess = (task) => {
    setShowTaskForm(false);
    setEditingTask(null);
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setShowTaskForm(true);
  };

  const handleCloseTaskForm = () => {
    setShowTaskForm(false);
    setEditingTask(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's what's happening with your tasks.</p>
        </div>
        
        <Dialog open={showTaskForm} onOpenChange={setShowTaskForm}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700 transition-colors">
              <Plus className="mr-2 h-4 w-4" />
              New Task
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <TaskForm 
              task={editingTask}
              onSuccess={handleTaskFormSuccess}
              onCancel={handleCloseTaskForm}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTasks}</div>
            <p className="text-xs text-gray-600">
              Active tasks in your workspace
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completedTasks}</div>
            <div className="mt-2">
              <Progress value={stats.completionRate} className="h-2" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {stats.completionRate}% completion rate
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Zap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.inProgressTasks}</div>
            <p className="text-xs text-gray-600">
              Tasks currently being worked on
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.overdueTasks}</div>
            <p className="text-xs text-gray-600">
              {stats.overdueTasks > 0 ? 'Need immediate attention' : 'All tasks on track'}
            </p>
          </CardContent>
        </Card>
      </div>

      {tasks.length === 0 ? (
        // Empty State
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-gray-400 mb-4">
              <CheckSquare className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-2">No tasks yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by creating your first task. Stay organized and boost your productivity!
            </p>
            <Dialog open={showTaskForm} onOpenChange={setShowTaskForm}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Task
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <TaskForm 
                  onSuccess={handleTaskFormSuccess}
                  onCancel={handleCloseTaskForm}
                />
              </DialogContent>
            </Dialog>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Tasks */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="h-5 w-5" />
                Recent Tasks
              </CardTitle>
              <CardDescription>Your latest task activities</CardDescription>
            </CardHeader>
            <CardContent>
              {recentTasks.length > 0 ? (
                <div className="space-y-3">
                  {recentTasks.map((task) => (
                    <TaskCard 
                      key={task.id} 
                      task={task} 
                      onEdit={handleEditTask}
                      compact={true}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No recent tasks</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Deadlines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Upcoming Deadlines
              </CardTitle>
              <CardDescription>Tasks due soon</CardDescription>
            </CardHeader>
            <CardContent>
              {upcomingTasks.length > 0 ? (
                <div className="space-y-4">
                  {upcomingTasks.map((task) => {
                    const dueDate = new Date(task.due_date);
                    const today = new Date();
                    const diffTime = dueDate - today;
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    const isOverdue = diffDays < 0;
                    const isDueToday = diffDays === 0;
                    
                    return (
                      <div key={task.id} className="p-3 border rounded-lg hover:shadow-sm transition-shadow">
                        <h4 className="font-medium text-sm mb-1">{task.title}</h4>
                        <div className="flex items-center justify-between">
                          <Badge 
                            className={`text-xs ${
                              task.priority === 'high' ? 'bg-red-100 text-red-800' :
                              task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}
                          >
                            {task.priority}
                          </Badge>
                          <span className={`text-xs ${
                            isOverdue ? 'text-red-600 font-medium' :
                            isDueToday ? 'text-orange-600 font-medium' :
                            diffDays <= 3 ? 'text-yellow-600' :
                            'text-gray-500'
                          }`}>
                            {isOverdue ? `${Math.abs(diffDays)} days overdue` :
                             isDueToday ? 'Due today' :
                             `${diffDays} days left`}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No upcoming deadlines</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Dashboard;