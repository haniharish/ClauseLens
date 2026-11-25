import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Lock, Mail, Scale, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';

export default function Login() {
  const { login } = useApp();
  const navigate = useNavigate();
  const [email, setEmail] = useState('alex.sharma@university.edu');
  const [password, setPassword] = useState('••••••••••••');
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      toast.error('Please enter both email and password');
      return;
    }
    setLoading(true);
    try {
      await login({ email, password, rememberMe });
      navigate('/dashboard');
    } catch {
      toast.error('Unable to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#080A12] px-4 py-12 text-slate-100">
      <div className="relative w-full max-w-md">
        <div className="pointer-events-none absolute -top-24 left-1/2 h-56 w-56 -translate-x-1/2 rounded-full bg-[#9B7AFF]/20 blur-3xl" />

        <div className="glass-card relative p-8">
          <div className="mb-6 flex flex-col items-center text-center">
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[#9B7AFF] to-[#06B6D4] shadow-glow-purple">
              <Scale className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Welcome back to ClauseLens</h1>
            <p className="mt-1 text-xs text-slate-400">
              AI Legal Intelligence & Version-Diff Alerts (Demo Auth Ready for Django JWT)
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="cl-input pl-10"
                  placeholder="you@domain.com"
                />
              </div>
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between">
                <label className="text-xs font-medium text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => toast('Password reset link simulated in demo mode', { icon: '🔐' })}
                  className="text-xs font-medium text-[#9B7AFF] hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="cl-input pl-10"
                  placeholder="Enter password"
                />
              </div>
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 rounded border-slate-600 bg-[#080A12] accent-[#9B7AFF]"
              />
              Remember me on this device
            </label>

            <button type="submit" disabled={loading} className="cl-btn-primary w-full py-3">
              {loading ? 'Signing in...' : 'Sign In to Dashboard'}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="mt-5 flex items-center gap-2 rounded-xl border border-[#9B7AFF]/20 bg-[#9B7AFF]/10 px-3 py-2 text-[11px] text-slate-300">
            <Sparkles className="h-4 w-4 shrink-0 text-[#9B7AFF]" />
            <span>Demo credentials pre-filled. Click Sign In to explore the dashboard.</span>
          </div>

          <p className="mt-6 text-center text-xs text-slate-400">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-semibold text-[#9B7AFF] hover:underline">
              Create account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
