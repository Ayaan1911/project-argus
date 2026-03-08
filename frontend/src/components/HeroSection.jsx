import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import heroDay from '../assets/hero-day.jpg';
import heroNight from '../assets/hero-night.jpg';

const HeroSection = ({ theme, onCtaClick }) => {
  const isDark = theme === 'dark';

  return (
    <section id="hero-section" className="relative min-h-screen flex items-center justify-center pt-32 pb-20 overflow-hidden bg-bg">
      {/* Layer 1 & 2: Photography Layers with Smooth Fade Transition */}
      <div className="absolute inset-0 z-0">
        {/* Night Image */}
        <div 
          className="absolute inset-0 transition-opacity duration-[600ms] ease-in-out"
          style={{ 
            backgroundImage: `url(${heroNight})`, 
            backgroundSize: 'cover', 
            backgroundPosition: 'center',
            opacity: isDark ? 1 : 0 
          }}
        />
        {/* Day Image */}
        <div 
          className="absolute inset-0 transition-opacity duration-[600ms] ease-in-out"
          style={{ 
            backgroundImage: `url(${heroDay})`, 
            backgroundSize: 'cover', 
            backgroundPosition: 'center',
            opacity: isDark ? 0 : 1 
          }}
        />

        {/* Layer 3: Dark Gradient Overlay (For Readability) */}
        <div 
          className="absolute inset-0 z-10 bg-gradient-to-b from-black/45 to-black/65"
        />
      </div>

      {/* Layer 4: Ultra-Subtle Grid Pattern (Signature Branding) */}
      <div className="absolute inset-0 z-20 grid-texture opacity-[0.03] pointer-events-none" />
      
      <div className="container mx-auto px-6 relative z-30 max-w-5xl text-center">
        
        {/* Status indicator */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-bg/20 bg-black/40 backdrop-blur-md mb-12 shadow-sm"
        >
          <span className="w-2 h-2 rounded-full bg-accent animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.8)]" />
          <span className="text-[10px] font-mono font-bold text-white/70 tracking-widest uppercase">Live Fraud Monitoring</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-6xl md:text-[5.5rem] font-black leading-[0.95] tracking-tight text-white mb-10 text-balance"
        >
          Don't Get <br />
          Scammed. Verify <br />
          Before You <span className="text-accent drop-shadow-[0_0_15px_rgba(245,158,11,0.3)]">Pay.</span>
        </motion.h1>

        {/* Subtext */}
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="text-lg md:text-xl text-white/95 max-w-2xl mx-auto mb-14 leading-relaxed font-semibold drop-shadow-sm"
        >
          Project Argus analyzes rental listings using multi-modal AI—spotting price anomalies, 
          stolen images, and broker scam patterns in under 10 seconds.
        </motion.p>

        {/* Actions */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-5"
        >
          <button 
            onClick={onCtaClick}
            className="w-full sm:w-auto px-10 py-5 bg-accent text-black font-bold rounded-2xl hover:shadow-[0_20px_40px_-10px_rgba(245,158,11,0.4)] transition-all active:scale-95 group"
          >
            Analyze a Listing
            <span className="inline-block ml-2 group-hover:translate-x-1 transition-transform">→</span>
          </button>
          <button 
            onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
            className="w-full sm:w-auto px-10 py-5 bg-white/10 backdrop-blur-md border border-white/20 text-white font-bold rounded-2xl hover:bg-white/20 transition-all active:scale-95"
          >
            See how it works
          </button>
        </motion.div>

      </div>
    </section>
  );
};

export default HeroSection;
