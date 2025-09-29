import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Separator } from "../components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "../components/ui/avatar";
import { useToast } from "../hooks/use-toast";
import { useAuth } from "../contexts/AuthContext";
import ChangePasswordDialog from "../components/ChangePasswordDialog";
import { 
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Smartphone,
  Mail,
  Save,
  Camera
} from "lucide-react";

const Settings = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    desktop: false,
    task_reminders: true,
    project_updates: true,
    weekly_digest: false
  });

  const [profile, setProfile] = useState({
    name: "",
    email: "",
    role: "",
    timezone: "UTC+0",
    language: "English"
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Load user data on mount
  useEffect(() => {
    loadProfileData();
    loadNotificationSettings();
  }, []);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/settings/profile`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data.profile);
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
      toast({
        title: "Error",
        description: "Failed to load profile data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadNotificationSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings/notifications`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications);
      }
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const handleNotificationChange = (key, value) => {
    setNotifications(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleProfileChange = (key, value) => {
    setProfile(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveProfile = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${BACKEND_URL}/api/settings/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: profile.name,
          role: profile.role,
          timezone: profile.timezone,
          language: profile.language
        })
      });

      if (response.ok) {
        toast({
          title: "Profile Updated",
          description: "Your profile has been saved successfully",
        });
      } else {
        throw new Error('Failed to save profile');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save profile changes",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const saveNotifications = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${BACKEND_URL}/api/settings/notifications`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(notifications)
      });

      if (response.ok) {
        toast({
          title: "Notification Settings Updated",
          description: "Your notification preferences have been saved",
        });
      } else {
        throw new Error('Failed to save notifications');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save notification settings",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6 max-w-4xl animate-fade-in-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
        <div className="transform hover:scale-105 transition-transform duration-300">
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Settings ⚙️
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Manage your account settings and preferences.</p>
        </div>
      </div>

      {/* Profile Settings */}
      <Card className="hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] animate-fade-in-up">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Profile Information
          </CardTitle>
          <CardDescription>Update your personal information and profile details.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Avatar */}
          <div className="flex items-center gap-4">
            <Avatar className="h-20 w-20">
              <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
            <div>
              <Button variant="outline" size="sm">
                <Camera className="mr-2 h-4 w-4" />
                Change Photo
              </Button>
              <p className="text-xs text-gray-500 mt-1">JPG, PNG up to 2MB</p>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                value={profile.name}
                onChange={(e) => handleProfileChange('name', e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={profile.email}
                onChange={(e) => handleProfileChange('email', e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Input
                id="role"
                value={profile.role}
                onChange={(e) => handleProfileChange('role', e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select value={profile.timezone} onValueChange={(value) => handleProfileChange('timezone', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC-8">Pacific Time (UTC-8)</SelectItem>
                  <SelectItem value="UTC-5">Eastern Time (UTC-5)</SelectItem>
                  <SelectItem value="UTC+0">Greenwich Mean Time (UTC+0)</SelectItem>
                  <SelectItem value="UTC+1">Central European Time (UTC+1)</SelectItem>
                  <SelectItem value="UTC+9">Japan Standard Time (UTC+9)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end">
            <Button 
              onClick={saveProfile}
              disabled={saving || loading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] animate-fade-in-up animation-delay-100">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notification Preferences
          </CardTitle>
          <CardDescription>Configure how and when you receive notifications.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Notification Channels */}
          <div>
            <h4 className="font-medium mb-4">Notification Channels</h4>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-gray-500" />
                  <div>
                    <div className="font-medium text-sm">Email Notifications</div>
                    <div className="text-xs text-gray-500">Receive notifications via email</div>
                  </div>
                </div>
                <Switch
                  checked={notifications.email}
                  onCheckedChange={(value) => handleNotificationChange('email', value)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Smartphone className="h-4 w-4 text-gray-500" />
                  <div>
                    <div className="font-medium text-sm">Push Notifications</div>
                    <div className="text-xs text-gray-500">Receive push notifications on mobile</div>
                  </div>
                </div>
                <Switch
                  checked={notifications.push}
                  onCheckedChange={(value) => handleNotificationChange('push', value)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Globe className="h-4 w-4 text-gray-500" />
                  <div>
                    <div className="font-medium text-sm">Desktop Notifications</div>
                    <div className="text-xs text-gray-500">Show notifications on desktop</div>
                  </div>
                </div>
                <Switch
                  checked={notifications.desktop}
                  onCheckedChange={(value) => handleNotificationChange('desktop', value)}
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Notification Types */}
          <div>
            <h4 className="font-medium mb-4">Notification Types</h4>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">Task Reminders</div>
                  <div className="text-xs text-gray-500">Get reminded about upcoming task deadlines</div>
                </div>
                <Switch
                  checked={notifications.task_reminders}
                  onCheckedChange={(value) => handleNotificationChange('task_reminders', value)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">Project Updates</div>
                  <div className="text-xs text-gray-500">Notifications about project status changes</div>
                </div>
                <Switch
                  checked={notifications.project_updates}
                  onCheckedChange={(value) => handleNotificationChange('project_updates', value)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">Weekly Digest</div>
                  <div className="text-xs text-gray-500">Weekly summary of your productivity</div>
                </div>
                <Switch
                  checked={notifications.weekly_digest}
                  onCheckedChange={(value) => handleNotificationChange('weekly_digest', value)}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end mt-6">
            <Button 
              onClick={saveNotifications}
              disabled={saving || loading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {saving ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              {saving ? 'Saving...' : 'Save Notification Settings'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Appearance Settings */}
      <Card className="hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] animate-fade-in-up animation-delay-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Appearance
          </CardTitle>
          <CardDescription>Customize the look and feel of your workspace.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Theme</Label>
              <Select defaultValue="light">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Light</SelectItem>
                  <SelectItem value="dark">Dark</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label>Language</Label>
              <Select value={profile.language} onValueChange={(value) => handleProfileChange('language', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="English">English</SelectItem>
                  <SelectItem value="Spanish">Spanish</SelectItem>
                  <SelectItem value="French">French</SelectItem>
                  <SelectItem value="German">German</SelectItem>
                  <SelectItem value="Japanese">Japanese</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security
          </CardTitle>
          <CardDescription>Manage your account security and privacy settings.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            {profile.auth_provider === 'email' ? (
              <ChangePasswordDialog>
                <Button variant="outline" className="justify-start w-full sm:w-auto">
                  Change Password
                </Button>
              </ChangePasswordDialog>
            ) : (
              <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-lg">
                Password change is not available for Google authentication users
              </div>
            )}
            
            <Button 
              variant="outline" 
              className="justify-start w-full sm:w-auto"
              onClick={() => toast({
                title: "Coming Soon",
                description: "Two-factor authentication will be available soon",
              })}
            >
              Two-Factor Authentication
            </Button>
            
            <Button 
              variant="outline" 
              className="justify-start w-full sm:w-auto"
              onClick={() => toast({
                title: "Login History",
                description: "You can view your recent login activity",
              })}
            >
              Login History
            </Button>
            
            <Button 
              variant="outline" 
              className="justify-start w-full sm:w-auto text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={() => toast({
                title: "Account Deletion",
                description: "Please contact support to delete your account",
                variant: "destructive",
              })}
            >
              Delete Account
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;