export const mockData = {
  tasks: [
    {
      id: 1,
      title: "Design new landing page",
      description: "Create a modern and responsive landing page for the new product launch",
      status: "in-progress",
      priority: "high",
      dueDate: "2024-01-15",
      assignee: "John Smith",
      estimatedTime: "8h",
      tags: ["design", "frontend", "marketing"]
    },
    {
      id: 2,
      title: "API integration for user authentication",
      description: "Implement secure user authentication system with JWT tokens",
      status: "pending",
      priority: "high",
      dueDate: "2024-01-12",
      assignee: "Sarah Johnson",
      estimatedTime: "12h",
      tags: ["backend", "security", "api"]
    },
    {
      id: 3,
      title: "Write project documentation",
      description: "Create comprehensive documentation for the new project features",
      status: "completed",
      priority: "medium",
      dueDate: "2024-01-10",
      assignee: "Mike Chen",
      estimatedTime: "6h",
      tags: ["documentation", "technical-writing"]
    },
    {
      id: 4,
      title: "Database schema optimization",
      description: "Optimize database queries and improve performance for user data",
      status: "in-progress",
      priority: "medium",
      dueDate: "2024-01-18",
      assignee: "Emily Davis",
      estimatedTime: "10h",
      tags: ["database", "performance", "backend"]
    },
    {
      id: 5,
      title: "Mobile app testing",
      description: "Conduct thorough testing of the mobile application on different devices",
      status: "pending",
      priority: "low",
      dueDate: "2024-01-20",
      assignee: "David Wilson",
      estimatedTime: "16h",
      tags: ["testing", "mobile", "qa"]
    },
    {
      id: 6,
      title: "Setup CI/CD pipeline",
      description: "Configure automated deployment pipeline for continuous integration",
      status: "completed",
      priority: "high",
      dueDate: "2024-01-08",
      assignee: "Alex Rodriguez",
      estimatedTime: "14h",
      tags: ["devops", "automation", "deployment"]
    },
    {
      id: 7,
      title: "User feedback analysis",
      description: "Analyze user feedback from beta testing and create improvement plan",
      status: "in-progress",
      priority: "medium",
      dueDate: "2024-01-16",
      assignee: "Lisa Thompson",
      estimatedTime: "4h",
      tags: ["analysis", "user-experience", "feedback"]
    },
    {
      id: 8,
      title: "Security audit review",
      description: "Conduct comprehensive security audit of the application",
      status: "pending",
      priority: "high",
      dueDate: "2024-01-22",
      assignee: "Tom Anderson",
      estimatedTime: "20h",
      tags: ["security", "audit", "compliance"]
    }
  ],

  projects: [
    {
      id: 1,
      name: "E-commerce Platform",
      description: "Build a comprehensive e-commerce platform with payment integration",
      status: "active",
      progress: 75,
      tasks: 24,
      dueDate: "Mar 15, 2024",
      team: ["John Smith", "Sarah Johnson", "Mike Chen"],
      priority: "high"
    },
    {
      id: 2,
      name: "Mobile App Development",
      description: "Cross-platform mobile application for task management",
      status: "active",
      progress: 45,
      tasks: 18,
      dueDate: "Apr 30, 2024",
      team: ["Emily Davis", "David Wilson", "Alex Rodriguez"],
      priority: "medium"
    },
    {
      id: 3,
      name: "Analytics Dashboard",
      description: "Real-time analytics dashboard for business intelligence",
      status: "active",
      progress: 90,
      tasks: 12,
      dueDate: "Feb 28, 2024",
      team: ["Lisa Thompson", "Tom Anderson"],
      priority: "high"
    },
    {
      id: 4,
      name: "Customer Support Portal",
      description: "Self-service customer support portal with ticketing system",
      status: "planning",
      progress: 15,
      tasks: 32,
      dueDate: "Jun 15, 2024",
      team: ["Sarah Johnson", "Mike Chen", "Emily Davis"],
      priority: "medium"
    },
    {
      id: 5,
      name: "API Documentation",
      description: "Comprehensive API documentation and developer resources",
      status: "completed",
      progress: 100,
      tasks: 8,
      dueDate: "Jan 10, 2024",
      team: ["Mike Chen", "Tom Anderson"],
      priority: "low"
    }
  ],

  stats: {
    totalTasks: 48,
    completedTasks: 12,
    activeProjects: 5,
    overdueTasks: 3,
    teamMembers: 8,
    totalProjects: 12
  },

  teamMembers: [
    {
      id: 1,
      name: "John Smith",
      role: "Frontend Developer",
      email: "john.smith@example.com",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face",
      tasksCount: 6,
      status: "active"
    },
    {
      id: 2,
      name: "Sarah Johnson",
      role: "Backend Developer",
      email: "sarah.johnson@example.com",
      avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b47c?w=32&h=32&fit=crop&crop=face",
      tasksCount: 8,
      status: "active"
    },
    {
      id: 3,
      name: "Mike Chen",
      role: "Technical Writer",
      email: "mike.chen@example.com",
      avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&h=32&fit=crop&crop=face",
      tasksCount: 4,
      status: "active"
    },
    {
      id: 4,
      name: "Emily Davis",
      role: "Database Administrator",
      email: "emily.davis@example.com",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&h=32&fit=crop&crop=face",
      tasksCount: 5,
      status: "active"
    },
    {
      id: 5,
      name: "David Wilson",
      role: "QA Engineer",
      email: "david.wilson@example.com",
      avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=32&h=32&fit=crop&crop=face",
      tasksCount: 7,
      status: "away"
    },
    {
      id: 6,
      name: "Alex Rodriguez",
      role: "DevOps Engineer",
      email: "alex.rodriguez@example.com",
      avatar: "https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?w=32&h=32&fit=crop&crop=face",
      tasksCount: 3,
      status: "active"
    },
    {
      id: 7,
      name: "Lisa Thompson",
      role: "UX Designer",
      email: "lisa.thompson@example.com",
      avatar: "https://images.unsplash.com/photo-1544725176-7c40e5a71c5e?w=32&h=32&fit=crop&crop=face",
      tasksCount: 2,
      status: "active"
    },
    {
      id: 8,
      name: "Tom Anderson",
      role: "Security Analyst",
      email: "tom.anderson@example.com",
      avatar: "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=32&h=32&fit=crop&crop=face",
      tasksCount: 4,
      status: "active"
    }
  ]
};