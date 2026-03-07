# Project Argus: Requirements & Features

Project Argus is a production-hardened rental scam detection system designed for the Indian real estate market.

## 1. Functional Requirements

### 1.1 Detection Engines
- **Price Anomaly Detection**:
    - Compares listing prices against regional market medians for 6+ major Indian cities.
    - Normalizes pricing to price-per-sqft where data is available.
- **ML Risk Assessment**:
    - Implement an **IsolationForest** model for unsupervised anomaly detection.
    - Generate a normalized risk score from 0 (Safe) to 100 (High Risk).
- **Text & Urgency Analysis**:
    - Detect high-pressure sales tactics and "advance token" demands using NLP.
- **Broker Behavioral Fingerprinting**:
    - Track and flag phone number reuse and mass-listing patterns.

### 1.2 User Experience
- **URL Submission**: Support direct URL input from 99acres, Housing.com, and NoBroker.
- **Cinematic Loading State**: Visually represent forensic analysis steps (Scraping, Anomaly Detection, AI Reasoning).
- **Interactive Results Dashboard**:
    - Display risk verdict with color-coded badges.
    - Visualize forensic signals (Price, Urgency, Phone, Images).
    - Provide AI-generated descriptive reasoning.
    - Offer actionable recommendations.

## 2. Technical Requirements

### 2.1 Backend
- **Framework**: FastAPI (Python).
- **Architecture**: Modular forensic pipeline.
- **AI Integration**: OpenRouter API for explainable AI reasoning.
- **Performance**: Analysis completion in <10 seconds.

### 2.2 Frontend
- **Framework**: React.js with Tailwind CSS.
- **Animations**: GSAP for cinematic transitions and gauge animations.
- **Responsiveness**: Mobile-first design for seamless usage on smartphones.

## 3. Data Requirements

### 3.1 Market Benchmarks
- **Coverage**: Bangalore, Mumbai, Delhi, Pune, Hyderabad, Chennai.
- **Granularity**: Locality-specific median pricing data.

### 3.2 Security
- **Privacy**: No persistent storage of user PII or analyzed URLs (Stateless Analysis).
- **Schema**: Standardized JSON response structure across all endpoints.
