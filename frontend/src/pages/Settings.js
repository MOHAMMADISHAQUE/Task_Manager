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
import { useTheme } from "../contexts/ThemeContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useNotifications } from "../contexts/NotificationContext";
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
  const { theme, toggleTheme, setTheme } = useTheme();
  const { currentLanguage, changeLanguage, t, availableLanguages } = useLanguage();
  const { createTestNotifications } = useNotifications();
  
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
    <div className="space-y-8 max-w-4xl animate-fade-in-up">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4">
        <div className="transform hover:scale-105 transition-transform duration-300">
          <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            {t('settings.title')} ⚙️
          </h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">{t('settings.description')}</p>
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
        <CardContent className="space-y-8">
          {/* Avatar */}
          <div className="flex items-center gap-6">
            <Avatar className="h-20 w-20">
              <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=80&h=80&fit=crop&crop=face" />
              <AvatarFallback>JD</AvatarFallback>
            </Avatar>
            <div className="space-y-3">
              <Button variant="outline" size="sm" className="h-9">
                <Camera className="mr-2 h-4 w-4" />
                Change Photo
              </Button>
              <p className="text-xs text-gray-500">JPG, PNG up to 2MB</p>
            </div>
          </div>

          {/* Form Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <Label htmlFor="name" className="text-sm font-medium">Full Name</Label>
              <Input
                id="name"
                value={profile.name}
                onChange={(e) => handleProfileChange('name', e.target.value)}
                disabled={loading}
                className="h-10"
              />
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
              <Input
                id="email"
                type="email"
                value={profile.email}
                disabled
                className="bg-gray-50 dark:bg-gray-800 h-10"
              />
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="role" className="text-sm font-medium">Role</Label>
              <Input
                id="role"
                value={profile.role}
                onChange={(e) => handleProfileChange('role', e.target.value)}
                placeholder="e.g. Product Manager"
                disabled={loading}
                className="h-10"
              />
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="timezone" className="text-sm font-medium">Timezone</Label>
              <Select value={profile.timezone} onValueChange={(value) => handleProfileChange('timezone', value)}>
                <SelectTrigger className="h-10">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC-12">UTC-12</SelectItem>
                  <SelectItem value="UTC-11">UTC-11</SelectItem>
                  <SelectItem value="UTC-10">UTC-10</SelectItem>
                  <SelectItem value="UTC-9">UTC-9</SelectItem>
                  <SelectItem value="UTC-8">UTC-8</SelectItem>
                  <SelectItem value="UTC-7">UTC-7</SelectItem>
                  <SelectItem value="UTC-6">UTC-6</SelectItem>
                  <SelectItem value="UTC-5">UTC-5</SelectItem>
                  <SelectItem value="UTC-4">UTC-4</SelectItem>
                  <SelectItem value="UTC-3">UTC-3</SelectItem>
                  <SelectItem value="UTC-2">UTC-2</SelectItem>
                  <SelectItem value="UTC-1">UTC-1</SelectItem>
                  <SelectItem value="UTC+0">UTC+0</SelectItem>
                  <SelectItem value="UTC+1">UTC+1</SelectItem>
                  <SelectItem value="UTC+2">UTC+2</SelectItem>
                  <SelectItem value="UTC+3">UTC+3</SelectItem>
                  <SelectItem value="UTC+4">UTC+4</SelectItem>
                  <SelectItem value="UTC+5">UTC+5</SelectItem>
                  <SelectItem value="UTC+6">UTC+6</SelectItem>
                  <SelectItem value="UTC+7">UTC+7</SelectItem>
                  <SelectItem value="UTC+8">UTC+8</SelectItem>
                  <SelectItem value="UTC+9">UTC+9</SelectItem>
                  <SelectItem value="UTC+10">UTC+10</SelectItem>
                  <SelectItem value="UTC+11">UTC+11</SelectItem>
                  <SelectItem value="UTC+12">UTC+12</SelectItem>
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
            <div className="space-y-6">
              <div className="flex items-center justify-between py-3">
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

          <div className="flex justify-between items-center mt-6">
            <Button 
              onClick={createTestNotifications}
              variant="outline"
              className="text-purple-600 border-purple-600 hover:bg-purple-50"
            >
              🔔 Test Notifications
            </Button>
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
            {t('settings.appearance')}
          </CardTitle>
          <CardDescription>Customize your interface preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="theme" className="text-sm font-medium">
                {t('settings.theme')}
              </Label>
              <div className="flex items-center gap-2">
                <Button
                  variant={theme === 'light' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTheme('light')}
                  className="px-3 py-1"
                >
                  ☀️ Light
                </Button>
                <Button
                  variant={theme === 'dark' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTheme('dark')}
                  className="px-3 py-1"
                >
                  🌙 Dark
                </Button>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="language" className="text-sm font-medium">
                {t('settings.language')}
              </Label>
              <Select value={currentLanguage} onValueChange={changeLanguage}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {availableLanguages.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.flag} {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card className="hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01] animate-fade-in-up animation-delay-300">
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
                  {t('settings.changePassword')}
                </Button>
              </ChangePasswordDialog>
            ) : (
              <div className="text-sm text-gray-500 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                Password change is not available for Google authentication users
              </div>
            )}
            
            <Button 
              variant="outline" 
              className="justify-start w-full sm:w-auto text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={() => toast({
                title: "Account Deletion",
                description: "Please contact support to delete your account",
                variant: "destructive",
              })}
            >
              {t('settings.deleteAccount')}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;