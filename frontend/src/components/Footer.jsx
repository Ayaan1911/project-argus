import React from 'react';
import { Shield } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="py-20 bg-bg border-t border-border">
      <div className="container mx-auto px-6">
        
        <div className="flex flex-col md:flex-row justify-between items-start gap-12">
          
          <div className="max-w-xs">
             <div className="flex items-center gap-3 mb-6">
                <Shield className="text-accent" size={24} />
                <span className="text-xl font-black text-text tracking-tighter">Project Argus</span>
             </div>
             <p className="text-sm text-text-muted leading-relaxed">
               An AI security tool dedicated to protecting Phase 1 renters in India 
               from high-sophistry rental scams.
             </p>
          </div>

          <div className="flex flex-wrap gap-12 md:gap-24">
             <div>
                <h4 className="text-[10px] font-mono font-bold text-text-subtle tracking-widest uppercase mb-6">Product</h4>
                <ul className="space-y-4 text-sm font-medium text-text-muted hover:text-text cursor-pointer transition-all">
                   <li className="hover:text-text">Verification</li>
                   <li className="hover:text-text">Features</li>
                   <li className="hover:text-text">Case Studies</li>
                </ul>
             </div>
             <div>
                <h4 className="text-[10px] font-mono font-bold text-text-subtle tracking-widest uppercase mb-6">Legal</h4>
                <ul className="space-y-4 text-sm font-medium text-text-muted hover:text-text cursor-pointer transition-all">
                   <li className="hover:text-text">Privacy Policy</li>
                   <li className="hover:text-text">Terms of Service</li>
                </ul>
             </div>
          </div>

        </div>

        <div className="mt-20 pt-8 border-t border-border flex flex-col md:flex-row justify-between items-center gap-6">
           <p className="text-xs text-text-subtle font-medium">© 2025 AI for Bharat Hackathon. All rights reserved.</p>
           <div className="flex items-center gap-4 text-xs text-text-subtle font-bold font-mono tracking-tighter">
              <span>PROUDLY BUILT FOR INDIA</span>
              <span className="text-accent text-[16px]">●</span>
           </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;
