/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        cl: {
          bg: 'var(--cl-bg)',
          sidebar: 'var(--cl-sidebar)',
          card: 'var(--cl-card)',
          cardHover: 'var(--cl-card-hover)',
          elevated: 'var(--cl-elevated)',
          border: 'var(--cl-border)',
          borderLight: 'var(--cl-border-light)',
          text: 'var(--cl-text)',
          muted: 'var(--cl-muted)',
          subtle: 'var(--cl-subtle)',
          accent: '#9B7AFF',
          accentDark: '#7C54F5',
          accentLight: '#B79EFF',
          blue: '#3B82F6',
          cyan: '#06B6D4',
          green: '#10B981',
          orange: '#F59E0B',
          red: '#EF4444',
        },
      },
      boxShadow: {
        'glow-purple': '0 0 28px rgba(155, 122, 255, 0.22)',
        'glow-card': '0 10px 30px -10px rgba(0, 0, 0, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.28s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
