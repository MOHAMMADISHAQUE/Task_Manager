import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const AuthCallback = () => {
  const navigate = useNavigate();
  const { loginWithEmergent, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [processing, setProcessing] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get session_id from URL hash
        const hash = window.location.hash;
        const urlParams = new URLSearchParams(hash.substring(1));
        const sessionId = urlParams.get('session_id');
        
        if (sessionId) {
          console.log('Processing Emergent Auth callback with session:', sessionId);
          
          const result = await loginWithEmergent(sessionId);
          
          if (result.success) {
            toast({
              title: "Welcome to SmartTask AI! 🎉",
              description: "You have been successfully logged in with Google.",
            });
            
            // Redirect to dashboard after successful auth
            navigate('/dashboard', { replace: true });
          } else {
            console.error('Emergent auth failed:', result.message);
            toast({
              title: "Authentication Failed",
              description: result.message || "Please try again",
              variant: "destructive",
            });
            
            // Redirect back to login on failure
            navigate('/login', { replace: true });
          }
        } else {
          console.error('No session_id found in URL');
          toast({
            title: "Authentication Error",
            description: "Invalid callback - no session found",
            variant: "destructive",
          });
          
          navigate('/login', { replace: true });
        }
      } catch (error) {
        console.error('Auth callback error:', error);
        toast({
          title: "Authentication Error",
          description: "Something went wrong during authentication",
          variant: "destructive",
        });
        
        navigate('/login', { replace: true });
      } finally {
        setProcessing(false);
      }
    };

    handleCallback();
  }, [loginWithEmergent, navigate, toast]);

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated && !processing) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, processing, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Completing Authentication...
        </h2>
        <p className="text-gray-600">
          Please wait while we finish setting up your account
        </p>
      </div>
    </div>
  );
};

export default AuthCallback;