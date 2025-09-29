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
            // Check if user needs onboarding
            try {
              const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
              const onboardingResponse = await fetch(`${BACKEND_URL}/api/onboarding/status`, {
                credentials: 'include'
              });
              
              if (onboardingResponse.ok) {
                const onboardingData = await onboardingResponse.json();
                
                if (!onboardingData.onboarded) {
                  // New user - show welcome/onboarding
                  toast({
                    title: "Welcome to SmartTask AI! 🎉",
                    description: "Let's set up your workspace",
                  });
                  navigate('/welcome', { replace: true });
                } else {
                  // Existing user - go to dashboard
                  toast({
                    title: "Welcome back! 🎉",
                    description: "You have been successfully logged in.",
                  });
                  navigate('/dashboard', { replace: true });
                }
              } else {
                // Fallback to dashboard if onboarding check fails
                navigate('/dashboard', { replace: true });
              }
            } catch (error) {
              console.error('Failed to check onboarding status:', error);
              // Fallback to dashboard
              navigate('/dashboard', { replace: true });
            }
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