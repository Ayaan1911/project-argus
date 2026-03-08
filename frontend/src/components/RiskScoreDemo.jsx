import React from 'react';
import { motion } from 'framer-motion';

const RiskScoreDemo = () => {
  return (
    <section id="demo" className="py-32 relative overflow-hidden bg-surface">
      <div className="glow-blob blob-orange w-[500px] h-[500px] -bottom-20 -left-20 opacity-5" />
      
      <div className="container mx-auto px-6 relative z-10">
        
        <div className="flex flex-col lg:flex-row items-center gap-24 lg:gap-40">
          
          <div className="flex-1 max-w-2xl">
            <motion.h2 
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="text-[10px] font-mono font-bold text-accent tracking-[0.4em] uppercase mb-8"
            >
              Intelligence
            </motion.h2>
            <motion.h3 
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-4xl md:text-6xl font-black text-fg tracking-tighter mb-10 leading-[1.1]"
            >
              Definitive risk analysis. <br />
              Stop guessing.
            </motion.h3>
            <p className="text-xl text-muted font-medium mb-14 leading-relaxed max-w-xl">
              Argus translates millions of data points into a single, comprehensive verdict 
              you can trust before transferring any funds.
            </p>
            
            <div className="space-y-4">
               <ResultPill label="Price Variance" value="-45% Anomaly" type="danger" />
               <ResultPill label="Image Integrity" value="Source match found" type="warning" />
               <ResultPill label="Trust Score" value="Low" type="danger" />
            </div>
          </div>

          <div className="flex-1 w-full max-w-xl">
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              className="glass glass-card border-white/20 dark:border-white/5 p-12 lg:p-16 relative overflow-hidden shadow-[0_50px_100px_-20px_rgba(0,0,0,0.1)] dark:shadow-[0_50px_100px_-20px_rgba(0,0,0,0.4)]"
            >
              <div className="absolute top-0 right-0 p-10 opacity-30">
                 <div className="text-[10px] font-mono font-bold text-subtle tracking-[0.2em] uppercase mb-2">Verdict Status</div>
                 <div className="text-[10px] font-mono font-bold text-accent tracking-[0.2em] uppercase">Verified High Risk</div>
              </div>

              <div className="flex flex-col items-center justify-center pt-8">
                 <div className="relative w-56 h-56 mb-12">
                    <svg className="w-full h-full -rotate-90">
                       <circle cx="112" cy="112" r="104" fill="none" stroke="var(--border)" strokeWidth="16" strokeOpacity="0.5" />
                       <motion.circle 
                         cx="112" cy="112" r="104" fill="none" stroke="var(--accent)" strokeWidth="16" 
                         strokeDasharray="653"
                         initial={{ strokeDashoffset: 653 }}
                         whileInView={{ strokeDashoffset: 653 * (1 - 0.82) }}
                         viewport={{ once: true }}
                         transition={{ duration: 2, ease: [0.16, 1, 0.3, 1] }}
                         strokeLinecap="round"
                       />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                       <span className="text-7xl font-black text-fg tracking-tighter">82</span>
                       <span className="text-[10px] font-mono font-black text-muted tracking-widest uppercase mt-1">Risk Score</span>
                    </div>
                 </div>
                 
                 <div className="text-center">
                    <h4 className="text-3xl font-black text-fg mb-3 tracking-tight">Potentially Unsafe</h4>
                    <p className="text-muted font-medium">High probability of deposit scam detected.</p>
                 </div>
              </div>

              {/* Decorative scanline */}
              <motion.div 
                animate={{ top: ["0%", "100%", "0%"] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                className="absolute left-0 right-0 h-px bg-accent/20 blur-sm pointer-events-none"
              />
            </motion.div>
          </div>

        </div>

      </div>
    </section>
  );
};

const ResultPill = ({ label, value, type }) => (
  <motion.div 
    whileHover={{ x: 10 }}
    className="flex items-center justify-between p-6 glass rounded-2xl border-white/5 dark:border-white/5"
  >
    <span className="text-xs font-mono font-bold text-fg tracking-widest uppercase">{label}</span>
    <span className={`text-xs font-mono font-black px-4 py-1.5 rounded-full ${type === 'danger' ? 'bg-accent/10 text-accent border border-accent/20' : 'bg-fg text-bg'}`}>
      {value}
    </span>
  </motion.div>
);

export default RiskScoreDemo;
