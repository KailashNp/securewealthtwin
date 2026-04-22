import React from 'react';
import RiskInterceptModal from '../components/RiskInterceptModal';

import { 
  LayoutDashboard, Target, Landmark, PieChart, 
  AlertTriangle, Settings, LogOut, TrendingUp, 
  Plus, ChevronRight, Scale, Clock, Zap, CreditCard,
  Search, Bell, User
} from 'lucide-react';
import './Networth.css';
// Add at the top:
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const NetWorth = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const chartData = [
    { m: 'JUN 23', h: 35 }, { m: '', h: 40 }, { m: '', h: 32 },
    { m: 'SEP 23', h: 45 }, { m: '', h: 48 }, { m: '', h: 52 },
    { m: 'DEC 23', h: 58 }, { m: '', h: 65 }, { m: '', h: 72 },
    { m: 'MAR 24', h: 78 }, { m: '', h: 85 }, { m: 'JUN 24', h: 100, active: true },
  ];

  useEffect(() => {
    setLoading(true);
    axios.get(`${API_BASE}/api/user/1/profile`)
      .then(res => setProfile(res.data))
      .catch(() => setProfile(null)) // hardcoded fallback stays visible
      .finally(() => setLoading(false));
  }, []);

  const [riskModal, setRiskModal] = useState({
  isOpen: false, decision: null, riskScore: 0, message: ""
});
const [pendingAction, setPendingAction] = useState(null);

