import React, { useState } from 'react';
import './Register1.css';
import { 
  Landmark, UserCircle, ShieldCheck, Lock, 
  ArrowRight, ArrowLeft, Info 
} from 'lucide-react';

const Register = ({onBack, onNext}) => {
  const [accountNumber, setAccountNumber] = useState('');

  return (
    <div className="register-page">
      {/* 1. Multi-step Progress Header */}
      <div className="onboarding-steps">
        <div className="step active">
          <div className="step-icon-box">
            <Landmark size={20} />
          </div>
          <span className="step-label">VERIFICATION</span>
        </div>
        
        <div className="step-divider"></div>

        <div className="step disabled">
          <div className="step-icon-box">
            <UserCircle size={20} />
          </div>
          <span className="step-label">DETAILS</span>
        </div>

        <div className="step-divider"></div>

        <div className="step disabled">
          <div className="step-icon-box">
            <ShieldCheck size={20} />
          </div>
          <span className="step-label">FINANCIAL DETAILS</span>
        </div>
      </div>

      {/* 2. Main Verification Card */}
      <div className="verification-card">
        <div className="card-accent-border"></div>
        
        <div className="card-content">
          <h1 className="auth-title">Account Verification</h1>
          <p className="auth-subtitle">
            SecureWealth Twin requires a linked account to build your 
            architectural portfolio ledger.
          </p>

          <div className="form-group">
            <label className="input-label">ENTER BANK ACCOUNT NUMBER</label>
            <div className="input-wrapper">
              <input 
                type="text" 
                placeholder="0000 0000 0000 0000"
                value={accountNumber}
                onChange={(e) => setAccountNumber(e.target.value)}
              />
              <Lock className="input-icon" size={18} />
            </div>
            <div className="input-info">
              <Info size={14} />
              <span>This helps us securely sync your financial profile.</span>
            </div>
          </div>

          <button className="btn-continue" onClick={onNext}>
  Continue to Details <ArrowRight size={18} />
</button>

          <button onClick={onBack}className="btn-back">
            <ArrowLeft size={16} /> Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default Register;