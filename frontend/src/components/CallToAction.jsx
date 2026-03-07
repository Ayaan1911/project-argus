import React from 'react';
import { motion } from 'framer-motion';

const CallToAction = ({ onVerificationStart }) => {
  const [url, setUrl] = React.useState('');

  const handleVerify = () => {
    if (url.trim()) {
      onVerificationStart(url);
    }
  };

  return (
    <section id="cta" className="py-40 relative overflow-hidden bg-bg">
      <div className="glow-blob blob-orange w-[800px] h-[800px] -top-40 left-1/2 -translate-x-1/2 opacity-10" />

      <div className="container mx-auto px-6 relative z-10">

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto glass rounded-[60px] p-16 md:p-32 text-center relative overflow-hidden shadow-[0_100px_150px_-30px_rgba(0,0,0,0.2)] dark:shadow-[0_100px_150px_-30px_rgba(0,0,0,0.6)]"
        >
          {/* Internal atmospheric glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-accent/30 blur-[100px] pointer-events-none opacity-50" />

          <h2 className="text-5xl md:text-[5rem] font-black tracking-tighter mb-10 relative z-10 leading-[0.9] text-fg">
            Secure your <br /> deposit today.
          </h2>
          <p className="text-xl text-muted font-medium mb-16 max-w-2xl mx-auto relative z-10 leading-relaxed">
            Copy any rental listing URL from Housing, 99acres, or NoBroker
            and get a definitive risk assessment in seconds.
          </p>

          <div className="relative max-w-2xl mx-auto z-10 group bg-bg dark:bg-black/50 rounded-3xl border border-border p-2 focus-within:ring-4 focus-within:ring-accent/10 transition-all">
            <input
              type="text"
              placeholder="Paste listing URL here..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full h-16 bg-transparent px-8 font-mono text-sm outline-none placeholder:text-subtle text-fg"
            />
            <button
              onClick={handleVerify}
              className="md:absolute top-2 right-2 bottom-2 px-10 py-4 md:py-0 bg-accent text-fg font-black rounded-2xl hover:scale-[1.02] shadow-xl shadow-accent/20 transition-all active:scale-95 whitespace-nowrap"
            >
              Verify Now
            </button>
          </div>

          <div className="mt-20 flex flex-wrap justify-center gap-x-12 gap-y-6 opacity-40 text-[10px] font-mono font-bold tracking-[0.4em] uppercase text-fg">
            <span className="hover:opacity-100 transition-opacity cursor-default">Housing.com</span>
            <span className="hover:opacity-100 transition-opacity cursor-default">99Acres</span>
            <span className="hover:opacity-100 transition-opacity cursor-default">MagicBricks</span>
            <span className="hover:opacity-100 transition-opacity cursor-default">NoBroker</span>
          </div>
        </motion.div>

      </div>
    </section>
  );
};

export default CallToAction;
