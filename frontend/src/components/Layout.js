import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import UserMenu from "./UserMenu";
import NotificationDropdown from "./NotificationDropdown";
import { useAuth } from "../contexts/AuthContext";
import { 
  LayoutDashboard, 
  CheckSquare, 
  Folder, 
  BarChart3, 
  Settings,
  Menu,
  X,
  Bell,
  Search
} from "lucide-react";

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { loading } = useAuth();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Tasks", href: "/tasks", icon: CheckSquare },
    { name: "Projects", href: "/projects", icon: Folder },
    { name: "Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  const isActive = (href) => {
    return location.pathname === href || (href === "/dashboard" && location.pathname === "/");
  };

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 animate-fade-in-up">
        <div className="text-center">
          <div className="relative">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <div className="absolute inset-0 animate-ping rounded-full h-12 w-12 border border-blue-400 opacity-20"></div>
          </div>
          <h2 className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Loading SmartTask AI ✨
          </h2>
          <p className="text-gray-600 animate-pulse">
            Setting up your workspace...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navbar */}
      <nav className="bg-white shadow-sm border-b border-gray-200 fixed w-full top-0 z-50">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-14 sm:h-16">
            {/* Left side */}
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="lg:hidden"
              >
                <Menu className="h-6 w-6" />
              </Button>
              <div className="flex-shrink-0 flex items-center ml-4 lg:ml-0">
                <h1 className="text-xl font-bold text-blue-600">SmartTask AI</h1>
              </div>
            </div>

            {/* Center - Search */}
            <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search tasks, projects..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              <NotificationDropdown />
              <UserMenu />
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col lg:pt-16 z-30">
        <div className="flex flex-col flex-1 min-h-0 bg-white border-r border-gray-200">
          <nav className="flex-1 px-4 py-2 space-y-0.5">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-3 py-1.5 text-sm font-medium rounded-lg cursor-pointer
                    ${isActive(item.href)
                      ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600 shadow-sm'
                      : 'text-gray-700'
                    }
                  `}
                >
                  <Icon className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-blue-600' : 'text-gray-500'
                  }`} />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <div className={`
        lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white transform transition-transform duration-300 ease-in-out pt-14 sm:pt-16
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full border-r border-gray-200">
          {/* Close button for mobile - compact header */}
          <div className="flex items-center justify-between px-4 py-2 border-b border-gray-100">
            <h2 className="text-sm font-semibold text-gray-900">Menu</h2>
            <Button variant="ghost" size="sm" onClick={() => setSidebarOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-2 space-y-0.5">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    group flex items-center px-3 py-1.5 text-sm font-medium rounded-lg cursor-pointer
                    ${isActive(item.href)
                      ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600 shadow-sm'
                      : 'text-gray-700'
                    }
                  `}
                >
                  <Icon className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-blue-600' : 'text-gray-500'
                  }`} />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 pt-14 sm:pt-16 relative">
        {/* Subtle animated background - only for main content area */}
        <div className="absolute inset-0 lg:left-0 bg-gradient-to-br from-blue-50/30 via-white to-purple-50/30 animate-pulse pointer-events-none" style={{ animationDuration: '8s' }}></div>
        <main className="relative p-3 sm:p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;