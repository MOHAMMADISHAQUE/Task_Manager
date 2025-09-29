import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();
  const [mountTime] = useState(Date.now());

  // If we've been loading for more than 10 seconds total, force redirect
  const isStuckLoading = loading && (Date.now() - mountTime) > 10000;

  if (loading && !isStuckLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
          <p className="mt-2 text-xs text-gray-500">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (isStuckLoading || !user) {
    console.log(isStuckLoading ? 'ProtectedRoute: Timeout reached' : 'ProtectedRoute: No user, redirecting');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;