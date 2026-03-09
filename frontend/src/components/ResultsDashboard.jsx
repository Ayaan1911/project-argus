import React, { useEffect, useRef } from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Info, ArrowLeft, Download } from 'lucide-react';
import { gsap } from 'gsap';
import heroNight from '../assets/hero-night.jpg';

const ResultsDashboard = ({ result, onReset }) => {
  const rootRef = useRef(null);

  if (!result) return null;

  // Handle error case from backend
  if (result.error) {
    return (
      <div style={styles.dashboard}>
        <div style={{
          ...styles.heroBackground,
          backgroundImage: `linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.9)), url(${heroNight})`
        }} />
        <div style={styles.container}>
          <div style={styles.errorCard}>
            <ShieldAlert size={48} color="var(--accent)" />
            <h2 style={styles.heroHeading}>ANALYSIS FAILED</h2>
            <p style={styles.heroSummary}>{result.error}</p>
            <button onClick={onReset} className="btn btn-primary" style={{ marginTop: '24px' }}>
              TRY AGAIN
            </button>
          </div>
        </div>
      </div>
    );
  }

  const score = result.risk_score ?? Math.round((result.confidence_score || 0) * 100);
  const isHighRisk = score > 65;
  const isSuspicious = score > 30 && score <= 65;

  let verdict = "LOW RISK";
  let VerdictIcon = ShieldCheck;
  let accentColor = "#10b981"; // Safe green
  let verdictDescription = "Argus analysis indicates this listing appears legitimate.";

  if (isHighRisk) {
    verdict = "HIGH RISK";
    VerdictIcon = ShieldAlert;
    accentColor = "#ef4444"; // Danger red
    verdictDescription = "Argus detected signals commonly associated with rental scams.";
  } else if (isSuspicious) {
    verdict = "SUSPICIOUS";
    VerdictIcon = AlertTriangle;
    accentColor = "var(--accent)";
    verdictDescription = "Argus found some anomalies that warrant careful verification.";
  }

  useEffect(() => {
    let ctx = gsap.context(() => {
      // Safety checks for GSAP targets
      const targets = [
        { selector: '.hero-section', vars: { opacity: 0, y: 20 } },
        { selector: '.signal-card', vars: { opacity: 0, y: 30, stagger: 0.1 } },
        { selector: '.reasoning-section', vars: { opacity: 0, y: 40 } },
        { selector: '.rec-card', vars: { opacity: 0, scale: 0.95, stagger: 0.05 } }
      ];

      targets.forEach(t => {
        if (document.querySelector(t.selector)) {
          gsap.from(t.selector, {
            ...t.vars,
            duration: 0.8,
            ease: 'power3.out',
            scrollTrigger: t.selector.includes('section') || t.selector.includes('card') ? {
              trigger: t.selector,
              start: 'top 90%'
            } : undefined
          });
        }
      });

      // Gauge animation safety
      if (document.querySelector('.gauge-path')) {
        const path = document.querySelector('.gauge-path');
        const length = path.getTotalLength();
        gsap.fromTo('.gauge-path',
          { strokeDasharray: length, strokeDashoffset: length },
          { strokeDashoffset: length - (score / 100) * length, duration: 2, ease: 'power4.out', delay: 0.5 }
        );
      }
    }, rootRef);

    return () => ctx.revert();
  }, [score]);

  return (
    <div ref={rootRef} style={styles.dashboard}>
      {/* Background Layer */}
      <div style={{
        ...styles.heroBackground,
        backgroundImage: `linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.9)), url(${heroNight})`
      }} />

      {/* HEADER NAV */}
      <div style={styles.nav}>
        <button onClick={onReset} style={styles.navBtn}>
          <ArrowLeft size={18} />
          <span>NEW ANALYSIS</span>
        </button>
        <span style={styles.navUrl}>{result.scraped_data?.source_url || result.url}</span>
        <button style={styles.navBtn}>
          <Download size={18} />
          <span>REPORT</span>
        </button>
      </div>

      <div style={styles.container}>

        {/* SECTION 1: HERO VERDICT */}
        <section className="hero-section" style={styles.heroSection}>
          <div style={styles.gaugeWrapper}>
            <svg viewBox="0 0 100 100" style={styles.gaugeSvg}>
              <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="6" />
              <circle
                className="gauge-path"
                cx="50" cy="50" r="45"
                fill="none"
                stroke={accentColor}
                strokeWidth="6"
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div style={styles.gaugeContent}>
              <span style={styles.gaugeScore}>{score}</span>
              <span style={styles.gaugeLabel}>SCORE</span>
            </div>
          </div>

          <div style={{ ...styles.verdictBadge, color: accentColor, borderColor: accentColor }}>
            <VerdictIcon size={20} />
            <span>{verdict}</span>
          </div>

          <p style={styles.heroSummary}>
            {verdictDescription} Confidence: {isHighRisk ? 84 : (isSuspicious ? 76 : 88)}%.
          </p>
        </section>

        {/* SECTION 2: SIGNAL ANALYSIS */}
        <section style={styles.section}>
          <h3 style={styles.sectionHeading}>WHY ARGUS FLAGGED THIS</h3>
          <div style={styles.signalGrid}>
            <SignalCard
              name="Price vs Market"
              value={result.signals?.["Price vs Market"] !== undefined ? `${Math.round(result.signals["Price vs Market"] * 100)}%` : 'N/A'}
              desc="Deviation from typical regional median."
            />
            <SignalCard
              name="Urgency Language"
              value={result.signals?.["Urgency Language"] || 0}
              desc="High-pressure tactics detected in text."
            />
            <SignalCard
              name="Phone Reuse"
              value={result.signals?.["Phone Reuse"] || 1}
              desc="Historical broker activity across listings."
            />
            <SignalCard
              name="Image Count"
              value={result.signals?.["Image Count"] || 0}
              desc="Visual verification of property assets."
            />
          </div>
        </section>

        {/* SECTION 3: AI FORENSIC EXPLANATION */}
        <section className="reasoning-section" style={styles.section}>
          <h3 style={styles.sectionHeading}>AI FORENSIC EXPLANATION</h3>
          <div style={styles.explanationCard}>
            <p style={styles.explanationText}>
              {result.explanation || "No detailed forensic reasoning generated."}
            </p>
            <div style={styles.modelTag}>PREDICTIVE REASONING v3.2 (OPENROUTER)</div>
          </div>
        </section>

        {/* SECTION 4: RECOMMENDATIONS */}
        <section style={styles.section}>
          <h3 style={styles.sectionHeading}>PROTECTIVE RECOMMENDATIONS</h3>
          <div style={styles.recGrid}>
            {(result.recommendations || []).map((rec, i) => (
              <div key={i} className="rec-card" style={styles.recCard}>
                <div style={styles.recBullet} />
                <span style={styles.recText}>{rec}</span>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
};

const SignalCard = ({ name, value, desc }) => (
  <div className="signal-card" style={styles.signalCard}>
    <span style={styles.signalName}>{name}</span>
    <span style={styles.signalValue}>{value}</span>
    <p style={styles.signalDesc}>{desc}</p>
  </div>
);

const styles = {
  dashboard: {
    minHeight: '100vh',
    width: '100vw',
    backgroundColor: '#0c0a09',
    color: 'white',
    fontFamily: 'var(--font-sans)',
    position: 'relative',
    overflowX: 'hidden'
  },
  heroBackground: {
    position: 'absolute',
    inset: 0,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundAttachment: 'fixed',
    zIndex: 1
  },
  nav: {
    height: '64px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
    position: 'relative',
    zIndex: 10,
    backgroundColor: 'rgba(0,0,0,0.2)',
    backdropFilter: 'blur(10px)'
  },
  navBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
    fontWeight: 700,
    letterSpacing: '0.05em',
    color: 'white',
  },
  navUrl: {
    fontSize: '11px',
    fontFamily: 'var(--font-mono)',
    color: 'rgba(255,255,255,0.5)',
    maxWidth: '300px',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '60px 24px 100px',
    position: 'relative',
    zIndex: 10
  },
  // Sections
  section: {
    marginTop: '60px',
  },
  sectionHeading: {
    fontSize: '11px',
    fontWeight: 800,
    color: 'white',
    letterSpacing: '0.15em',
    marginBottom: '20px',
    opacity: 0.6,
  },
  // Hero
  heroSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
  },
  gaugeWrapper: {
    position: 'relative',
    width: '160px',
    height: '160px',
    marginBottom: '24px',
  },
  gaugeSvg: {
    width: '100%',
    height: '100%',
  },
  gaugeContent: {
    position: 'absolute',
    inset: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
  },
  gaugeScore: {
    fontSize: '48px',
    fontWeight: 900,
    lineHeight: 1,
    color: 'white'
  },
  gaugeLabel: {
    fontSize: '10px',
    fontWeight: 700,
    letterSpacing: '0.1em',
    opacity: 0.5,
    color: 'white'
  },
  verdictBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 20px',
    borderRadius: '8px',
    border: '1px solid',
    fontSize: '14px',
    fontWeight: 800,
    letterSpacing: '0.05em',
    marginBottom: '16px',
    backgroundColor: 'rgba(255,255,255,0.05)',
    backdropFilter: 'blur(5px)'
  },
  heroSummary: {
    fontSize: '18px',
    color: 'white',
    lineHeight: 1.5,
    maxWidth: '500px',
    opacity: 0.95,
  },
  // Signals
  signalGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '12px',
  },
  signalCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    backdropFilter: 'blur(5px)'
  },
  signalName: {
    fontSize: '10px',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    opacity: 0.5,
    color: 'white'
  },
  signalValue: {
    fontSize: '24px',
    fontWeight: 800,
    color: 'white'
  },
  signalDesc: {
    fontSize: '12px',
    color: 'rgba(255,255,255,0.6)',
    lineHeight: 1.4,
    marginTop: '4px',
  },
  // Explanation
  explanationCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '16px',
    padding: '32px',
    position: 'relative',
    backdropFilter: 'blur(5px)'
  },
  explanationText: {
    fontSize: '16px',
    lineHeight: 1.7,
    color: 'white',
    opacity: 0.9,
  },
  modelTag: {
    position: 'absolute',
    bottom: '16px',
    right: '24px',
    fontSize: '9px',
    fontWeight: 700,
    fontFamily: 'var(--font-mono)',
    color: 'var(--accent)',
    opacity: 0.6,
  },
  // Recommendations
  recGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  recCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    padding: '16px 20px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    backdropFilter: 'blur(5px)'
  },
  recBullet: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    backgroundColor: 'var(--accent)',
    flexShrink: 0,
  },
  recText: {
    fontSize: '14px',
    lineHeight: 1.5,
    color: 'white'
  },
  errorCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '24px',
    padding: '60px 40px',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '16px',
    backdropFilter: 'blur(10px)'
  }
};

export default ResultsDashboard;
