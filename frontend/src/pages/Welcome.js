import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { CheckCircle, Sparkles, Zap, ArrowRight, Stars, Rocket } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Welcome = () => {
  const [workspaceType, setWorkspaceType] = useState('sample');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const handleSetupWorkspace = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/onboarding/setup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          add_sample_data: workspaceType === 'sample',
          workspace_type: workspaceType
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        toast({
          title: "Welcome to SmartTask AI! 🎉",
          description: data.message,
        });
        
        // Redirect to dashboard
        navigate('/dashboard', { replace: true });
      } else {
        throw new Error('Failed to set up workspace');
      }
    } catch (error) {
      toast({
        title: "Setup Error",
        description: "Failed to set up your workspace. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <Card className="border-0 shadow-xl">
          <CardHeader className="text-center pb-8">
            <div className="mx-auto w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Welcome to SmartTask AI
            </CardTitle>
            <CardDescription className="text-base text-gray-600 mt-2">
              Let's set up your personal productivity workspace
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold text-lg mb-4 text-gray-900">
                How would you like to start?
              </h3>
              
              <RadioGroup value={workspaceType} onValueChange={setWorkspaceType} className="space-y-4">
                {/* Clean Workspace Option */}
                <div className={`flex items-center space-x-3 p-5 rounded-lg border-2 transition-all cursor-pointer ${
                  workspaceType === 'clean' 
                    ? 'border-gray-400 bg-gray-50 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300'
                }`} onClick={() => setWorkspaceType('clean')}>
                  <RadioGroupItem value="clean" id="clean" />
                  <div className="flex items-start gap-4 flex-1">
                    <div className="flex-shrink-0 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="h-5 w-5 text-gray-700" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 text-base">Start Fresh</div>
                      <div className="text-sm text-gray-600 mt-1 leading-relaxed">
                        Begin with a clean workspace and create your own tasks and projects from scratch.
                      </div>
                      <div className="text-xs text-green-600 mt-2 font-medium">
                        Perfect for experienced users
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sample Data Option */}
                <div className={`flex items-center space-x-3 p-5 rounded-lg border-2 transition-all cursor-pointer ${
                  workspaceType === 'sample' 
                    ? 'border-blue-400 bg-blue-50 shadow-sm' 
                    : 'border-gray-200 hover:border-blue-300'
                }`} onClick={() => setWorkspaceType('sample')}>
                  <RadioGroupItem value="sample" id="sample" />
                  <div className="flex items-start gap-4 flex-1">
                    <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Zap className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900 text-base">Explore with Sample Data</div>
                      <div className="text-sm text-gray-600 mt-1 leading-relaxed">
                        Get started quickly with personalized sample projects and tasks to explore all features.
                      </div>
                      <div className="text-xs text-blue-600 mt-2 font-medium">
                        Recommended for new users • Unique to you
                      </div>
                    </div>
                  </div>
                </div>
              </RadioGroup>
            </div>

            {/* Features Preview */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">What you'll get:</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>AI-powered task creation</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Smart notifications</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Project management</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Analytics & insights</span>
                </div>
              </div>
            </div>

            {/* Action Button */}
            <Button 
              onClick={handleSetupWorkspace}
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 text-base font-medium"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Setting up your workspace...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  Get Started
                  <ArrowRight className="h-4 w-4" />
                </div>
              )}
            </Button>

            <p className="text-xs text-gray-500 text-center">
              You can always customize your workspace later in Settings
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Welcome;