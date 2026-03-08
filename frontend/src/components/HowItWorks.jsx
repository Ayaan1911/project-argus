import React from 'react';
import { motion } from 'framer-motion';

const features = [
  {
    id: 'price',
    num: '01',
    label: 'Price Intelligence',
    title: 'Spot Price Anomalies Instantly',
    desc: 'Argus compares the stated rent against real-time micro-market median models for that specific locality. Anything more than 30% below baseline triggers an immediate risk flag.',
  },
  {
    id: 'image',
    num: '02',
    label: 'Image Verification',
    title: 'Detect Stolen & Reused Photos',
    desc: 'Our perceptual hashing engine scans millions of listings to detect if images are being reused across different platforms or hijacked from unrelated properties.',
  },
  {
    id: 'language',
    num: '03',
    label: 'Scam Language Detection',
    title: 'Analyze Linguistic Fraud Signals',
    desc: 'Argus parses descriptions for high-pressure sales tactics, suspicious advance-deposit rules, and phrasing patterns common in rental frauds.',
  },
  {
    id: 'broker',
    num: '04',
    label: 'Broker Pattern Detection',
    title: 'Identify Burner Phone Networks',
    desc: 'We map contact numbers against known deceitful actor graphs, identifying burner phone patterns and repeat offenders across the rental ecosystem.',
  }
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-32 relative overflow-hidden bg-bg">
      {/* Background glow for section depth */}
      <div className="glow-blob blob-indigo w-[800px] h-[800px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-5 dark:opacity-10" />

      <div className="container mx-auto px-6 relative z-10">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-32">
          <motion.h2 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="text-xs font-mono font-bold text-accent tracking-[0.3em] uppercase mb-6"
          >
            Capabilities
          </motion.h2>
          <motion.h3 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-6xl font-black text-fg tracking-tight leading-[1.1]"
          >
            Multi-modal verification. <br />
            Definitive security.
          </motion.h3>
        </div>

        {/* Stacked Product Modules */}
        <div className="space-y-40">
          {features.map((feature, idx) => (
            <div 
              key={feature.id} 
              className={`flex flex-col md:flex-row items-center gap-16 lg:gap-32 ${idx % 2 !== 0 ? 'md:flex-row-reverse' : ''}`}
            >
              {/* Product Visual Module */}
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="flex-1 w-full"
              >
                <div className="aspect-[16/10] glass glass-card border-fg/10 dark:border-white/5 shadow-2xl relative group p-1">
                  <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent pointer-events-none" />
                  <div className="w-full h-full rounded-[20px] overflow-hidden bg-surface/20 border border-fg/5">
                     <FeatureVisual type={feature.id} />
                  </div>
                </div>
              </motion.div>

              {/* Description Column */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-100px" }}
                transition={{ duration: 0.8, delay: 0.2 }}
                className="flex-1 max-w-xl"
              >
                <div className="flex items-center gap-6 mb-8">
                  <span className="text-4xl font-black text-accent/20 tracking-tighter leading-none">{feature.num}</span>
                  <div className="h-px bg-border flex-1" />
                </div>
                <h4 className="text-3xl md:text-4xl font-black text-fg mb-8 tracking-tight leading-tight">{feature.title}</h4>
                <p className="text-lg text-muted leading-relaxed font-medium">
                  {feature.desc}
                </p>
                <div className="mt-10 flex items-center gap-2 text-accent text-sm font-bold tracking-widest uppercase">
                   <div className="w-8 h-px bg-accent" />
                   Learn more
                </div>
              </motion.div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
};

/* Feature SVGs - updated for cleaner look */
const FeatureVisual = ({ type }) => {
  if (type === 'price') return <PriceSVG />;
  if (type === 'image') return <ImageSVG />;
  if (type === 'language') return <LanguageSVG />;
  if (type === 'broker') return <BrokerSVG />;
  return null;
};

function PriceSVG() {
  return (
    <div className="w-full h-full flex items-center justify-center p-12 ">
      <svg viewBox="0 0 400 240" className="w-full h-full text-accent drop-shadow-2xl">
        <path d="M40 200 L360 200" stroke="currentColor" strokeWidth="1" strokeOpacity="0.1" />
        <motion.path 
          d="M40 200 L100 170 L160 185 L220 120 L280 145 L360 60"
          fill="none" 
          stroke="currentColor" 
          strokeWidth="3" 
          strokeLinecap="round" 
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          transition={{ duration: 2, ease: "easeInOut" }}
        />
        <motion.circle 
          cx="220" cy="120" r="6" 
          fill="currentColor" 
          initial={{ scale: 0 }}
          whileInView={{ scale: 1 }}
          transition={{ delay: 1 }}
        />
        <rect x="230" y="80" width="80" height="30" rx="8" fill="currentColor" fillOpacity="0.1" stroke="currentColor" strokeWidth="1" strokeOpacity="0.2" />
        <text x="240" y="100" className="text-[10px] font-mono font-bold fill-fg uppercase tracking-widest">Anomaly</text>
      </svg>
    </div>
  );
}

function ImageSVG() {
  return (
    <div className="w-full h-full flex items-center justify-center p-12">
      <div className="relative w-full h-full max-w-[300px] flex items-center justify-center">
         <div className="absolute top-0 left-0 w-32 h-32 rounded-2xl bg-muted/10 border border-border flex items-center justify-center overflow-hidden">
             <div className="w-16 h-16 rounded-full bg-muted/20" />
         </div>
         <div className="absolute bottom-0 right-0 w-32 h-32 rounded-2xl bg-accent/10 border border-accent/30 flex items-center justify-center overflow-hidden">
             <div className="w-16 h-16 rounded-full bg-accent/30" />
         </div>
         <div className="w-px h-24 bg-accent/30 rotate-45 transform translate-x-4 translate-y-2 opacity-50" />
         <div className="px-4 py-2 glass rounded-full text-[10px] font-mono font-bold text-accent tracking-widest uppercase shadow-xl">Match 98.2%</div>
      </div>
    </div>
  );
}

function LanguageSVG() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 space-y-4">
       <div className="w-full h-2 bg-muted/10 rounded-full overflow-hidden">
          <motion.div initial={{ width: 0 }} whileInView={{ width: "70%" }} className="h-full bg-muted/40" />
       </div>
       <div className="w-full h-2 bg-accent/10 rounded-full overflow-hidden border border-accent/20">
          <motion.div initial={{ width: 0 }} whileInView={{ width: "90%" }} className="h-full bg-accent" />
       </div>
       <div className="w-full h-2 bg-muted/10 rounded-full overflow-hidden">
          <motion.div initial={{ width: 0 }} whileInView={{ width: "40%" }} className="h-full bg-muted/40" />
       </div>
       <div className="mt-4 px-3 py-1 bg-accent font-mono text-[8px] font-black tracking-widest text-bg rounded-md">SCAM PATTERN DETECTED</div>
    </div>
  );
}

function BrokerSVG() {
  return (
    <div className="w-full h-full flex items-center justify-center p-8">
      <svg viewBox="0 0 300 200" className="w-full h-full">
         <circle cx="150" cy="100" r="30" fill="none" stroke="var(--accent)" strokeWidth="1" strokeDasharray="4 4" />
         {[0, 72, 144, 216, 288].map((angle, i) => {
           const x = 150 + Math.cos(angle * Math.PI / 180) * 80;
           const y = 100 + Math.sin(angle * Math.PI / 180) * 80;
           return (
             <React.Fragment key={i}>
               <line x1="150" y1="100" x2={x} y2={y} stroke="var(--border)" strokeWidth="1" opacity="0.3" />
               <circle cx={x} cy={y} r="8" fill={i % 2 === 0 ? "var(--accent)" : "var(--border)"} />
             </React.Fragment>
           )
         })}
      </svg>
    </div>
  );
}

export default HowItWorks;
