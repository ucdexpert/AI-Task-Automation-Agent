'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Bot, Mail, Lock, User, Loader2, ArrowRight, Sparkles } from 'lucide-react';

export default function SignupPage() {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [phoneNumber, setPhoneNumber] = useState<string>(''); // Added phoneNumber state
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Pass phoneNumber to the register function
      await register(email, password, fullName, phoneNumber);
      addToast('Identity created! Welcome to AgentX.', 'success');
      router.push('/dashboard');
    } catch (error) {
      addToast('Registration failed. Try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0C10] flex items-center justify-center p-6 selection:bg-accent-blue/30 overflow-hidden relative">
      {/* Background blobs */}
      <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-accent-blue/5 blur-[120px] rounded-full"></div>
      <div className="absolute top-[20%] -right-[5%] w-[30%] h-[30%] bg-purple-600/5 blur-[100px] rounded-full"></div>

      <div className="w-full max-w-[420px] relative z-10">
        <div className="text-center mb-10">
          <div className="w-12 h-12 bg-gradient-to-tr from-accent-blue to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-accent-blue/20">
            <Bot className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-black text-white uppercase italic tracking-tighter">
            Agent<span className="text-accent-blue">X</span> Signup
          </h1>
          <p className="text-slate-500 text-sm mt-2 font-medium">Initialize your automation core</p>
        </div>

        <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/5 p-8 rounded-[32px] shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Full Identity</label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Doe"
                  required
                  className="w-full h-12 bg-black/20 border border-white/5 rounded-xl pl-12 pr-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Phone Number</label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+1234567890"
                  className="w-full h-12 bg-black/20 border border-white/5 rounded-xl pl-12 pr-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Email Terminal</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  required
                  className="w-full h-12 bg-black/20 border border-white/5 rounded-xl pl-12 pr-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Access Protocol</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 characters"
                  required
                  className="w-full h-12 bg-black/20 border border-white/5 rounded-xl pl-12 pr-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 bg-accent-blue hover:bg-accent-blueDark disabled:bg-slate-800 text-white rounded-2xl font-black text-sm transition-all shadow-xl shadow-accent-blue/20 flex items-center justify-center gap-2 group mt-4"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>Create Identity <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
              )}
            </button>
          </form>

          <div className="mt-8 text-center border-t border-white/5 pt-6">
            <p className="text-slate-500 text-xs font-medium">
              Already initialized?{' '}
              <Link href="/login" className="text-accent-blue hover:underline font-bold">
                Connect Here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
