import React from 'react';
import { motion } from 'framer-motion';

const ImpactSection = () => {
  return (
    <section id="impact" className="py-32 relative overflow-hidden bg-bg">
      <div className="glow-blob blob-indigo w-[700px] h-[700px] top-1/2 -left-20 opacity-5" />
      
      <div className="container mx-auto px-6 relative z-10">
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-32 items-center">
          
          <div className="max-w-xl">
             <motion.h2 
               initial={{ opacity: 0, y: 20 }}
               whileInView={{ opacity: 1, y: 0 }}
               viewport={{ once: true }}
               className="text-5xl md:text-7xl font-black text-fg tracking-[0.02em] leading-[0.9] mb-12"
             >
               The rental <br /> market is <br /> <span className="text-muted/20">broken.</span> <br />
               We're fixing it.
             </motion.h2>
             <p className="text-xl text-muted font-medium leading-relaxed mb-16">
               Scammers exploit desperation and trust using sophisticated tactics. 
               Argus provides the necessary counterbalance, restoring power to the 
               tenant through transparent, instant verification.
             </p>
             
             <motion.div 
               whileHover={{ scale: 1.02 }}
               className="inline-flex items-center gap-6 px-8 py-4 glass rounded-3xl border-fg/10 shadow-xl"
             >
                <div className="flex -space-x-3">
                   {[1,2,3,4].map(i => (
                     <div key={i} className="w-10 h-10 rounded-full border-4 border-bg bg-border shadow-sm" />
                   ))}
                </div>
                <span className="text-sm font-bold text-fg italic tracking-tight">Joined by 1,200+ early adopters</span>
             </motion.div>
          </div>

          <div className="grid grid-cols-2 gap-6">
             <StatBox value="₹500Cr+" label="Annual Fraud" delay={0.1} />
             <StatBox value="15M+" label="At-Risk Renters" delay={0.2} />
             <StatBox value="94%" label="Detection Rate" delay={0.3} />
             <StatBox value="<10s" label="Analysis Time" delay={0.4} />
          </div>

        </div>

      </div>
    </section>
  );
};

const StatBox = ({ value, label, delay }) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay }}
    className="glass p-12 rounded-[40px] text-center shadow-2xl shadow-indigo-500/5 group hover:border-accent/40 transition-all duration-500"
  >
     <div className="text-4xl md:text-5xl font-black text-fg tracking-tighter mb-4 group-hover:scale-110 transition-transform duration-500">{value}</div>
     <div className="text-[10px] font-mono font-bold text-accent tracking-[0.3em] uppercase">{label}</div>
  </motion.div>
);

export default ImpactSection;
