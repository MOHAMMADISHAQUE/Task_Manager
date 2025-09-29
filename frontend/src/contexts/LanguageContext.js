import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language translations
const translations = {
  en: {
    // Navigation
    dashboard: 'Dashboard',
    tasks: 'Tasks',
    projects: 'Projects',
    analytics: 'Analytics',
    settings: 'Settings',
    
    // Common
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    update: 'Update',
    loading: 'Loading...',
    success: 'Success',
    error: 'Error',
    
    // Dashboard
    'dashboard.welcome': 'Welcome back! Here\'s what\'s happening with your tasks.',
    'dashboard.totalTasks': 'Total Tasks',
    'dashboard.completedTasks': 'Completed',
    'dashboard.inProgressTasks': 'In Progress',
    'dashboard.overdueTasks': 'Overdue',
    
    // Tasks
    'tasks.title': 'Tasks',
    'tasks.description': 'Manage and track all your tasks in one place.',
    'tasks.createTask': 'Create Task',
    'tasks.smartCreator': 'Smart Task Creator',
    'tasks.aiPowered': 'AI Powered',
    'tasks.placeholder': 'Remind me to...',
    
    // Settings
    'settings.title': 'Settings',
    'settings.description': 'Manage your account settings and preferences.',
    'settings.profile': 'Profile Settings',
    'settings.notifications': 'Notification Settings',
    'settings.appearance': 'Appearance',
    'settings.security': 'Security',
    'settings.theme': 'Theme',
    'settings.language': 'Language',
    'settings.changePassword': 'Change Password',
    'settings.deleteAccount': 'Delete Account'
  },
  es: {
    // Navigation
    dashboard: 'Panel',
    tasks: 'Tareas',
    projects: 'Proyectos',
    analytics: 'Análisis',
    settings: 'Configuración',
    
    // Common
    save: 'Guardar',
    cancel: 'Cancelar',
    delete: 'Eliminar',
    edit: 'Editar',
    create: 'Crear',
    update: 'Actualizar',
    loading: 'Cargando...',
    success: 'Éxito',
    error: 'Error',
    
    // Dashboard
    'dashboard.welcome': '¡Bienvenido de nuevo! Esto es lo que está pasando con tus tareas.',
    'dashboard.totalTasks': 'Tareas Totales',
    'dashboard.completedTasks': 'Completadas',
    'dashboard.inProgressTasks': 'En Progreso',
    'dashboard.overdueTasks': 'Vencidas',
    
    // Tasks
    'tasks.title': 'Tareas',
    'tasks.description': 'Gestiona y rastrea todas tus tareas en un solo lugar.',
    'tasks.createTask': 'Crear Tarea',
    'tasks.smartCreator': 'Creador Inteligente de Tareas',
    'tasks.aiPowered': 'Con IA',
    'tasks.placeholder': 'Recuérdame...',
    
    // Settings
    'settings.title': 'Configuración',
    'settings.description': 'Gestiona la configuración de tu cuenta y preferencias.',
    'settings.profile': 'Configuración de Perfil',
    'settings.notifications': 'Configuración de Notificaciones',
    'settings.appearance': 'Apariencia',
    'settings.security': 'Seguridad',
    'settings.theme': 'Tema',
    'settings.language': 'Idioma',
    'settings.changePassword': 'Cambiar Contraseña',
    'settings.deleteAccount': 'Eliminar Cuenta'
  },
  fr: {
    // Navigation
    dashboard: 'Tableau de Bord',
    tasks: 'Tâches',
    projects: 'Projets',
    analytics: 'Analyses',
    settings: 'Paramètres',
    
    // Common
    save: 'Enregistrer',
    cancel: 'Annuler',
    delete: 'Supprimer',
    edit: 'Modifier',
    create: 'Créer',
    update: 'Mettre à jour',
    loading: 'Chargement...',
    success: 'Succès',
    error: 'Erreur',
    
    // Dashboard
    'dashboard.welcome': 'Bon retour ! Voici ce qui se passe avec vos tâches.',
    'dashboard.totalTasks': 'Tâches Totales',
    'dashboard.completedTasks': 'Terminées',
    'dashboard.inProgressTasks': 'En Cours',
    'dashboard.overdueTasks': 'En Retard',
    
    // Tasks
    'tasks.title': 'Tâches',
    'tasks.description': 'Gérez et suivez toutes vos tâches en un seul endroit.',
    'tasks.createTask': 'Créer une Tâche',
    'tasks.smartCreator': 'Créateur Intelligent de Tâches',
    'tasks.aiPowered': 'Alimenté par IA',
    'tasks.placeholder': 'Rappelle-moi de...',
    
    // Settings
    'settings.title': 'Paramètres',
    'settings.description': 'Gérez les paramètres de votre compte et vos préférences.',
    'settings.profile': 'Paramètres de Profil',
    'settings.notifications': 'Paramètres de Notification',
    'settings.appearance': 'Apparence',
    'settings.security': 'Sécurité',
    'settings.theme': 'Thème',
    'settings.language': 'Langue',
    'settings.changePassword': 'Changer le Mot de Passe',
    'settings.deleteAccount': 'Supprimer le Compte'
  },
  de: {
    // Navigation
    dashboard: 'Dashboard',
    tasks: 'Aufgaben',
    projects: 'Projekte',
    analytics: 'Analysen',
    settings: 'Einstellungen',
    
    // Common
    save: 'Speichern',
    cancel: 'Abbrechen',
    delete: 'Löschen',
    edit: 'Bearbeiten',
    create: 'Erstellen',
    update: 'Aktualisieren',
    loading: 'Lädt...',
    success: 'Erfolg',
    error: 'Fehler',
    
    // Dashboard
    'dashboard.welcome': 'Willkommen zurück! Hier ist, was mit Ihren Aufgaben passiert.',
    'dashboard.totalTasks': 'Aufgaben Gesamt',
    'dashboard.completedTasks': 'Abgeschlossen',
    'dashboard.inProgressTasks': 'In Bearbeitung',
    'dashboard.overdueTasks': 'Überfällig',
    
    // Tasks
    'tasks.title': 'Aufgaben',
    'tasks.description': 'Verwalten und verfolgen Sie alle Ihre Aufgaben an einem Ort.',
    'tasks.createTask': 'Aufgabe Erstellen',
    'tasks.smartCreator': 'Intelligenter Aufgaben-Ersteller',
    'tasks.aiPowered': 'KI-gestützt',
    'tasks.placeholder': 'Erinnere mich daran...',
    
    // Settings
    'settings.title': 'Einstellungen',
    'settings.description': 'Verwalten Sie Ihre Kontoeinstellungen und Präferenzen.',
    'settings.profile': 'Profil-Einstellungen',
    'settings.notifications': 'Benachrichtigungseinstellungen',
    'settings.appearance': 'Erscheinungsbild',
    'settings.security': 'Sicherheit',
    'settings.theme': 'Design',
    'settings.language': 'Sprache',
    'settings.changePassword': 'Passwort Ändern',
    'settings.deleteAccount': 'Konto Löschen'
  },
  zh: {
    // Navigation
    dashboard: '仪表板',
    tasks: '任务',
    projects: '项目',
    analytics: '分析',
    settings: '设置',
    
    // Common
    save: '保存',
    cancel: '取消',
    delete: '删除',
    edit: '编辑',
    create: '创建',
    update: '更新',
    loading: '加载中...',
    success: '成功',
    error: '错误',
    
    // Dashboard
    'dashboard.welcome': '欢迎回来！这是您任务的最新情况。',
    'dashboard.totalTasks': '总任务数',
    'dashboard.completedTasks': '已完成',
    'dashboard.inProgressTasks': '进行中',
    'dashboard.overdueTasks': '已逾期',
    
    // Tasks
    'tasks.title': '任务',
    'tasks.description': '在一个地方管理和跟踪您的所有任务。',
    'tasks.createTask': '创建任务',
    'tasks.smartCreator': '智能任务创建器',
    'tasks.aiPowered': 'AI 驱动',
    'tasks.placeholder': '提醒我...',
    
    // Settings
    'settings.title': '设置',
    'settings.description': '管理您的帐户设置和偏好。',
    'settings.profile': '个人资料设置',
    'settings.notifications': '通知设置',
    'settings.appearance': '外观',
    'settings.security': '安全',
    'settings.theme': '主题',
    'settings.language': '语言',
    'settings.changePassword': '更改密码',
    'settings.deleteAccount': '删除帐户'
  }
};

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'zh', name: '中文', flag: '🇨🇳' }
];

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');

  useEffect(() => {
    // Load language from localStorage
    const savedLanguage = localStorage.getItem('smarttask-language');
    if (savedLanguage && translations[savedLanguage]) {
      setCurrentLanguage(savedLanguage);
    } else {
      // Try to detect browser language
      const browserLang = navigator.language.split('-')[0];
      if (translations[browserLang]) {
        setCurrentLanguage(browserLang);
      }
    }
  }, []);

  const changeLanguage = (languageCode) => {
    if (translations[languageCode]) {
      setCurrentLanguage(languageCode);
      localStorage.setItem('smarttask-language', languageCode);
    }
  };

  const t = (key) => {
    return translations[currentLanguage]?.[key] || translations['en'][key] || key;
  };

  const value = {
    currentLanguage,
    changeLanguage,
    t,
    languages,
    availableLanguages: languages
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};