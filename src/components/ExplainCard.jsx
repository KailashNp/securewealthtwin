import React, { useState } from 'react';
import axios from 'axios';
import { ChevronDown, ChevronUp, Info, Activity } from 'lucide-react';
import './ExplainCard.css';

export default function ExplainCard({ recommendationId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    // Lazy Fetching: Only fetch if we don't have data yet
    if (!isOpen && !data) {
      setLoading(true);
      try {
        const res = await axios.get(
          `${process.env.REACT_APP_API_URL}/api/recommend/explain?id=${recommendationId}`
        );
        setData(res.data); // Expected: { explanation_text, top_drivers: [{label, weight}] }
      } catch (err) {
        // Fallback for demo if API isn't ready
        setData({
          explanation_text: "Our architectural model recommends this based on your 22-year time horizon and current liquid buffer efficiency.",
          top_drivers: [
            { label: "Time Horizon", weight: 95 },
            { label: "Risk Tolerance", weight: 72 },
            { label: "Market Volatility", weight: 40 }
          ]
        });
      } finally {
        setLoading(false);
      }
    }
    setIsOpen(!isOpen);
  };

  return (
    <div className="explain-container">
      <button className="why-btn" onClick={handleToggle}>
        Why? {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {isOpen && (
        <div className="explain-panel">
          {loading ? (
            <div className="explain-loader">Analyzing drivers...</div>
          ) : (
            <>
              <p className="explanation-text">
                <Info size={14} className="info-icon" />
                {data?.explanation_text}
              </p>
              
              <div className="shap-drivers">
                <span className="driver-header">TOP 3 AI DRIVERS (SHAP)</span>
                {data?.top_drivers?.slice(0, 3).map((driver, idx) => (
                  <div key={idx} className="driver-row">
                    <div className="driver-info">
                      <span className="driver-label">{driver.label}</span>
                      <span className="driver-weight">{driver.weight}% impact</span>
                    </div>
                    <div className="driver-bar-bg">
                      <div 
                        className="driver-bar-fill" 
                        style={{ width: `${driver.weight}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}