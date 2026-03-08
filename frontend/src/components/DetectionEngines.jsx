import React from 'react';
import { motion } from 'framer-motion';

const DetectionEngines = () => {
  return (
    <section id="engines" className="py-32 relative overflow-hidden bg-bg">
      <div className="glow-blob blob-purple w-[600px] h-[600px] -top-20 -right-20 opacity-5" />
      
      <div className="container mx-auto px-6 relative z-10">
        
        <div className="max-w-3xl mb-24">
          <motion.h2 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="text-[10px] font-mono font-bold text-accent tracking-[0.4em] uppercase mb-8"
          >
            Infrastructure
          </motion.h2>
          <motion.h3 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-5xl font-black text-fg tracking-tight mb-8 leading-tight"
          >
            Powered by specialized <br /> forensic models.
          </motion.h3>
          <p className="text-xl text-muted font-medium leading-relaxed max-w-2xl">
            Argus doesn't just look at the price. It runs a multi-modal analysis pipeline 
            across all listing data simultaneously.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <EngineCard 
            title="Price Anomaly" 
            desc="Matches rent against 5-year micro-market baseline models." 
            icon="📊"
            delay={0.1}
          />
          <EngineCard 
            title="Image Forensic" 
            desc="Reverse searches watermarks and duplicate apartment photos." 
            icon="🔎"
            delay={0.2}
          />
          <EngineCard 
            title="Semantic Text" 
            desc="Flags high-pressure sales language and suspicious deposit rules." 
            icon="✍️"
            delay={0.3}
          />
          <EngineCard 
            title="Broker Network" 
            desc="Cross-references phone numbers and posting behavior graph." 
            icon="🌐"
            delay={0.4}
          />
        </div>

      </div>
    </section>
  );
};

const EngineCard = ({ title, desc, icon, delay }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.6, delay }}
    whileHover={{ y: -8, scale: 1.02 }}
    className="glass glass-card group p-10 flex flex-col items-start border-fg/10 dark:border-white/5 shadow-2xl shadow-indigo-500/5"
  >
    <div className="w-14 h-14 rounded-2xl bg-bg border border-border flex items-center justify-center text-3xl mb-8 group-hover:scale-110 transition-all duration-500 shadow-sm">
      <span className="grayscale group-hover:grayscale-0 transition-all">{icon}</span>
    </div>
    <h3 className="text-xl font-black text-fg mb-4 tracking-tight leading-none uppercase text-xs font-mono font-bold tracking-widest">{title}</h3>
    <h3 className="text-2xl font-black text-fg mb-4 tracking-tight leading-none">{title}</h3>
    <p className="text-muted text-base leading-relaxed font-medium">{desc}</p>
    
    <div className="mt-auto pt-10 flex items-center gap-2 text-[10px] font-mono font-bold text-accent tracking-widest uppercase opacity-0 group-hover:opacity-100 transition-all">
       Module Active
       <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
    </div>
  </motion.div>
);

export default DetectionEngines;
