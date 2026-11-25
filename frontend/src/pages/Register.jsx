import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Lock, Mail, Scale, User } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';

export default function Register() {
  const { register } = useApp();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    acceptedTerms: false,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.fullName.trim() || !form.email.trim() || !form.password) {
      toast.error('Please fill in all required fields');
      return;
    }
    if (form.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }
    if (form.password !== form.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (!form.acceptedTerms) {
      toast.error('Please accept the Terms & Privacy Policy');
      return;
    }
    setLoading(true);
    try {
      await register(form);
      navigate('/profile');
    } catch {
      toast.error('Registration failed');
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
            <h1 className="text-2xl font-bold tracking-tight text-white">Create your ClauseLens account</h1>
            <p className="mt-1 text-xs text-slate-400">
              Start summarizing Terms &amp; Conditions tailored to your context
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-300">Full Name</label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  value={form.fullName}
                  onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                  className="cl-input pl-10"
                  placeholder="Alex Sharma"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-300">Email Address</label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="cl-input pl-10"
                  placeholder="alex@university.edu"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-300">Password</label>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="password"
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    className="cl-input pl-10"
                    placeholder="Min 6 chars"
                  />
                </div>
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-medium text-slate-300">Confirm</label>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  <input
                    type="password"
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                    className="cl-input pl-10"
                    placeholder="Repeat password"
                  />
                </div>
              </div>
            </div>

            <label className="flex items-start gap-2.5 text-xs text-slate-400 cursor-pointer">
              <input
                type="checkbox"
                checked={form.acceptedTerms}
                onChange={(e) => setForm({ ...form, acceptedTerms: e.target.checked })}
                className="mt-0.5 h-4 w-4 rounded border-slate-600 bg-[#080A12] accent-[#9B7AFF]"
              />
              <span>
                I agree to the ClauseLens Terms of Service and Privacy Policy (mock authentication for frontend demo).
              </span>
            </label>

            <button type="submit" disabled={loading} className="cl-btn-primary w-full py-3">
              {loading ? 'Creating account...' : 'Create Account'}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-[#9B7AFF] hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
