import React, { useState, useEffect } from 'react';
import { gsap } from 'gsap';
import { CheckCircle2, Loader2 } from 'lucide-react';
import heroNight from '../assets/hero-night.jpg';

const AnalysisLoading = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const steps = [
        "Extracting listing data",
        "Running anomaly detection",
        "Cross-checking broker activity",
        "Generating AI explanation"
    ];

    useEffect(() => {
        // Progress through steps every 1s for demo
        const interval = setInterval(() => {
            setCurrentStep(prev => {
                if (prev < steps.length - 1) return prev + 1;
                clearInterval(interval);
                return prev;
            });
        }, 1000);

        // Initial fade in
        gsap.fromTo('.loading-container',
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 1, ease: 'power2.out' }
        );

        return () => clearInterval(interval);
    }, [steps.length]);

    // Animate new steps appearing
    useEffect(() => {
        const stepSelector = `.step-${currentStep}`;
        if (document.querySelector(stepSelector)) {
            gsap.fromTo(stepSelector,
                { opacity: 0, x: -10 },
                { opacity: 1, x: 0, duration: 0.5, ease: 'power2.out' }
            );
        }
    }, [currentStep]);

    return (
        <div className="loading-screen" style={styles.screen}>
            {/* Background Layer */}
            <div style={{
                ...styles.heroBackground,
                backgroundImage: `linear-gradient(rgba(10,10,10,0.75), rgba(10,10,10,0.9)), url(${heroNight})`
            }} />

            <div className="loading-container" style={styles.container}>
                <h2 style={styles.heading}>ARGUS AI ANALYSIS</h2>
                <div style={styles.stepsContainer}>
                    {steps.map((step, index) => {
                        const isCompleted = index < currentStep;
                        const isActive = index === currentStep;
                        const isFuture = index > currentStep;

                        return (
                            <div
                                key={index}
                                className={`step-${index}`}
                                style={{
                                    ...styles.stepRow,
                                    opacity: isFuture ? 0.3 : 1,
                                    color: isActive ? 'var(--accent)' : 'white'
                                }}
                            >
                                <div style={styles.iconWrapper}>
                                    {isCompleted ? (
                                        <CheckCircle2 size={18} color="#10b981" />
                                    ) : isActive ? (
                                        <Loader2 size={18} className="animate-spin" color="var(--accent)" />
                                    ) : (
                                        <div style={styles.dot} />
                                    )}
                                </div>
                                <span style={{
                                    ...styles.stepText,
                                    fontWeight: isActive ? '600' : '400',
                                    color: isActive ? 'var(--accent)' : 'rgba(255,255,255,0.8)'
                                }}>
                                    {step}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Bottom Progress Bar */}
            <div style={styles.progressTrack}>
                <div
                    className="loading-progress-fill"
                    style={{
                        ...styles.progressFill,
                        width: `${((currentStep + 1) / steps.length) * 100}%`
                    }}
                />
            </div>
        </div>
    );
};

const styles = {
    screen: {
        height: '100vh',
        width: '100vw',
        backgroundColor: '#0c0a09',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'fixed',
        top: 0,
        left: 0,
        zIndex: 1000,
        overflow: 'hidden'
    },
    heroBackground: {
        position: 'absolute',
        inset: 0,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
        zIndex: -1
    },
    container: {
        maxWidth: '400px',
        width: '100%',
        padding: '40px',
        textAlign: 'center',
        zIndex: 10
    },
    heading: {
        fontFamily: "var(--font-display)",
        fontSize: '14px',
        fontWeight: 800,
        color: 'white',
        letterSpacing: '0.2em',
        marginBottom: '48px',
        opacity: 0.9
    },
    stepsContainer: {
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        alignItems: 'flex-start',
        width: 'fit-content',
        margin: '0 auto'
    },
    stepRow: {
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        transition: 'all 0.3s ease',
    },
    iconWrapper: {
        width: '24px',
        height: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
    },
    dot: {
        width: '4px',
        height: '4px',
        borderRadius: '50%',
        backgroundColor: 'rgba(255,255,255,0.3)'
    },
    stepText: {
        fontFamily: "var(--font-body)",
        fontSize: '16px',
    },
    progressTrack: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        width: '100%',
        height: '4px',
        backgroundColor: 'rgba(255,255,255,0.05)',
        zIndex: 20
    },
    progressFill: {
        height: '100%',
        backgroundColor: 'var(--accent)',
        transition: 'width 1s ease-in-out'
    }
};

export default AnalysisLoading;
