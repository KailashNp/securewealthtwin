import React from 'react';

export default function HealthScoreBadge({ score }) {
  // SVG Math for the ring
  const r = 32;
  const circ = 2 * Math.PI * r;
  const offset = circ * (1 - score / 100);
  
  // Dynamic color logic based on performance thresholds
  const color = score >= 70 ? '#178CF2' : score >= 40 ? '#E8A020' : '#D94040';

  return (
    <div className="health-score-wrapper" style={{ position: 'relative', width: '80px', height: '80px' }}>
      <svg width="80" height="80" style={{ display: 'block' }}>
        {/* Background Circle (Gray Track) */}
        <circle 
          cx="40" 
          cy="40" 
          r={r} 
          stroke="#eee" 
          strokeWidth="7" 
          fill="none"
        />
        {/* Foreground Circle (Progress Ring) */}
        <circle 
          cx="40" 
          cy="40" 
          r={r} 
          stroke={color} 
          strokeWidth="7" 
          fill="none"
          strokeDasharray={circ} 
          strokeDashoffset={offset} 
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease, stroke 0.3s ease' }}
          transform="rotate(-90 40 40)"
        />
        {/* Score Text */}
        <text 
          x="40" 
          y="46" 
          textAnchor="middle" 
          fontSize="20" 
          fontWeight="800" 
          fill={color}
          style={{ fontFamily: 'Inter, sans-serif' }}
        >
          {score}
        </text>
      </svg>
    </div>
  );
}