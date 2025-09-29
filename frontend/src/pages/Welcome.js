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
  const [mounted, setMounted] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    setMounted(true);
  }, []);

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
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-4">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        {/* Floating Particles */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-white rounded-full opacity-20 animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${2 + Math.random() * 2}s`
              }}
            />
          ))}
        </div>
        
        {/* Gradient Orbs */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
      </div>

      <div className={`relative z-10 w-full max-w-2xl transform transition-all duration-1000 ${
        mounted ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'
      }`}>
        <Card className="border-0 shadow-2xl bg-white/10 backdrop-blur-lg border border-white/20">
          <CardHeader className="text-center pb-8 relative">
            {/* Animated Logo */}
            <div className="relative mx-auto mb-6">
              <div className="absolute inset-0 w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full blur-lg opacity-60 animate-pulse"></div>
              <div className="relative w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg transform hover:scale-110 transition-transform duration-300 group">
                <Sparkles className="h-8 w-8 text-white animate-spin-slow group-hover:animate-bounce" />
                {/* Orbiting elements */}
                <div className="absolute inset-0 animate-spin-slow">
                  <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <div className="absolute top-1/2 -right-2 transform -translate-y-1/2 w-1.5 h-1.5 bg-pink-400 rounded-full"></div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-cyan-400 rounded-full"></div>
                </div>
              </div>
            </div>

            <CardTitle className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent mb-4 animate-fade-in-up">
              Welcome to SmartTask AI
            </CardTitle>
            <CardDescription className="text-lg text-white/80 animate-fade-in-up animation-delay-200">
              Let's set up your <span className="text-transparent bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text font-semibold">personal productivity workspace</span>
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-8 relative">
            <div className={`transform transition-all duration-700 ${
              mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`} style={{ animationDelay: '400ms' }}>
              <h3 className="font-bold text-xl mb-6 text-white text-center">
                🚀 How would you like to start your <span className="text-transparent bg-gradient-to-r from-yellow-400 to-pink-400 bg-clip-text">journey</span>?
              </h3>
              
              <RadioGroup value={workspaceType} onValueChange={setWorkspaceType} className="space-y-4">
                {/* Clean Workspace Option */}
                <div 
                  className={`group relative overflow-hidden p-6 rounded-xl border-2 cursor-pointer transform transition-all duration-500 hover:scale-105 ${
                    workspaceType === 'clean' 
                      ? 'border-cyan-400 bg-gradient-to-r from-white/20 to-cyan-100/20 shadow-2xl shadow-cyan-500/25' 
                      : 'border-white/30 bg-white/5 hover:border-cyan-300 hover:bg-white/10 hover:shadow-xl hover:shadow-cyan-500/10'
                  }`} 
                  onClick={() => setWorkspaceType('clean')}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  <div className="relative flex items-center space-x-3">
                    <RadioGroupItem value="clean" id="clean" />
                    <div className="flex items-start gap-4 flex-1">
                      <div className="relative flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-gray-300 to-gray-500 rounded-xl"></div>
                        <div className="absolute inset-0 bg-gradient-to-tl from-white/20 to-transparent rounded-xl"></div>
                        <CheckCircle className="relative h-6 w-6 text-white drop-shadow-lg transform group-hover:rotate-12 transition-transform duration-300" />
                      </div>
                      <div>
                        <div className="font-bold text-white text-lg flex items-center gap-2">
                          Start Fresh 
                          <Stars className="h-4 w-4 text-cyan-400 animate-pulse" />
                        </div>
                        <div className="text-sm text-white/80 mt-2 leading-relaxed">
                          Begin with a clean workspace and create your own tasks and projects from scratch.
                        </div>
                        <div className="text-xs text-cyan-300 mt-3 font-semibold flex items-center gap-1">
                          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                          Perfect for experienced users
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sample Data Option */}
                <div 
                  className={`group relative overflow-hidden p-6 rounded-xl border-2 cursor-pointer transform transition-all duration-500 hover:scale-105 ${
                    workspaceType === 'sample' 
                      ? 'border-purple-400 bg-gradient-to-r from-purple-100/20 to-pink-100/20 shadow-2xl shadow-purple-500/25' 
                      : 'border-white/30 bg-white/5 hover:border-purple-300 hover:bg-white/10 hover:shadow-xl hover:shadow-purple-500/10'
                  }`} 
                  onClick={() => setWorkspaceType('sample')}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                  <div className="relative flex items-center space-x-3">
                    <RadioGroupItem value="sample" id="sample" />
                    <div className="flex items-start gap-4 flex-1">
                      <div className="relative flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-purple-400 to-pink-500 rounded-xl"></div>
                        <div className="absolute inset-0 bg-gradient-to-tl from-white/20 to-transparent rounded-xl"></div>
                        <Zap className="relative h-6 w-6 text-white drop-shadow-lg animate-pulse transform group-hover:scale-110 transition-transform duration-300" />
                      </div>
                      <div>
                        <div className="font-bold text-white text-lg flex items-center gap-2">
                          Explore with Sample Data 
                          <Rocket className="h-4 w-4 text-yellow-400 animate-bounce" />
                        </div>
                        <div className="text-sm text-white/80 mt-2 leading-relaxed">
                          Get started quickly with personalized sample projects and tasks to explore all features.
                        </div>
                        <div className="text-xs text-purple-300 mt-3 font-semibold flex items-center gap-1">
                          <span className="w-2 h-2 bg-yellow-400 rounded-full animate-ping"></span>
                          Recommended for new users • Unique to you
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </RadioGroup>
            </div>

            {/* Features Preview */}
            <div className={`relative overflow-hidden bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-6 transform transition-all duration-700 ${
              mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`} style={{ animationDelay: '800ms' }}>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5"></div>
              <h4 className="relative font-bold text-white mb-4 text-center">✨ What you'll get:</h4>
              <div className="relative grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                {[
                  { icon: "🤖", text: "AI-powered task creation", delay: "900ms" },
                  { icon: "🔔", text: "Smart notifications", delay: "1000ms" },
                  { icon: "📊", text: "Project management", delay: "1100ms" },
                  { icon: "📈", text: "Analytics & insights", delay: "1200ms" }
                ].map((feature, index) => (
                  <div 
                    key={index}
                    className={`flex items-center gap-3 p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-300 transform hover:scale-105 ${
                      mounted ? 'translate-x-0 opacity-100' : 'translate-x-4 opacity-0'
                    }`}
                    style={{ animationDelay: feature.delay }}
                  >
                    <span className="text-lg animate-bounce" style={{ animationDelay: feature.delay }}>{feature.icon}</span>
                    <span className="text-white/90 font-medium">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Button */}
            <div className={`transform transition-all duration-700 ${
              mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`} style={{ animationDelay: '1300ms' }}>
              <Button 
                onClick={handleSetupWorkspace}
                disabled={loading}
                className="relative w-full h-14 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 hover:from-purple-500 hover:via-pink-500 hover:to-purple-500 text-white text-lg font-bold rounded-xl shadow-2xl shadow-purple-500/50 border border-white/20 overflow-hidden group transform hover:scale-105 transition-all duration-300"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/50 to-pink-600/50 animate-pulse"></div>
                {loading ? (
                  <div className="relative flex items-center gap-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span className="animate-pulse">Setting up your cosmic workspace...</span>
                  </div>
                ) : (
                  <div className="relative flex items-center gap-3">
                    <Rocket className="h-5 w-5 animate-bounce" />
                    <span>Launch Your Journey</span>
                    <ArrowRight className="h-5 w-5 transform group-hover:translate-x-1 transition-transform duration-300" />
                  </div>
                )}
              </Button>
            </div>

            <p className={`text-xs text-white/60 text-center transform transition-all duration-700 ${
              mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'
            }`} style={{ animationDelay: '1400ms' }}>
              ✨ You can always customize your workspace later in Settings
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Welcome;