import React, { useState } from 'react';
import './Alerts.css';

const Alerts = () => {
  const [isSimulating, setIsSimulating] = useState(false);

  const signalWeights = [
    { label: 'New/untrusted device', weight: '+20', color: 'orange' },
    { label: 'Action < 10s after login', weight: '+15', color: 'orange' },
    { label: 'Amount > 2.5× 90-day avg', weight: '+25', color: 'red' },
    { label: 'OTP retry > 2 attempts', weight: '+20', color: 'orange' },
    { label: 'First-time fund type', weight: '+15', color: 'orange' },
    { label: 'Cancel-retry loop > 3×', weight: '+10', color: 'green' },
    { label: 'Night transfer > ₹50k', weight: '+10', color: 'green' },
  ];

  const recentEvaluations = [
    { desc: 'SIP ₹3k · Priya', score: 12, status: 'allow' },
    { desc: 'Transfer ₹1.2L · Arjun', score: 72, status: 'block' },
    { desc: 'ELSS ₹25k · Ramesh', score: 40, status: 'warn' },
    { desc: 'Gold buy · Priya', score: 8, status: 'allow' },
    { desc: 'NPS ₹5k · Neha', score: 20, status: 'allow' },
  ];

  return (
    <div className="main-content">
      {/* Header with Toggle */}
      <header className="fraud-header">
        <div className="title-block">
          <h1>Fraud intercept</h1>
          <p className="subtext">Every wealth action passes through this gate</p>
        </div>
        <div className="simulation-toggle">
          <span className="toggle-label">Live simulation</span>
          <label className="switch">
            <input 
              type="checkbox" 
              checked={isSimulating} 
              onChange={() => setIsSimulating(!isSimulating)} 
            />
            <span className="slider round"></span>
          </label>
        </div>
      </header>

      {/* Grid Layout */}
      <div className="dashboard-grid">
        {/* Signal Weights Card */}
        <div className="content-card">
          <h3 className="card-inner-title">Signal weights</h3>
          <div className="signal-list">
            {signalWeights.map((item, index) => (
              <div key={index} className="signal-row">
                <div className="signal-left">
                  <span className={`dot ${item.color}`}></span>
                  <span className="signal-label">{item.label}</span>
                </div>
                <span className="weight-val">{item.weight}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Evaluations Card */}
        <div className="content-card">
          <h3 className="card-inner-title">Recent evaluations</h3>
          <div className="eval-list">
            {recentEvaluations.map((item, index) => (
              <div key={index} className="eval-row">
                <span className="eval-desc">{item.desc}</span>
                <div className="eval-right">
                  <span className="eval-score">Score {item.score}</span>
                  <span className={`status-pill ${item.status}`}>
                    {item.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Demo Triggers Footer Card */}
      <div className="content-card demo-card">
        <h3 className="card-inner-title">Demo triggers</h3>
        <div className="trigger-buttons">
          <button className="trigger-btn block">block gate · score 72</button>
          <button className="trigger-btn warn">warn gate · score 40</button>
          <button className="trigger-btn allow">allow gate · score 8</button>
        </div>
        <div className="info-box">
          Toggle the live simulation switch above to auto-trigger scenarios every 6 seconds — useful for hands-free demos.
        </div>
      </div>
    </div>
  );
};

export default Alerts;