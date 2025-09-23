# SmartTask AI - Backend Integration Contracts

## API Endpoints to Implement

### Task Management
- **GET /api/tasks** - Get all tasks with optional filtering
  - Query params: status, priority, search, assignee
  - Returns: Array of task objects

- **POST /api/tasks** - Create new task
  - Body: { title, description, priority, dueDate, assignee, tags?, projectId? }
  - Returns: Created task object

- **PUT /api/tasks/:id** - Update task
  - Body: Partial task object
  - Returns: Updated task object

- **DELETE /api/tasks/:id** - Delete task
  - Returns: Success confirmation

### Project Management
- **GET /api/projects** - Get all projects with optional filtering
  - Query params: status, search
  - Returns: Array of project objects

- **POST /api/projects** - Create new project
  - Body: { name, description, priority, dueDate, teamMembers }
  - Returns: Created project object

- **PUT /api/projects/:id** - Update project
  - Body: Partial project object
  - Returns: Updated project object

- **DELETE /api/projects/:id** - Delete project
  - Returns: Success confirmation

### Analytics
- **GET /api/analytics/stats** - Get dashboard statistics
  - Returns: { totalTasks, completedTasks, activeProjects, overdueTasks }

- **GET /api/analytics/tasks-by-status** - Task distribution by status
  - Returns: Object with status counts

- **GET /api/analytics/tasks-by-priority** - Task distribution by priority
  - Returns: Object with priority counts

### Team Management
- **GET /api/team** - Get team members
  - Returns: Array of team member objects

## Database Models

### Task Model
```
{
  _id: ObjectId,
  title: String (required),
  description: String (required),
  status: String (enum: ['pending', 'in-progress', 'completed']),
  priority: String (enum: ['low', 'medium', 'high']),
  dueDate: Date,
  assignee: String,
  estimatedTime: String,
  tags: [String],
  projectId: ObjectId (optional),
  createdAt: Date,
  updatedAt: Date
}
```

### Project Model
```
{
  _id: ObjectId,
  name: String (required),
  description: String (required),
  status: String (enum: ['planning', 'active', 'completed', 'on-hold']),
  priority: String (enum: ['low', 'medium', 'high']),
  progress: Number (0-100),
  dueDate: Date,
  teamMembers: [String],
  createdAt: Date,
  updatedAt: Date
}
```

### Team Member Model
```
{
  _id: ObjectId,
  name: String (required),
  email: String (required, unique),
  role: String,
  avatar: String (optional),
  status: String (enum: ['active', 'away', 'busy']),
  createdAt: Date
}
```

## Mock Data Replacement

### Frontend Changes Required
1. Replace `mockData` imports with actual API calls
2. Update state management for real-time data
3. Add loading states and error handling
4. Implement form submissions for creating/updating tasks and projects

### Key Files to Update
- `/app/frontend/src/pages/Dashboard.js` - Replace mock stats and recent tasks
- `/app/frontend/src/pages/Tasks.js` - Replace mock tasks with API calls
- `/app/frontend/src/pages/Projects.js` - Replace mock projects with API calls
- `/app/frontend/src/pages/Analytics.js` - Replace mock analytics with API calls

## Integration Steps
1. Create MongoDB models and database connection
2. Implement CRUD endpoints for tasks and projects
3. Add analytics calculation endpoints
4. Update frontend to use actual API endpoints
5. Add proper error handling and loading states
6. Test all functionality end-to-end

## Error Handling
- Consistent error response format: `{ error: true, message: "Error description" }`
- Frontend should show user-friendly error messages using toast notifications
- Implement proper HTTP status codes (200, 201, 400, 404, 500)

## Authentication (Future Enhancement)
- Currently using mock user data
- Can be enhanced with JWT authentication
- User sessions and role-based access control