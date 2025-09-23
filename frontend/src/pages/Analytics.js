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
  Zap
} from "lucide-react";
import { mockData } from "../data/mock";

const Analytics = () => {
  const { stats, tasks, projects } = mockData;

  // Calculate analytics data
  const completionRate = Math.round((stats.completedTasks / stats.totalTasks) * 100);
  const overdueRate = Math.round((stats.overdueTasks / stats.totalTasks) * 100);
  const activeProjectsRate = Math.round((stats.activeProjects / stats.totalProjects) * 100);

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-1">Get insights into your productivity and project performance.</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Task Completion Rate</CardTitle>
            <Target className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{completionRate}%</div>
            <div className="mt-2">
              <Progress value={completionRate} className="h-2" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              <TrendingUp className="inline h-3 w-3 text-green-600 mr-1" />
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Daily Tasks</CardTitle>
            <Zap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">6.4</div>
            <p className="text-xs text-gray-600 mt-1">
              <TrendingUp className="inline h-3 w-3 text-green-600 mr-1" />
              +0.8 from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Project Success Rate</CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{activeProjectsRate}%</div>
            <div className="mt-2">
              <Progress value={activeProjectsRate} className="h-2" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              <TrendingUp className="inline h-3 w-3 text-green-600 mr-1" />
              +5% from last quarter
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue Rate</CardTitle>
            <Clock className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{overdueRate}%</div>
            <div className="mt-2">
              <Progress value={overdueRate} className="h-2 bg-red-100" />
            </div>
            <p className="text-xs text-gray-600 mt-2">
              <TrendingDown className="inline h-3 w-3 text-red-600 mr-1" />
              -2% from last month
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
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Completed</span>
                </div>
                <div className="text-right">
                  <div className="font-medium">{tasksByStatus.completed}</div>
                  <div className="text-xs text-gray-500">
                    {Math.round((tasksByStatus.completed / tasks.length) * 100)}%
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
                    {Math.round((tasksByStatus['in-progress'] / tasks.length) * 100)}%
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
                    {Math.round((tasksByStatus.pending / tasks.length) * 100)}%
                  </div>
                </div>
              </div>
            </div>
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
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">High Priority</span>
                  <span className="text-sm font-medium">{tasksByPriority.high} tasks</span>
                </div>
                <Progress 
                  value={(tasksByPriority.high / tasks.length) * 100} 
                  className="h-2 bg-red-100"
                />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Medium Priority</span>
                  <span className="text-sm font-medium">{tasksByPriority.medium} tasks</span>
                </div>
                <Progress 
                  value={(tasksByPriority.medium / tasks.length) * 100} 
                  className="h-2 bg-yellow-100"
                />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Low Priority</span>
                  <span className="text-sm font-medium">{tasksByPriority.low} tasks</span>
                </div>
                <Progress 
                  value={(tasksByPriority.low / tasks.length) * 100} 
                  className="h-2 bg-green-100"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Team Performance
            </CardTitle>
            <CardDescription>Individual team member productivity metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockData.teamMembers.slice(0, 5).map((member) => (
                <div key={member.id} className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-sm">{member.name}</div>
                    <div className="text-xs text-gray-500">{member.role}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-sm">{member.tasksCount} tasks</div>
                    <div className={`text-xs px-2 py-1 rounded-full ${
                      member.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {member.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Recent Activity Summary
            </CardTitle>
            <CardDescription>Key metrics from the past 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tasks Created</span>
                <div className="text-right">
                  <div className="font-medium">24</div>
                  <div className="text-xs text-green-600">+15% vs prev month</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Tasks Completed</span>
                <div className="text-right">
                  <div className="font-medium">18</div>
                  <div className="text-xs text-green-600">+8% vs prev month</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Projects Started</span>
                <div className="text-right">
                  <div className="font-medium">3</div>
                  <div className="text-xs text-blue-600">Same as prev month</div>
                </div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Average Response Time</span>
                <div className="text-right">
                  <div className="font-medium">2.4h</div>
                  <div className="text-xs text-green-600">-0.3h vs prev month</div>
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