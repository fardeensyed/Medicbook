import { useEffect, useState } from 'react';
import { getDepartments, getDoctors, loginPatient, registerPatient } from '../api/client';
import { savePatient } from './LoginGate';

export default function LandingPage({ onLoginSuccess }) {
  const [doctors, setDoctors] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedDept, setSelectedDept] = useState('All');
  const [loading, setLoading] = useState(true);
  
  // Auth modal states
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authTab, setAuthTab] = useState('login'); // 'login' | 'register'
  const [name, setName] = useState('');
  const [contact, setContact] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  // Inquiry form states
  const [inquiryName, setInquiryName] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquiryMsg, setInquiryMsg] = useState('');
  const [inquirySuccess, setInquirySuccess] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [docsData, deptsData] = await Promise.all([
          getDoctors(),
          getDepartments()
        ]);
        setDoctors(docsData);
        setDepartments(deptsData);
      } catch (err) {
        console.error('Failed to load landing data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  async function handleAuthSubmit(e) {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      let data;
      if (authTab === 'login') {
        data = await loginPatient(contact.trim());
      } else {
        if (!name.trim()) {
          throw new Error('Please enter your full name to register.');
        }
        data = await registerPatient(name.trim(), contact.trim());
      }
      savePatient(data);
      onLoginSuccess({
        patientId: data.patient_id,
        name: data.name,
        contact: data.email_or_phone,
      });
      setShowAuthModal(false);
    } catch (err) {
      setAuthError(err.message || 'Authentication failed. Please check your inputs.');
    } finally {
      setAuthLoading(false);
    }
  }

  function handleInquirySubmit(e) {
    e.preventDefault();
    setInquirySuccess(true);
    setInquiryName('');
    setInquiryEmail('');
    setInquiryMsg('');
  }

  const filteredDoctors = selectedDept === 'All'
    ? doctors
    : doctors.filter(doc => doc.department_name === selectedDept);

  return (
    <div className="landing-page">
      <header className="landing-header">
        <a href="/" className="landing-logo">
          <div className="brand-icon">+</div>
          <h1>MediBook</h1>
        </a>
        <nav className="landing-nav">
          <a href="#features">Features</a>
          <a href="#doctors">Doctors</a>
          <a href="#inquire">Inquire</a>
          <button className="btn btn-outline" onClick={() => { setAuthTab('login'); setShowAuthModal(true); }}>
            Sign In
          </button>
          <button className="btn btn-primary" onClick={() => { setAuthTab('register'); setShowAuthModal(true); }}>
            Register
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h2>Your Medical Appointments, Simplified.</h2>
          <p>
            MediBook helps you browse specialist doctors, review their schedules, and book slots in seconds. Supported by our intelligent 24/7 AI chat assistant to manage your bookings instantly.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary btn-lg" onClick={() => { setAuthTab('register'); setShowAuthModal(true); }}>
              Get Started Now
            </button>
            <a href="#doctors" className="btn btn-secondary btn-lg">
              Meet the Doctors
            </a>
          </div>
        </div>

        <div className="hero-image-container">
          <div className="hero-glow-card">
            <div className="hero-stat-badge">
              <div className="hero-stat-icon">💬</div>
              <div className="hero-stat-info">
                <h4>AI Chat Assistant</h4>
                <p>Book & cancel via chat 24/7</p>
              </div>
            </div>
            <div className="hero-stat-badge">
              <div className="hero-stat-icon">📅</div>
              <div className="hero-stat-info">
                <h4>Flexible Schedules</h4>
                <p>View free time slots instantly</p>
              </div>
            </div>
            <div className="hero-stat-badge">
              <div className="hero-stat-icon">👨‍⚕️</div>
              <div className="hero-stat-info">
                <h4>Expert Specialists</h4>
                <p>Cardiology, Dermatology & more</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="landing-section">
        <div className="section-header">
          <h2>Why Choose MediBook?</h2>
          <p>We combine healthcare organization with state-of-the-art conversational AI.</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-card-icon">⚡</span>
            <h3>Instant Booking</h3>
            <p>Skip the phone lines. Select a doctor, pick a date, and confirm your slot in seconds.</p>
          </div>
          <div className="feature-card">
            <span className="feature-card-icon">🤖</span>
            <h3>Chat-Based Rescheduling</h3>
            <p>Our smart chatbot allows you to reschedule or cancel bookings naturally in normal language.</p>
          </div>
          <div className="feature-card">
            <span className="feature-card-icon">📊</span>
            <h3>Patient Dashboard</h3>
            <p>Log in to view all your upcoming appointments in one clear, beautifully-arranged space.</p>
          </div>
        </div>
      </section>

      {/* Doctors Directory Section */}
      <section id="doctors" className="landing-section" style={{ background: '#ffffff' }}>
        <div className="section-header">
          <h2>Meet Our Doctors</h2>
          <p>Check doctor departments, available days, and working hours.</p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>Loading doctors directory…</div>
        ) : (
          <>
            <div className="department-filter-bar">
              <button
                className={`filter-btn ${selectedDept === 'All' ? 'active' : ''}`}
                onClick={() => setSelectedDept('All')}
              >
                All Departments
              </button>
              {departments.map((dept) => (
                <button
                  key={dept.id}
                  className={`filter-btn ${selectedDept === dept.name ? 'active' : ''}`}
                  onClick={() => setSelectedDept(dept.name)}
                >
                  {dept.name}
                </button>
              ))}
            </div>

            <div className="landing-doctors-grid">
              {filteredDoctors.map((doc) => (
                <div key={doc.id} className="doctor-public-card">
                  <div className="doc-info-header">
                    <div className="doc-avatar">
                      {doc.name.split(' ').slice(-1)[0][0]}
                    </div>
                    <div className="doc-name-dept">
                      <h3>{doc.name}</h3>
                      <span>{doc.department_name}</span>
                    </div>
                  </div>
                  <div className="doc-availability">
                    <p><strong>Days:</strong> {doc.available_days}</p>
                    <p><strong>Hours:</strong> {doc.available_start_time.slice(0, 5)} - {doc.available_end_time.slice(0, 5)}</p>
                  </div>
                  <button
                    className="btn btn-outline"
                    style={{ marginTop: 'auto' }}
                    onClick={() => {
                      setAuthTab('login');
                      setShowAuthModal(true);
                    }}
                  >
                    Check Available Slots
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </section>

      {/* Inquiries Section */}
      <section id="inquire" className="landing-section inquiry-section">
        <div className="inquiry-grid">
          <div>
            <h2 style={{ fontSize: '2rem', color: 'var(--color-primary-dark)', margin: '0 0 16px 0' }}>
              Have Questions? Get in Touch
            </h2>
            <p style={{ color: 'var(--color-text-muted)', marginBottom: '24px' }}>
              If you have any questions about registration, department operating hours, or need support with appointment booking, send us an inquiry. Our administration team is here to assist.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <p>📍 <strong>Location:</strong> 123 Healthcare Blvd, Suite 100</p>
              <p>📞 <strong>Phone Support:</strong> +1 (555) 123-4567</p>
              <p>✉️ <strong>Email:</strong> support@medibook.example.com</p>
            </div>
          </div>

          <div className="inquiry-form-card">
            {inquirySuccess ? (
              <div className="form-success-state">
                <span className="form-success-icon">✓</span>
                <h3>Inquiry Submitted!</h3>
                <p style={{ color: 'var(--color-text-muted)' }}>
                  Thank you for contacting us. We will review your message and reply via email within 24 hours.
                </p>
                <button className="btn btn-secondary" onClick={() => setInquirySuccess(false)}>
                  Send Another Inquiry
                </button>
              </div>
            ) : (
              <form onSubmit={handleInquirySubmit}>
                <div>
                  <label htmlFor="inquiry-name">Your Name</label>
                  <input
                    id="inquiry-name"
                    type="text"
                    placeholder="Jane Doe"
                    value={inquiryName}
                    onChange={(e) => setInquiryName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="inquiry-email">Email Address</label>
                  <input
                    id="inquiry-email"
                    type="email"
                    placeholder="jane@example.com"
                    value={inquiryEmail}
                    onChange={(e) => setInquiryEmail(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="inquiry-msg">Message / Inquiry Details</label>
                  <textarea
                    id="inquiry-msg"
                    rows="4"
                    placeholder="Tell us what you need help with…"
                    value={inquiryMsg}
                    onChange={(e) => setInquiryMsg(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary">
                  Submit Inquiry
                </button>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: '30px', background: 'var(--color-text)', color: '#94a3b8', fontSize: '0.85rem' }}>
        <p>© 2026 MediBook Appointment Portal. All rights reserved.</p>
        <p>Built using React & FastAPI</p>
      </footer>

      {/* Auth Modal Popup */}
      {showAuthModal && (
        <div className="auth-modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
            <div className="auth-tabs">
              <button
                className={`auth-tab-btn ${authTab === 'login' ? 'active' : ''}`}
                onClick={() => { setAuthTab('login'); setAuthError(''); }}
              >
                Sign In
              </button>
              <button
                className={`auth-tab-btn ${authTab === 'register' ? 'active' : ''}`}
                onClick={() => { setAuthTab('register'); setAuthError(''); }}
              >
                Register
              </button>
            </div>
            
            <div className="auth-body">
              <form onSubmit={handleAuthSubmit}>
                {authTab === 'register' && (
                  <>
                    <label htmlFor="auth-name">Full Name</label>
                    <input
                      id="auth-name"
                      type="text"
                      placeholder="Jane Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                    />
                  </>
                )}

                <label htmlFor="auth-contact">Email or Phone</label>
                <input
                  id="auth-contact"
                  type="text"
                  placeholder="jane@example.com"
                  value={contact}
                  onChange={(e) => setContact(e.target.value)}
                  required
                />

                {authError && <p className="form-error" style={{ margin: '0' }}>{authError}</p>}

                <button type="submit" className="btn btn-primary" disabled={authLoading}>
                  {authLoading ? 'Please wait…' : authTab === 'login' ? 'Sign In' : 'Register Now'}
                </button>
              </form>
              <button className="auth-close-btn" onClick={() => setShowAuthModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
