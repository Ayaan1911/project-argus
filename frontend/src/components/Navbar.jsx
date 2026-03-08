import React from 'react';
import { motion } from 'framer-motion';
import { Moon, Sun, Shield } from 'lucide-react';

const Navbar = ({ theme, onThemeToggle, toggleTheme, onCtaClick }) => {
  const isDark = theme === 'dark';
  const handleToggle = onThemeToggle || toggleTheme;

  return (
    <nav className="fixed top-0 left-0 w-full z-[100] transition-all duration-300">
      <div className="container mx-auto px-6 h-20 flex items-center justify-between glass border-fg/10 mt-4 rounded-full max-w-6xl shadow-2xl">
        
        {/* Left: Logo */}
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="w-10 h-10 glass rounded-xl flex items-center justify-center group-hover:bg-accent group-hover:text-bg transition-all duration-300">
            <Shield size={20} className="transition-transform group-hover:rotate-12" />
          </div>
          <span className="text-xl font-black text-fg tracking-tighter">Argus</span>
        </div>

        {/* Center: Navigation Links (Desktop) */}
        <div className="hidden md:flex items-center gap-10">
          <a href="#how-it-works" className="text-[13px] font-bold text-muted hover:text-accent tracking-widest uppercase transition-colors">How it works</a>
          <a href="#engines" className="text-[13px] font-bold text-muted hover:text-accent tracking-widest uppercase transition-colors">Forensics</a>
          <a href="#impact" className="text-[13px] font-bold text-muted hover:text-accent tracking-widest uppercase transition-colors">Impact</a>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-6">
          {/* Custom Theme Toggle */}
          <button 
            onClick={handleToggle} 
            className="flex items-center gap-3 p-1 glass-dark rounded-full pr-4 group transition-all"
            aria-label="Toggle theme"
          >
            <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center shadow-[0_0_10px_rgba(245,158,11,0.5)] group-hover:rotate-180 transition-transform duration-500">
              {isDark ? <Moon size={14} className="text-fg" /> : <Sun size={14} className="text-fg" />}
            </div>
            <span className="text-[10px] font-mono font-black text-fg tracking-widest uppercase hidden sm:inline">{isDark ? 'Dark' : 'Light'}</span>
          </button>

          <button 
            onClick={onCtaClick}
            className="hidden sm:flex px-6 py-2.5 bg-fg text-bg text-[13px] font-black rounded-full hover:scale-105 transition-all active:scale-95 shadow-lg shadow-fg/10"
          >
            Analyze Listing
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
