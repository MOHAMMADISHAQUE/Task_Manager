import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Checkbox } from './ui/checkbox';
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Calendar, 
  Clock, 
  Flag,
  CheckCircle2
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { useTask } from '../contexts/TaskContext';
import { useToast } from '../hooks/use-toast';

const TaskCard = ({ task, onEdit, compact = false }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const { toggleTaskStatus, deleteTask } = useTask();
  const { toast } = useToast();

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'in-progress': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'pending': return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const isOverdue = () => {
    if (task.status === 'completed' || !task.due_date) return false;
    return new Date(task.due_date) < new Date();
  };

  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    });
  };

  const handleToggleComplete = async () => {
    const result = await toggleTaskStatus(task.id);
    if (result.success) {
      toast({
        title: task.status === 'completed' ? "Task Reopened" : "Task Completed",
        description: task.status === 'completed' 
          ? "Task marked as pending."
          : "Great job! Task marked as completed.",
      });
    } else {
      toast({
        title: "Error",
        description: result.message,
        variant: "destructive",
      });
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    const result = await deleteTask(task.id);
    
    if (result.success) {
      toast({
        title: "Task Deleted",
        description: "The task has been deleted successfully.",
      });
    } else {
      toast({
        title: "Error",
        description: result.message,
        variant: "destructive",
      });
    }
    setIsDeleting(false);
  };

  if (compact) {
    return (
      <div className="flex items-center justify-between p-3 bg-white rounded-lg border hover:shadow-sm transition-shadow">
        <div className="flex items-center gap-3 flex-1">
          <Checkbox 
            checked={task.status === 'completed'}
            onCheckedChange={handleToggleComplete}
          />
          <div className="flex-1 min-w-0">
            <h4 className={`font-medium truncate ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {task.title}
            </h4>
            {task.due_date && (
              <div className={`flex items-center gap-1 text-xs mt-1 ${isOverdue() ? 'text-red-600' : 'text-gray-500'}`}>
                <Calendar className="h-3 w-3" />
                {formatDate(task.due_date)}
                {isOverdue() && <span className="text-red-600 font-medium">(Overdue)</span>}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
            {task.priority}
          </Badge>
        </div>
      </div>
    );
  }

  return (
    <Card className="group hover:shadow-md transition-all duration-200 hover:border-blue-200">
      <CardContent className="p-3 sm:p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-start gap-3 flex-1">
            <Checkbox 
              checked={task.status === 'completed'}
              onCheckedChange={handleToggleComplete}
              className="mt-1"
            />
            <div className="flex-1 min-w-0">
              <h3 className={`font-semibold text-base sm:text-lg mb-1 ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-2">{task.description}</p>
              )}
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                disabled={isDeleting}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit && onEdit(task)}>
                <Edit className="mr-2 h-4 w-4" />
                Edit Task
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleToggleComplete}>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                {task.status === 'completed' ? 'Mark as Pending' : 'Mark as Complete'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={handleDelete}
                className="text-red-600 focus:text-red-600"
                disabled={isDeleting}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {isDeleting ? 'Deleting...' : 'Delete Task'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="flex flex-wrap items-center gap-2 mb-3">
          <Badge className={`text-xs ${getStatusColor(task.status)}`}>
            {task.status}
          </Badge>
          <Badge className={`text-xs ${getPriorityColor(task.priority)}`}>
            <Flag className="mr-1 h-3 w-3" />
            {task.priority}
          </Badge>
        </div>

        {task.due_date && (
          <div className={`flex items-center gap-1 text-sm ${isOverdue() ? 'text-red-600' : 'text-gray-500'}`}>
            <Calendar className="h-4 w-4" />
            <span>Due: {formatDate(task.due_date)}</span>
            {isOverdue() && <span className="text-red-600 font-medium">(Overdue)</span>}
          </div>
        )}

        <div className="flex items-center justify-between mt-3 pt-3 border-t text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>Created {formatDate(task.created_at)}</span>
          </div>
          {task.updated_at !== task.created_at && (
            <span>Updated {formatDate(task.updated_at)}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TaskCard;