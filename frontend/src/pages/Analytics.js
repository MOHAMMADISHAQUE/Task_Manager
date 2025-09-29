import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown,
  CheckSquare,
  Clock,
  Users,
  Calendar,
  BarChart3,
  PieChart,
  Target,
  Zap,
  AlertCircle
} from "lucide-react";
import { useTask } from "../contexts/TaskContext";

const Analytics = () => {
  const { tasks, getTaskStats } = useTask();
  const stats = getTaskStats();

  // Calculate analytics data
  const tasksByPriority = {
    high: tasks.filter(t => t.priority === 'high').length,
    medium: tasks.filter(t => t.priority === 'medium').length,
    low: tasks.filter(t => t.priority === 'low').length,
  };

  const tasksByStatus = {
    completed: tasks.filter(t => t.status === 'completed').length,
    'in-progress': tasks.filter(t => t.status === 'in-progress').length,
    pending: tasks.filter(t => t.status === 'pending').length,
  };

  // Calculate productivity trends
  const today = new Date();
  const thisWeek = tasks.filter(task => {
    const taskDate = new Date(task.createdAt);
    const diffTime = today - taskDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7;
  });

  const completedThisWeek = thisWeek.filter(t => t.status === 'completed').length;
  const weeklyCompletionRate = thisWeek.length > 0 ? Math.round((completedThisWeek / thisWeek.length) * 100) : 0;

  // Overdue tasks analysis
  const overdueTasks = tasks.filter(task => {
    if (task.status === 'completed' || !task.dueDate) return false;
    return new Date(task.dueDate) < today;
  });

  // Upcoming deadlines
  const upcomingDeadlines = tasks.filter(task => {
    if (task.status === 'completed' || !task.dueDate) return false;
    const dueDate = new Date(task.dueDate);
    const diffTime = dueDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 7 && diffDays >= 0;
  });

  const getPercentage = (count, total) => {
    return total > 0 ? Math.round((count / total) * 100) : 0;
  };

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
        <div className="transform hover:scale-105 transition-transform duration-300">
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
            Analytics 📊
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Get insights into your productivity and task performance.</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 animate-fade-in-up">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Task Completion Rate</CardTitle>
            <Target className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completionRate}%</div>
            <div className="mt-2">
              <Progress value={stats.completionRate} className="h-2" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {stats.completedTasks} of {stats.totalTasks} tasks completed
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 animate-fade-in-up">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Weekly Progress</CardTitle>
            <Zap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{weeklyCompletionRate}%</div>
            <div className="mt-2">
              <Progress value={weeklyCompletionRate} className="h-2" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {completedThisWeek} tasks completed this week
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 animate-fade-in-up">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tasks</CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats.pendingTasks + stats.inProgressTasks}</div>
            <p className="text-xs text-gray-600 mt-1">
              {stats.pendingTasks} pending, {stats.inProgressTasks} in progress
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 animate-fade-in-up">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue Tasks</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.overdueTasks}</div>
            <p className="text-xs text-gray-600 mt-1">
              {stats.overdueTasks > 0 ? 'Need immediate attention' : 'All tasks on track!'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Task Distribution by Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              Task Distribution by Status
            </CardTitle>
            <CardDescription>Breakdown of tasks by current status</CardDescription>
          </CardHeader>
          <CardContent>
            {stats.totalTasks > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Completed</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{tasksByStatus.completed}</div>
                    <div className="text-xs text-gray-500">
                      {getPercentage(tasksByStatus.completed, tasks.length)}%
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">In Progress</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{tasksByStatus['in-progress']}</div>
                    <div className="text-xs text-gray-500">
                      {getPercentage(tasksByStatus['in-progress'], tasks.length)}%
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Pending</span>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">{tasksByStatus.pending}</div>
                    <div className="text-xs text-gray-500">
                      {getPercentage(tasksByStatus.pending, tasks.length)}%
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <PieChart className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No task data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Task Priority Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Task Priority Analysis
            </CardTitle>
            <CardDescription>Distribution of tasks by priority level</CardDescription>
          </CardHeader>
          <CardContent>
            {stats.totalTasks > 0 ? (
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">High Priority</span>
                    </div>
                    <span className="text-sm font-medium">{tasksByPriority.high} tasks</span>
                  </div>
                  <Progress 
                    value={getPercentage(tasksByPriority.high, tasks.length)} 
                    className="h-2"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Medium Priority</span>
                    </div>
                    <span className="text-sm font-medium">{tasksByPriority.medium} tasks</span>
                  </div>
                  <Progress 
                    value={getPercentage(tasksByPriority.medium, tasks.length)} 
                    className="h-2"
                  />
                </div>
                
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">Low Priority</span>
                    </div>
                    <span className="text-sm font-medium">{tasksByPriority.low} tasks</span>
                  </div>
                  <Progress 
                    value={getPercentage(tasksByPriority.low, tasks.length)} 
                    className="h-2"
                  />
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <BarChart3 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No priority data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Deadlines */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Upcoming Deadlines
            </CardTitle>
            <CardDescription>Tasks due in the next 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            {upcomingDeadlines.length > 0 ? (
              <div className="space-y-4">
                {upcomingDeadlines.slice(0, 5).map((task) => {
                  const dueDate = new Date(task.dueDate);
                  const diffTime = dueDate - today;
                  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                  
                  return (
                    <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div>
                        <div className="font-medium text-sm">{task.title}</div>
                        <div className="text-xs text-gray-500 capitalize">{task.priority} priority</div>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${
                          diffDays === 0 ? 'text-red-600' : 
                          diffDays <= 2 ? 'text-orange-600' : 'text-blue-600'
                        }`}>
                          {diffDays === 0 ? 'Due today' : `${diffDays} days`}
                        </div>
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

        {/* Recent Activity Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Productivity Insights
            </CardTitle>
            <CardDescription>Your task management patterns</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Tasks Created</span>
                <div className="text-right">
                  <div className="font-medium">{stats.totalTasks}</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Average Completion Rate</span>
                <div className="text-right">
                  <div className="font-medium">{stats.completionRate}%</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tasks This Week</span>
                <div className="text-right">
                  <div className="font-medium">{thisWeek.length}</div>
                  <div className="text-xs text-gray-500">{completedThisWeek} completed</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tasks Needing Attention</span>
                <div className="text-right">
                  <div className="font-medium text-red-600">{overdueTasks.length + upcomingDeadlines.length}</div>
                  <div className="text-xs text-gray-500">
                    {overdueTasks.length} overdue, {upcomingDeadlines.length} due soon
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;