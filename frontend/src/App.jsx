import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import HowItWorks from './components/HowItWorks';
import DetectionEngines from './components/DetectionEngines';
import RiskScoreDemo from './components/RiskScoreDemo';
import ImpactSection from './components/ImpactSection';
import CallToAction from './components/CallToAction';
import AnalysisLoading from './components/AnalysisLoading';
import ResultsDashboard from './components/ResultsDashboard';
import Footer from './components/Footer';

function App() {
  const [theme, setTheme] = useState('light');
  const [appState, setAppState] = useState('home'); // 'home', 'analyzing', 'results'
  const [activeUrl, setActiveUrl] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);

  // Theme toggle effect
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Listen for the custom events emitted by the GSAP components
  useEffect(() => {
    const handleStartAnalysis = async (e) => {
      const url = e.detail.url;
      setActiveUrl(url);
      setAppState('analyzing');

      try {
        const startTime = Date.now();
        const formData = new FormData();
        formData.append('url', url);

        const response = await fetch('http://localhost:8080/analyze/url', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();

        // Ensure cinematic loading screen shows for at least 4.8s (4 steps * 1.2s)
        const minLoadingTime = 5000;
        const timeElapsed = Date.now() - startTime;
        const remainingTime = Math.max(0, minLoadingTime - timeElapsed);

        setTimeout(() => {
          setAnalysisResult(result);
          setAppState('results');
        }, remainingTime);

      } catch (error) {
        console.error('Analysis failed:', error);
        setTimeout(() => {
          setAnalysisResult({ error: "Connection to Argus AI server lost. Please try again." });
          setAppState('results');
        }, 1000);
      }
    };

    const handleAnalysisComplete = (e) => {
      // This is now handled within handleStartAnalysis above
    };

    window.addEventListener('startAnalysis', handleStartAnalysis);
    window.addEventListener('analysisComplete', handleAnalysisComplete);

    return () => {
      window.removeEventListener('startAnalysis', handleStartAnalysis);
      window.removeEventListener('analysisComplete', handleAnalysisComplete);
    };
  }, []);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  const resetToHome = () => {
    setAppState('home');
    setActiveUrl('');
    window.scrollTo({ top: 0, behavior: 'instant' });
  };

  const scrollToInput = () => {
    const section = document.getElementById('cta');
    if (section) section.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFinalCtaSelect = (url) => {
    const event = new CustomEvent('startAnalysis', { detail: { url } });
    window.dispatchEvent(event);
  };

  return (
    <div className="min-h-screen w-full bg-bg">

      {appState === 'home' && (
        <>
          <Navbar theme={theme} onThemeToggle={toggleTheme} onCtaClick={scrollToInput} />
          <main className="relative">
            <HeroSection theme={theme} onCtaClick={scrollToInput} />
            <HowItWorks />
            <DetectionEngines />
            <RiskScoreDemo />
            <ImpactSection />
            <CallToAction onVerificationStart={handleFinalCtaSelect} />
          </main>
          <Footer />
        </>
      )}

      {appState === 'analyzing' && (
        <AnalysisLoading />
      )}

      {appState === 'results' && (
        <ResultsDashboard result={analysisResult} onReset={resetToHome} />
      )}

    </div>
  );
}

export default App;
