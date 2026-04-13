'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { api } from '@/lib/api';
import { ArrowLeft, User, Mail, Lock, Save } from 'lucide-react';
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
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const { addToast } = useToast();

  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

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
      });

      setProfile(response.data);
      addToast('Profile updated successfully', 'success');

      // Update auth context with new name
      localStorage.setItem('user', JSON.stringify(response.data));
      window.location.reload(); // Refresh to update navbar
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update profile';
      addToast(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) {
      addToast('Please fill in all password fields', 'error');
      return;
    }

    if (newPassword.length < 8) {
      addToast('New password must be at least 8 characters', 'error');
      return;
    }

    try {
      setSaving(true);
      await api.post('/api/profile/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      addToast('Password changed successfully', 'success');
      setCurrentPassword('');
      setNewPassword('');
      setShowPasswordSection(false);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to change password';
      addToast(message, 'error');
    } finally {
      setSaving(false);
    }
  };

  if (isLoading || loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-text-muted text-sm">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-4 md:px-6 py-6">
      <div className="max-w-[700px] mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-3 h-9 border border-text-primary text-text-primary text-sm rounded-md hover:bg-text-primary hover:text-background transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Profile Settings</h1>
            <p className="text-sm text-text-muted mt-1">Manage your account settings</p>
          </div>
        </div>

        {/* Profile Info Card */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-accent-blue/10 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-accent-blue" />
            </div>
            <h2 className="text-lg font-bold text-text-primary">Personal Information</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full h-11 px-4 bg-background border border-[rgba(255,255,255,0.08)] rounded-lg text-text-primary placeholder-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 px-4 bg-background border border-[rgba(255,255,255,0.08)] rounded-lg text-text-primary placeholder-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue"
                placeholder="your@email.com"
              />
            </div>

            <div className="pt-4">
              <button
                onClick={handleUpdateProfile}
                disabled={saving}
                className="flex items-center gap-2 px-4 h-11 bg-gradient-to-r from-accent-blue to-accent-blueDark text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                <Save className="w-4 h-4" />
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>

        {/* Account Info Card */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-accent-green/10 rounded-full flex items-center justify-center">
              <Mail className="w-5 h-5 text-accent-green" />
            </div>
            <h2 className="text-lg font-bold text-text-primary">Account Information</h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-text-muted mb-1">Account Created</p>
              <p className="text-sm text-text-primary font-medium">
                {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-text-muted mb-1">Status</p>
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                profile?.is_active ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-red/10 text-accent-red'
              }`}>
                {profile?.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* Password Change Card */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-6">
          <button
            onClick={() => setShowPasswordSection(!showPasswordSection)}
            className="w-full flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent-red/10 rounded-full flex items-center justify-center">
                <Lock className="w-5 h-5 text-accent-red" />
              </div>
              <h2 className="text-lg font-bold text-text-primary text-left">Change Password</h2>
            </div>
            <svg
              className={`w-5 h-5 text-text-muted transition-transform ${showPasswordSection ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showPasswordSection && (
            <div className="space-y-4 mt-6 pt-6 border-t border-[rgba(255,255,255,0.08)]">
              <PasswordInput
                label="Current Password"
                value={currentPassword}
                onChange={setCurrentPassword}
                placeholder="Enter current password"
              />

              <PasswordInput
                label="New Password"
                value={newPassword}
                onChange={setNewPassword}
                placeholder="Enter new password (min 8 chars)"
              />

              <button
                onClick={handleChangePassword}
                disabled={saving}
                className="w-full h-11 bg-accent-red hover:bg-red-600 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {saving ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
