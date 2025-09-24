import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Dialog, DialogContent, DialogTrigger } from "../components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  Plus, 
  Search, 
  Filter, 
  Calendar,
  Clock,
  User,
  MoreHorizontal,
  CheckSquare,
  AlertCircle,
  Flag
} from "lucide-react";
import { useTask } from "../contexts/TaskContext";
import TaskCard from "../components/TaskCard";
import TaskForm from "../components/TaskForm";

const Tasks = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [viewMode, setViewMode] = useState("all");
  
  const { tasks, getTasksByStatus } = useTask();

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || task.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const pendingTasks = getTasksByStatus('pending');
  const inProgressTasks = getTasksByStatus('in-progress');
  const completedTasks = getTasksByStatus('completed');
  const overdueTasks = tasks.filter(task => {
    if (task.status === 'completed' || !task.dueDate) return false;
    return new Date(task.dueDate) < new Date();
  });

  const handleTaskFormSuccess = () => {
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

  const TaskList = ({ tasks: taskList, emptyMessage }) => (
    <div className="space-y-4">
      {taskList.length > 0 ? (
        taskList.map((task) => (
          <TaskCard 
            key={task.id} 
            task={task} 
            onEdit={handleEditTask}
          />
        ))
      ) : (
        <Card>
          <CardContent className="p-8 text-center">
            <CheckSquare className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks found</h3>
            <p className="text-gray-600">{emptyMessage}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-600 mt-1">Manage and track all your tasks in one place.</p>
        </div>
        
        <Dialog open={showTaskForm} onOpenChange={setShowTaskForm}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700 transition-colors">
              <Plus className="mr-2 h-4 w-4" />
              Add New Task
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

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2 text-blue-600 mb-1">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-medium">Pending</span>
          </div>
          <div className="text-2xl font-bold text-blue-700">{pendingTasks.length}</div>
        </div>
        
        <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200">
          <div className="flex items-center gap-2 text-yellow-600 mb-1">
            <Flag className="h-4 w-4" />
            <span className="text-sm font-medium">In Progress</span>
          </div>
          <div className="text-2xl font-bold text-yellow-700">{inProgressTasks.length}</div>
        </div>
        
        <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
          <div className="flex items-center gap-2 text-green-600 mb-1">
            <CheckSquare className="h-4 w-4" />
            <span className="text-sm font-medium">Completed</span>
          </div>
          <div className="text-2xl font-bold text-green-700">{completedTasks.length}</div>
        </div>
        
        <div className="bg-gradient-to-r from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
          <div className="flex items-center gap-2 text-red-600 mb-1">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">Overdue</span>
          </div>
          <div className="text-2xl font-bold text-red-700">{overdueTasks.length}</div>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in-progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>

            {/* Priority Filter */}
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>

            <Button 
              variant="outline"
              onClick={() => {
                setSearchTerm("");
                setStatusFilter("all");
                setPriorityFilter("all");
              }}
            >
              <Filter className="mr-2 h-4 w-4" />
              Clear
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Task Tabs */}
      <Tabs value={viewMode} onValueChange={setViewMode} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="all">All Tasks</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="in-progress">In Progress</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="overdue">Overdue</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <TaskList 
            tasks={filteredTasks} 
            emptyMessage={searchTerm || statusFilter !== "all" || priorityFilter !== "all" 
              ? "Try adjusting your filters or search terms."
              : "Get started by creating your first task."
            }
          />
        </TabsContent>

        <TabsContent value="pending">
          <TaskList 
            tasks={pendingTasks.filter(task => {
              const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                   task.description.toLowerCase().includes(searchTerm.toLowerCase());
              const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
              return matchesSearch && matchesPriority;
            })} 
            emptyMessage="No pending tasks. Great job staying on top of things!"
          />
        </TabsContent>

        <TabsContent value="in-progress">
          <TaskList 
            tasks={inProgressTasks.filter(task => {
              const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                   task.description.toLowerCase().includes(searchTerm.toLowerCase());
              const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
              return matchesSearch && matchesPriority;
            })} 
            emptyMessage="No tasks in progress. Start working on a pending task!"
          />
        </TabsContent>

        <TabsContent value="completed">
          <TaskList 
            tasks={completedTasks.filter(task => {
              const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                   task.description.toLowerCase().includes(searchTerm.toLowerCase());
              const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
              return matchesSearch && matchesPriority;
            })} 
            emptyMessage="No completed tasks yet. Complete some tasks to see them here!"
          />
        </TabsContent>

        <TabsContent value="overdue">
          <TaskList 
            tasks={overdueTasks.filter(task => {
              const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                                   task.description.toLowerCase().includes(searchTerm.toLowerCase());
              const matchesPriority = priorityFilter === "all" || task.priority === priorityFilter;
              return matchesSearch && matchesPriority;
            })} 
            emptyMessage="No overdue tasks. Excellent time management!"
          />
        </TabsContent>
      </Tabs>

      {/* Empty State for no tasks at all */}
      {tasks.length === 0 && (
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
      )}
    </div>
  );
};

export default Tasks;