const securityGate = async (actionToRun, metadata) => {
  try {
    const res = await axios.post(`${API_BASE}/api/action/execute`, metadata);
    setPendingAction(() => actionToRun);
    setRiskModal({
      isOpen: true,
      decision: res.data.decision,
      riskScore: res.data.riskScore,
      message: res.data.message
    });
  } catch {
    setRiskModal({
      isOpen: true,
      decision: 'BLOCK',
      message: "Security protocols offline. Wealth actions restricted."
    });
  }
};

  
  return (
    <div className="dashboard-container">
      

      {/* MAIN CONTENT */}
      <main className="main-content">
        

        {/* HERO SECTION */}
        <section className="hero-section">
          <div className="hero-text">
            <span className="insight-tag" style={{color: 'var(--primary-teal)'}}>EXECUTIVE SUMMARY</span>
            <h1>Net Worth<br/>Calculator</h1>
            <p>Comprehensive analysis of your institutional assets and liabilities for the current fiscal quarter.</p>
          </div>

          <div className="networth-card">
  
  <div className="networth-left">
    <div className="networth-icon">₹</div>
    
    <div>
      <p className="networth-label">Aggregate Net Worth</p>
      <h2 className="networth-value">
        {profile?.netWorth || '34,80,000'}
      </h2>
    </div>
  </div>

  <div className="networth-right">
    <span className="networth-growth">
      +{profile?.netWorthTrend || '12.4%'}
    </span>
    <span className="networth-sub">vs last year</span>
  </div>

</div>
        </section>

        {/* GROWTH TRAJECTORY CHART */}
        <section className="chart-card" style={{marginBottom: '32px'}}>
          <div className="chart-header">
            <div>
              <h3>Growth Trajectory</h3>
              <p>12-month net worth evolution</p>
            </div>
            <div className="time-filters">
              <span className="active">1Y</span>
              <span>5Y</span>
              <span>ALL</span>
            </div>
          </div>
          
          <div className="bar-chart-container">
            {chartData.map((bar, i) => (
              <div key={i} className="bar-column">
                <div 
                  className={`bar-fill ${bar.active ? 'active' : ''}`} 
                  style={{ height: `${bar.h}%` }}
                ></div>
                <span className="bar-label">{bar.m}</span>
              </div>
            ))}
          </div>
        </section>

        {/* DATA GRID */}
        <div className="charts-grid">
           <div className="chart-card">
              <div className="chart-header">
                <div style={{display: 'flex', gap: '12px', alignItems: 'center'}}>
                  <div className="insight-icon tip" style={{margin: 0}}><PieChart size={18}/></div>
                  <h3>Liquid & Fixed Assets</h3>
                </div>
                <span className="insight-tag" style={{background: '#f0fdfa', padding: '4px 8px', borderRadius: '4px'}}>Total: ₹ 42,50,000</span>
              </div>
              <div className="asset-rows">
                <AssetRow label="Institutional Real Estate" sub="Tier-1 Portfolio" val="₹ 28,00,000" trend="+4.2%"/>
                <AssetRow label="Equities & Indices" sub="Vanguard All-World" val="₹ 8,40,000" trend="+12.8%"/>
                <AssetRow label="Fixed Income" sub="Treasury Bonds" val="₹ 4,10,000" trend="0.0%"/>
              </div>
             <button
  className="add-btn-placeholder"
  onClick={() => securityGate(
    () => alert("New asset category added!"),
    { actionType: 'ADD_ASSET', amount: 0 }
  )}
>
  <Plus size={16}/> Add New Asset Category
</button>
           </div>

           <div className="chart-card">
              <div className="chart-header">
                <div style={{display: 'flex', gap: '12px', alignItems: 'center'}}>
                  <div className="insight-icon strategy" style={{margin: 0, color: '#ef4444', background: '#fef2f2'}}><CreditCard size={18}/></div>
                  <h3>Liabilities & Debt</h3>
                </div>
                <span className="insight-tag" style={{background: '#fef2f2', padding: '4px 8px', borderRadius: '4px'}}>Total: ₹ 7,70,000</span>
              </div>
              <div className="asset-rows">
                <AssetRow label="Commercial Mortgage" sub="7.8% APR Fixed" val="₹ 6,20,000" trend="-₹ 15k Mon" isNeg/>
                <AssetRow label="Corporate Credit" sub="Amex Platinum" val="₹ 1,10,000" trend="Due in 12 days" isWarn/>
              </div>
              <div className="insight-card" style={{padding: '16px', marginTop: '20px', borderStyle: 'none', background: '#f9fbfb'}}>
                <h4 style={{fontSize: '14px', margin: '0 0 8px 0'}}>Debt Reduction Strategy</h4>
                <p style={{fontSize: '12px', margin: 0}}>Increase mortgage repayment by 10% to save ₹ 1.2L.</p>
                <button
  className="insight-link-btn"
  style={{marginTop: '8px'}}
  onClick={() => securityGate(
    () => alert("Debt reduction strategy applied!"),
    { actionType: 'DEBT_REDUCTION', amount: 62000 }
  )}
>
  Apply Strategy <ChevronRight size={14}/>
</button>
              </div>
           </div>
        </div>

        {/* BOTTOM STATS */}
        <div className="insights-grid">
          <StatCard icon={<Scale/>} label="Asset/Liability Ratio" val="5.51" type="tax" sub="Strong solvency"/>
          <StatCard icon={<Clock/>} label="Financial Freedom" val="14.2 Years" type="tip" sub="Withdrawal rate"/>
          <StatCard icon={<Zap/>} label="Portfolio Velocity" val="+1.8% / Mo" type="strategy" sub="Cap appreciation"/>
        </div>
      </main>

      <RiskInterceptModal
  isOpen={riskModal.isOpen}
  decision={riskModal.decision}
  riskScore={riskModal.riskScore}
  message={riskModal.message}
  onCancel={() => {
    setRiskModal({ ...riskModal, isOpen: false });
    setPendingAction(null);
  }}
  onAllow={() => {
    if (pendingAction) pendingAction();
    setRiskModal({ ...riskModal, isOpen: false });
    setPendingAction(null);
  }}
/>
    </div>
  );
};

const AssetRow = ({label, sub, val, trend, isNeg, isWarn}) => (
  <div style={{display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid #f3f4f6'}}>
    <div>
      <div style={{fontWeight: '700', fontSize: '14px'}}>{label}</div>
      <div style={{fontSize: '12px', color: 'var(--text-muted)'}}>{sub}</div>
    </div>
    <div style={{textAlign: 'right'}}>
      <div style={{fontWeight: '700', fontSize: '14px'}}>{val}</div>
      <div style={{fontSize: '11px', fontWeight: '700', color: isNeg ? '#ef4444' : isWarn ? '#f59e0b' : '#10b981'}}>{trend}</div>
    </div>
  </div>
);

const StatCard = ({icon, label, val, type, sub}) => (
  <div className="insight-card">
    <div className={`insight-icon ${type}`}>{icon}</div>
    <span className="insight-tag">{label}</span>
    <h4>{val}</h4>
    <p style={{margin: 0}}>{sub}</p>

  </div>

  
);

export default NetWorth;