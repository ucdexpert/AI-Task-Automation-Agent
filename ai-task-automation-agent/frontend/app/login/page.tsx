'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Bot, Mail, Lock, Loader2, ArrowRight, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      addToast('Welcome back to AgentX!', 'success');
      router.push('/dashboard');
    } catch (error) {
      addToast('Invalid email or password', 'error');
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
            Agent<span className="text-accent-blue">X</span> Login
          </h1>
          <p className="text-slate-500 text-sm mt-2 font-medium">Continue your automation sequence</p>
        </div>

        <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/5 p-8 rounded-[32px] shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
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
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">Secure Protocol</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-accent-blue transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full h-12 bg-black/20 border border-white/5 rounded-xl pl-12 pr-4 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-accent-blue/50 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-12 bg-accent-blue hover:bg-accent-blueDark disabled:bg-slate-800 text-white rounded-2xl font-black text-sm transition-all shadow-xl shadow-accent-blue/20 flex items-center justify-center gap-2 group"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>Connect to Agent <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" /></>
              )}
            </button>
          </form>

          <div className="mt-8 text-center border-t border-white/5 pt-6">
            <p className="text-slate-500 text-xs font-medium">
              New to AgentX?{' '}
              <Link href="/signup" className="text-accent-blue hover:underline font-bold">
                Create Identity
              </Link>
            </p>
          </div>
        </div>

        <div className="mt-8 flex items-center justify-center gap-2 text-slate-600">
           <Sparkles className="w-4 h-4" />
           <span className="text-[10px] font-black uppercase tracking-tighter">Powered by Llama 3.3 70B</span>
        </div>
      </div>
    </div>
  );
}
