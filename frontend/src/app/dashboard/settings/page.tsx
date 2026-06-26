"use client";

import React, { useState } from "react";
import { useApp } from "@/context/AppContext";
import { 
  User, 
  Settings as SettingsIcon, 
  ShieldAlert, 
  Camera, 
  Check, 
  Sparkles, 
  HelpCircle,
  Bell,
  Trash2,
  Lock,
  Languages,
  ChevronDown
} from "lucide-react";

export default function SettingsPage() {
  const { userProfile, settings, updateUserProfile, updateSettings } = useApp();

  // Tabs
  const [activeTab, setActiveTab] = useState<"profile" | "language" | "account">("profile");

  // Profile Form State
  const [profileName, setProfileName] = useState(userProfile.name);
  const [profileEmail, setProfileEmail] = useState(userProfile.email);
  const [profileRole, setProfileRole] = useState(userProfile.role);
  const [isProfileSaved, setIsProfileSaved] = useState(false);

  // Language Preferences State
  const [defaultSourceLang, setDefaultSourceLang] = useState(settings.defaultSourceLang);
  const [preferredTargetLangs, setPreferredTargetLangs] = useState<string[]>(settings.preferredTargetLangs);
  const [defaultAiModel, setDefaultAiModel] = useState(settings.defaultAiModel);
  const [translationMemory, setTranslationMemory] = useState(settings.translationMemory);
  const [autoApprove, setAutoApprove] = useState(settings.autoApproveHighConfidence);
  const [isLanguageSaved, setIsLanguageSaved] = useState(false);
  const [isTargetLangOpen, setIsTargetLangOpen] = useState(false);

  // Password / Notifications State
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [notifUpload, setNotifUpload] = useState(settings.emailNotifications.uploadSuccess);
  const [notifComplete, setNotifComplete] = useState(settings.emailNotifications.localizationComplete);
  const [notifAlerts, setNotifAlerts] = useState(settings.emailNotifications.systemAlerts);
  const [isAccountSaved, setIsAccountSaved] = useState(false);

  // Constants
  const SUPPORTED_LANGUAGES = ["Tamil", "Hindi", "Spanish", "French", "German", "Japanese", "Arabic", "Portuguese"];

  const handleProfileSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateUserProfile({
      name: profileName,
      email: profileEmail,
      role: profileRole,
      avatar: profileName.split(" ").map(n => n[0]).join("").toUpperCase()
    });
    setIsProfileSaved(true);
    setTimeout(() => setIsProfileSaved(false), 2000);
  };

  const handleLanguageSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings({
      defaultSourceLang,
      preferredTargetLangs,
      defaultAiModel,
      translationMemory,
      autoApproveHighConfidence: autoApprove
    });
    setIsLanguageSaved(true);
    setTimeout(() => setIsLanguageSaved(false), 2000);
  };

  const handleAccountSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings({
      emailNotifications: {
        uploadSuccess: notifUpload,
        localizationComplete: notifComplete,
        systemAlerts: notifAlerts
      }
    });
    
    if (newPassword) {
      if (newPassword !== confirmPassword) {
        alert("New passwords do not match!");
        return;
      }
      alert("Password updated successfully!");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    }

    setIsAccountSaved(true);
    setTimeout(() => setIsAccountSaved(false), 2000);
  };

  const toggleTargetLanguage = (lang: string) => {
    if (preferredTargetLangs.includes(lang)) {
      setPreferredTargetLangs(prev => prev.filter(l => l !== lang));
    } else {
      setPreferredTargetLangs(prev => [...prev, lang]);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-heading font-black text-2xl text-white">System Settings</h2>
        <p className="text-sm text-slate-400">Configure language mappings, translation models, and user details</p>
      </div>

      {/* Custom Tabs Navigation */}
      <div className="flex border-b border-border-custom bg-white/2 p-1.5 rounded-xl self-start w-fit">
        <button
          onClick={() => setActiveTab("profile")}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "profile" 
              ? "bg-accent-violet text-white glow-violet" 
              : "text-slate-400 hover:text-white"
          }`}
        >
          <User className="w-3.5 h-3.5" /> Profile
        </button>
        <button
          onClick={() => setActiveTab("language")}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "language" 
              ? "bg-accent-violet text-white glow-violet" 
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Languages className="w-3.5 h-3.5" /> Language Preferences
        </button>
        <button
          onClick={() => setActiveTab("account")}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
            activeTab === "account" 
              ? "bg-accent-violet text-white glow-violet" 
              : "text-slate-400 hover:text-white"
          }`}
        >
          <SettingsIcon className="w-3.5 h-3.5" /> Account & Security
        </button>
      </div>

      {/* PROFILE TAB PANEL */}
      {activeTab === "profile" && (
        <div className="glass-panel rounded-2xl p-6 border border-border-custom max-w-2xl">
          <form onSubmit={handleProfileSave} className="space-y-6">
            
            {/* Avatar Row */}
            <div className="flex items-center gap-6">
              <div className="relative group cursor-pointer w-20 h-20 rounded-full bg-gradient-to-tr from-accent-violet to-accent-cyan flex items-center justify-center font-heading font-black text-xl text-white glow-violet border border-border-custom">
                {profileName.split(" ").map(n => n[0]).join("").toUpperCase()}
                <div className="absolute inset-0 bg-black/60 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-white">Avatar Profile Image</h4>
                <p className="text-xs text-slate-500 mt-0.5">Click overlay to select a custom file (PNG/JPG)</p>
              </div>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={profileName}
                  onChange={(e) => setProfileName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white placeholder-slate-500 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={profileEmail}
                  onChange={(e) => setProfileEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white placeholder-slate-500 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  Platform Role
                </label>
                <select
                  value={profileRole}
                  onChange={(e) => setProfileRole(e.target.value as "Instructor" | "Admin")}
                  className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white outline-none cursor-pointer transition-all"
                >
                  <option value="Instructor">Instructor</option>
                  <option value="Admin">Admin</option>
                </select>
              </div>
            </div>

            <div className="h-px bg-border-custom/50" />

            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl text-xs font-bold text-white relative overflow-hidden bg-accent-violet hover:scale-105 active:scale-95 transition-all glow-violet"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-accent-violet to-accent-violet-light" />
              <span className="relative z-10 flex items-center gap-1.5">
                {isProfileSaved ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" /> Changes Saved
                  </>
                ) : (
                  "Save Changes"
                )}
              </span>
            </button>

          </form>
        </div>
      )}

      {/* LANGUAGE PREFERENCES TAB PANEL */}
      {activeTab === "language" && (
        <div className="glass-panel rounded-2xl p-6 border border-border-custom max-w-2xl">
          <form onSubmit={handleLanguageSave} className="space-y-6">
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              
              {/* Default source */}
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  Default Source Language
                </label>
                <select
                  value={defaultSourceLang}
                  onChange={(e) => setDefaultSourceLang(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white outline-none cursor-pointer transition-all"
                >
                  <option value="English">English</option>
                  <option value="Spanish">Spanish</option>
                  <option value="German">German</option>
                  <option value="Japanese">Japanese</option>
                </select>
              </div>

              {/* Preferred target */}
              <div className="relative">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                  Preferred Target Languages
                </label>
                <div
                  onClick={() => setIsTargetLangOpen(!isTargetLangOpen)}
                  className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white cursor-pointer flex items-center justify-between select-none"
                >
                  <span className="text-slate-400 text-sm">
                    {preferredTargetLangs.length === 0 ? "Select preferred target" : `${preferredTargetLangs.length} preferred`}
                  </span>
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                </div>

                {isTargetLangOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setIsTargetLangOpen(false)} />
                    <div className="absolute left-0 right-0 mt-2 z-20 rounded-xl bg-bg-secondary border border-border-custom p-2 max-h-48 overflow-y-auto shadow-2xl">
                      {SUPPORTED_LANGUAGES.map((lang) => (
                        <div
                          key={lang}
                          onClick={() => toggleTargetLanguage(lang)}
                          className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-white/5 text-sm text-slate-300 cursor-pointer select-none"
                        >
                          <span>{lang}</span>
                          {preferredTargetLangs.includes(lang) && <Check className="w-4 h-4 text-accent-cyan" />}
                        </div>
                      ))}
                    </div>
                  </>
                )}

                <div className="flex flex-wrap gap-1 mt-2">
                  {preferredTargetLangs.map((lang) => (
                    <span key={lang} className="text-[10px] bg-accent-violet/10 border border-accent-violet/20 text-accent-violet-light px-2 py-0.5 rounded">
                      {lang}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Model preference */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                Default AI Model Selector
              </label>
              <div className="grid grid-cols-3 gap-3 max-w-md">
                {["Fast", "Balanced", "High Accuracy"].map((model) => (
                  <button
                    key={model}
                    type="button"
                    onClick={() => setDefaultAiModel(model as any)}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold text-center transition-all ${
                      defaultAiModel === model
                        ? "border-accent-violet bg-accent-violet/5 text-white"
                        : "border-border-custom text-slate-400 hover:text-white hover:bg-white/2"
                    }`}
                  >
                    {model}
                  </button>
                ))}
              </div>
            </div>

            {/* Toggle checkboxes */}
            <div className="space-y-4 pt-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={translationMemory}
                  onChange={(e) => setTranslationMemory(e.target.checked)}
                  className="w-4 h-4 rounded border-border-custom bg-bg-primary text-accent-violet focus:ring-accent-violet"
                />
                <div>
                  <span className="text-sm font-semibold text-white block">Enable Translation Memory</span>
                  <span className="text-[10px] text-slate-500 block">Saves and auto-applies approved translations for identical sentences.</span>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoApprove}
                  onChange={(e) => setAutoApprove(e.target.checked)}
                  className="w-4 h-4 rounded border-border-custom bg-bg-primary text-accent-violet focus:ring-accent-violet"
                />
                <div>
                  <span className="text-sm font-semibold text-white block">Auto-approve High Confidence Blocks</span>
                  <span className="text-[10px] text-slate-500 block">Skips manual review and automatically publishes segments with 95%+ confidence scores.</span>
                </div>
              </label>
            </div>

            <div className="h-px bg-border-custom/50" />

            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl text-xs font-bold text-white relative overflow-hidden bg-accent-violet hover:scale-105 active:scale-95 transition-all glow-violet"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-accent-violet to-accent-violet-light" />
              <span className="relative z-10 flex items-center gap-1.5">
                {isLanguageSaved ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" /> Settings Saved
                  </>
                ) : (
                  "Save Preferences"
                )}
              </span>
            </button>

          </form>
        </div>
      )}

      {/* ACCOUNT & SECURITY TAB PANEL */}
      {activeTab === "account" && (
        <div className="space-y-6 max-w-2xl">
          
          {/* Security details form */}
          <div className="glass-panel rounded-2xl p-6 border border-border-custom">
            <form onSubmit={handleAccountSave} className="space-y-6">
              <h3 className="font-heading font-bold text-base text-white flex items-center gap-2">
                <Lock className="w-4 h-4 text-accent-cyan" /> Security & Notification Rules
              </h3>

              {/* Password change inputs */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white placeholder-slate-600 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white placeholder-slate-600 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-bg-primary/60 border border-border-custom focus:border-accent-violet focus:ring-1 focus:ring-accent-violet text-sm text-white placeholder-slate-600 outline-none transition-all"
                  />
                </div>
              </div>

              <div className="h-px bg-border-custom/50" />

              {/* Notifications */}
              <div className="space-y-4">
                <h4 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
                  <Bell className="w-4 h-4 text-accent-violet-light" /> Email Notification Preferences
                </h4>
                
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifUpload}
                      onChange={(e) => setNotifUpload(e.target.checked)}
                      className="w-4 h-4 rounded border-border-custom bg-bg-primary text-accent-violet focus:ring-accent-violet"
                    />
                    <span className="text-xs text-slate-300 font-semibold">Notify me when asset file completes uploading</span>
                  </label>
                  
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifComplete}
                      onChange={(e) => setNotifComplete(e.target.checked)}
                      className="w-4 h-4 rounded border-border-custom bg-bg-primary text-accent-violet focus:ring-accent-violet"
                    />
                    <span className="text-xs text-slate-300 font-semibold">Notify me when localization is fully completed by AI cluster</span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifAlerts}
                      onChange={(e) => setNotifAlerts(e.target.checked)}
                      className="w-4 h-4 rounded border-border-custom bg-bg-primary text-accent-violet focus:ring-accent-violet"
                    />
                    <span className="text-xs text-slate-300 font-semibold">Receive critical platform health system alerts</span>
                  </label>
                </div>
              </div>

              <div className="h-px bg-border-custom/50" />

              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl text-xs font-bold text-white relative overflow-hidden bg-accent-violet hover:scale-105 active:scale-95 transition-all glow-violet"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-accent-violet to-accent-violet-light" />
                <span className="relative z-10 flex items-center gap-1.5">
                  {isAccountSaved ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-white" /> Changes Saved
                    </>
                  ) : (
                    "Save Security Settings"
                  )}
                </span>
              </button>
            </form>
          </div>

          {/* Danger zone */}
          <div className="glass-panel rounded-2xl p-6 border border-rose-500/20 bg-rose-500/2">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <h4 className="text-sm font-semibold text-rose-400 flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-rose-500" /> Danger Zone
                </h4>
                <p className="text-xs text-slate-500">Deleting this account will permanently clear translation memories and catalog courses.</p>
              </div>

              <button
                onClick={() => {
                  if (confirm("WARNING: Are you sure you want to permanently delete this account? This cannot be undone.")) {
                    alert("Account deletion sequence initiated.");
                  }
                }}
                className="px-4 py-2 rounded-xl text-xs font-bold text-rose-400 border border-rose-500/25 hover:border-rose-500 hover:bg-rose-500/10 transition-all flex items-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" /> Delete Account
              </button>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
