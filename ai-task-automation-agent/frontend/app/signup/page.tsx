'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import PasswordInput from '@/components/ui/PasswordInput';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Bot } from 'lucide-react';

export default function SignupPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [fullNameError, setFullNameError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [confirmPasswordError, setConfirmPasswordError] = useState('');
  
  const [fullNameTouched, setFullNameTouched] = useState(false);
  const [emailTouched, setEmailTouched] = useState(false);
  const [passwordTouched, setPasswordTouched] = useState(false);
  const [confirmPasswordTouched, setConfirmPasswordTouched] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();
  const { addToast } = useToast();

  const validateFullName = (value: string) => {
    if (!value.trim()) return 'Full name is required';
    return '';
  };

  const validateEmail = (value: string) => {
    if (!value) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Please enter a valid email';
    return '';
  };

  const validatePassword = (value: string) => {
    if (!value) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    return '';
  };

  const validateConfirmPassword = (value: string) => {
    if (!value) return 'Please confirm your password';
    if (value !== password) return 'Passwords do not match';
    return '';
  };

  const handleBlur = (field: string) => {
    switch (field) {
      case 'fullName':
        setFullNameTouched(true);
        setFullNameError(validateFullName(fullName));
        break;
      case 'email':
        setEmailTouched(true);
        setEmailError(validateEmail(email));
        break;
      case 'password':
        setPasswordTouched(true);
        setPasswordError(validatePassword(password));
        break;
      case 'confirmPassword':
        setConfirmPasswordTouched(true);
        setConfirmPasswordError(validateConfirmPassword(confirmPassword));
        break;
    }
  };

  const calculatePasswordStrength = (pwd: string): number => {
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (/[A-Z]/.test(pwd)) strength++;
    if (/[0-9]/.test(pwd)) strength++;
    if (/[^A-Za-z0-9]/.test(pwd)) strength++;
    return strength;
  };

  const passwordStrength = calculatePasswordStrength(password);
  const strengthColors = ['#EF4444', '#F97316', '#EAB308', '#22C55E'];
  const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const nameErr = validateFullName(fullName);
    const emailErr = validateEmail(email);
    const pwdErr = validatePassword(password);
    const confirmErr = validateConfirmPassword(confirmPassword);
    
    setFullNameError(nameErr);
    setEmailError(emailErr);
    setPasswordError(pwdErr);
    setConfirmPasswordError(confirmErr);
    setFullNameTouched(true);
    setEmailTouched(true);
    setPasswordTouched(true);
    setConfirmPasswordTouched(true);

    if (nameErr || emailErr || pwdErr || confirmErr) return;

    setLoading(true);

    try {
      await register(email, password, fullName);
      addToast('Account created successfully!', 'success');
      router.push('/dashboard');
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed. Please try again.';
      addToast(message, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-[420px]">
        {/* Card */}
        <div className="bg-card rounded-xl border border-[rgba(255,255,255,0.08)] p-8">
          {/* Logo & Title */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-accent-blue to-accent-blueDark rounded-2xl mb-3">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-text-primary">Create your account</h1>
            <p className="text-text-muted text-sm mt-2">Start automating your tasks with AI</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div className="space-y-1">
              <label htmlFor="fullName" className="block text-sm font-medium text-text-primary">
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                onBlur={() => handleBlur('fullName')}
                placeholder="John Doe"
                className={`w-full h-11 px-4 bg-background border ${
                  fullNameTouched && fullNameError ? 'border-accent-red' : 'border-[rgba(255,255,255,0.08)]'
                } rounded-lg text-text-primary placeholder-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent transition-all`}
              />
              {fullNameTouched && fullNameError && (
                <p className="text-xs text-accent-red mt-1">{fullNameError}</p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-1">
              <label htmlFor="email" className="block text-sm font-medium text-text-primary">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => handleBlur('email')}
                placeholder="you@example.com"
                className={`w-full h-11 px-4 bg-background border ${
                  emailTouched && emailError ? 'border-accent-red' : 'border-[rgba(255,255,255,0.08)]'
                } rounded-lg text-text-primary placeholder-text-muted text-sm focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent transition-all`}
              />
              {emailTouched && emailError && (
                <p className="text-xs text-accent-red mt-1">{emailError}</p>
              )}
            </div>

            {/* Password */}
            <PasswordInput
              label="Password"
              value={password}
              onChange={setPassword}
              error={passwordTouched ? passwordError : ''}
              onBlur={() => handleBlur('password')}
            />

            {/* Password Strength Meter */}
            {password && (
              <div className="space-y-1">
                <div className="flex gap-1">
                  {[0, 1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-1 flex-1 rounded-full bg-[rgba(255,255,255,0.08)] overflow-hidden"
                    >
                      <div
                        className="h-full transition-all duration-200"
                        style={{
                          width: i < passwordStrength ? '100%' : '0%',
                          backgroundColor: i < passwordStrength ? strengthColors[passwordStrength - 1] : 'transparent',
                        }}
                      />
                    </div>
                  ))}
                </div>
                <p className="text-xs text-text-muted">{strengthLabels[passwordStrength - 1] || ''}</p>
              </div>
            )}

            {/* Confirm Password */}
            <PasswordInput
              label="Confirm Password"
              value={confirmPassword}
              onChange={setConfirmPassword}
              error={confirmPasswordTouched ? confirmPasswordError : ''}
              onBlur={() => handleBlur('confirmPassword')}
            />

            {/* Sign Up Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-gradient-to-r from-accent-blue to-accent-blueDark text-white font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 mt-6"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span>Creating account...</span>
                </>
              ) : (
                'Sign Up'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center text-sm text-text-muted">
            Already have an account?{' '}
            <Link href="/login" className="text-accent-blue hover:underline font-medium">
              Login
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
