'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { api } from '@/lib/api';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Lock, 
  Save, 
  Shield, 
  Fingerprint, 
  Calendar as CalendarIcon,
  ChevronRight,
  LogOut,
  Sparkles,
  Activity
} from 'lucide-react';
import Link from 'next/link';
import PasswordInput from '@/components/ui/PasswordInput';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface ProfileData {
  id: number;
  email: string;
  full_name: string | null;
  created_at: string;
  is_active: boolean;
}

export default function ProfilePage() {
  const { isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const { addToast } = useToast();

  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState(''); // Added phoneNumber state

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showPasswordSection, setShowPasswordSection] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadProfile();
    }
  }, [isAuthenticated]);

  const loadProfile = async () => {
    try {
      const response = await api.get('/api/profile/me');
      setProfile(response.data);
      setFullName(response.data.full_name || '');
      setEmail(response.data.email);
      setPhoneNumber(response.data.phone_number || ''); // Set phone number on load
    } catch (error) {
      console.error('Failed to load profile:', error);
      addToast('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    try {
      setSaving(true);
      const response = await api.put('/api/profile/me', {
        full_name: fullName,
        email: email,
        phone_number: phoneNumber, // Include phone number in update
      });

      setProfile(response.data);
      addToast('Identity profile synchronized!', 'success');

      // Update auth context with new name
      localStorage.setItem('user', JSON.stringify(response.data));
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update profile';
      addToast(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) {
      addToast('Security fields required', 'error');
      return;
    }

    try {
      setSaving(true);
      await api.post('/api/profile/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      addToast('Security protocol updated!', 'success');
      setCurrentPassword('');
      setNewPassword('');
      setShowPasswordSection(false);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Security update failed';
      addToast(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-[#0A0C10] flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0C10] text-slate-200 selection:bg-accent-blue/30 relative overflow-hidden">
      {/* Background blobs */}
      <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-accent-blue/5 blur-[120px] rounded-full"></div>
      
      <div className="max-w-[800px] mx-auto px-6 py-12 relative z-10">
        
        {/* Navigation */}
        <div className="flex items-center justify-between mb-12">
          <Link
            href="/dashboard"
            className="group flex items-center gap-2 text-slate-500 hover:text-white transition-colors font-bold text-sm"
          >
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Terminal Home
          </Link>
          <button 
            onClick={() => logout()}
            className="flex items-center gap-2 text-accent-red/80 hover:text-accent-red font-bold text-sm transition-colors"
          >
            <LogOut className="w-4 h-4" /> Disconnect
          </button>
        </div>

        {/* Profile Identity Header */}
        <div className="flex flex-col md:flex-row items-center gap-8 mb-12 p-8 bg-white/[0.03] border border-white/5 rounded-[40px] backdrop-blur-xl">
           <div className="w-24 h-24 bg-gradient-to-tr from-accent-blue to-purple-500 rounded-3xl flex items-center justify-center shadow-2xl shadow-accent-blue/20 ring-4 ring-white/5">
              <Fingerprint className="w-12 h-12 text-white" />
           </div>
           <div className="text-center md:text-left">
              <h1 className="text-3xl font-black text-white uppercase tracking-tighter italic">
                {profile?.full_name || 'Anonymous Agent'}
              </h1>
              <p className="text-slate-500 font-medium mt-1">{profile?.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-2 mt-4">
                 <span className="px-3 py-1 bg-accent-blue/10 text-accent-blue text-[10px] font-black uppercase rounded-full border border-accent-blue/20">
                   Level: Senior Operator
                 </span>
                 <span className="px-3 py-1 bg-accent-green/10 text-accent-green text-[10px] font-black uppercase rounded-full border border-accent-green/20">
                   Status: {profile?.is_active ? 'Online' : 'Offline'}
                 </span>
              </div>
           </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Main Config (8 Cols) */}
          <div className="md:col-span-8 space-y-8">
            
            {/* Identity Configuration */}
            <div className="bg-card rounded-[32px] border border-white/5 p-8 relative group">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-8 h-8 bg-accent-blue/10 rounded-xl flex items-center justify-center">
                  <User className="w-4 h-4 text-accent-blue" />
                </div>
                <h2 className="text-sm font-black text-white uppercase tracking-widest">Identity Config</h2>
              </div>

              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Full Designation</label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full h-12 bg-black/20 border border-white/5 rounded-xl px-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">System Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-12 bg-black/20 border border-white/5 rounded-xl px-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                  />
                  </div>
                  </div>

                  {/* Phone Number Configuration */}
                  <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Contact Number</label>
                  <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="+1234567890"
                    className="w-full h-12 bg-black/20 border border-white/5 rounded-xl px-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                  />
                  </div>
                  </div>

                  <button
                  onClick={handleUpdateProfile}
                  disabled={saving}
                  className="flex items-center gap-2 px-8 h-12 bg-accent-blue hover:bg-accent-blueDark text-white font-black text-xs uppercase tracking-widest rounded-2xl transition-all shadow-xl shadow-accent-blue/20 disabled:opacity-50"
                  >
                  <Save className="w-4 h-4" />
                  {saving ? 'Syncing...' : 'Update Protocol'}
                  </button>
            </div>

            {/* Security Overrides */}
            <div className="bg-card rounded-[32px] border border-white/5 p-8">
              <button
                onClick={() => setShowPasswordSection(!showPasswordSection)}
                className="w-full flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-accent-red/10 rounded-xl flex items-center justify-center">
                    <Lock className="w-4 h-4 text-accent-red" />
                  </div>
                  <h2 className="text-sm font-black text-white uppercase tracking-widest">Security Overrides</h2>
                </div>
                <ChevronRight className={`w-5 h-5 text-slate-600 transition-transform ${showPasswordSection ? 'rotate-90' : ''}`} />
              </button>

              {showPasswordSection && (
                <div className="space-y-6 mt-8 pt-8 border-t border-white/5 animate-in slide-in-from-top-4 duration-300">
                  <div className="space-y-4">
                    <PasswordInput
                      label="Current Access Key"
                      value={currentPassword}
                      onChange={setCurrentPassword}
                    />
                    <PasswordInput
                      label="New Access Key"
                      value={newPassword}
                      onChange={setNewPassword}
                    />
                  </div>
                  <button
                    onClick={handleChangePassword}
                    disabled={saving}
                    className="w-full h-12 bg-accent-red/10 hover:bg-accent-red/20 text-accent-red font-black text-xs uppercase tracking-widest rounded-2xl border border-accent-red/20 transition-all"
                  >
                    Authorize Change
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Metadata Sidebar (4 Cols) */}
          <div className="md:col-span-4 space-y-6">
            <div className="bg-white/[0.02] border border-white/5 rounded-[32px] p-6">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-6">System Metadata</h3>
              
              <div className="space-y-6">
                <div className="flex items-start gap-3">
                  <CalendarIcon className="w-4 h-4 text-accent-blue mt-0.5" />
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Initialized On</p>
                    <p className="text-sm font-medium text-white">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Shield className="w-4 h-4 text-accent-green mt-0.5" />
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Security Level</p>
                    <p className="text-sm font-medium text-white">Encrypted AES-256</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Activity className="w-4 h-4 text-yellow-500 mt-0.5" />
                  <div>
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">Authorization</p>
                    <p className="text-sm font-medium text-white">Full Access</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-accent-blue/10 to-purple-500/10 border border-white/5 rounded-[32px] p-6">
               <div className="flex items-center gap-2 mb-2 text-accent-blue">
                  <Sparkles className="w-4 h-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">Operator Note</span>
               </div>
               <p className="text-xs text-slate-500 leading-relaxed italic">
                 "Your identity is linked to all automation sequences. Keep your access keys secure."
               </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
