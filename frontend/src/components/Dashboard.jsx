import { useEffect, useState } from 'react';
import { cancelAppointment, getAvailableSlots, getDoctors, getPatientAppointments } from '../api/client';
import ChatWindow from './ChatWindow';

export default function Dashboard({ patient, onLogout }) {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'doctors' | 'slots'
  
  // Slot checker state
  const [checkDocId, setCheckDocId] = useState('');
  const [checkDate, setCheckDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });
  const [checkedSlots, setCheckedSlots] = useState([]);
  const [checkingSlots, setCheckingSlots] = useState(false);
  const [slotsError, setSlotsError] = useState('');

  // Floating Chatbot state
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Fetch appointments and doctors list
  const fetchAppointments = async () => {
    try {
      const data = await getPatientAppointments(patient.patientId);
      setAppointments(data);
    } catch (err) {
      console.error('Failed to load patient appointments:', err);
    }
  };

  useEffect(() => {
    async function loadDashboardData() {
      setLoading(true);
      try {
        await Promise.all([
          fetchAppointments(),
          getDoctors().then(data => setDoctors(data))
        ]);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, [patient.patientId]);

  // Handle slot checking
  const handleCheckSlots = async (e) => {
    if (e) e.preventDefault();
    if (!checkDocId || !checkDate) return;
    
    setCheckingSlots(true);
    setSlotsError('');
    setCheckedSlots([]);

    try {
      const res = await getAvailableSlots(checkDate, Number(checkDocId));
      const doctorSlots = res.doctors?.[0]?.slots || [];
      setCheckedSlots(doctorSlots);
    } catch (err) {
      setSlotsError(err.message || 'Failed to check slots. Note: past dates are invalid.');
    } finally {
      setCheckingSlots(false);
    }
  };

  // Handle appointment cancellation from table
  const handleCancelAppointment = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this appointment?')) return;
    try {
      await cancelAppointment(id);
      await fetchAppointments(); // refresh
    } catch (err) {
      alert(`Error cancelling appointment: ${err.message}`);
    }
  };

  // Callback triggered when chatbot books/cancels/reschedules an appointment
  const handleAppointmentChanged = () => {
    fetchAppointments();
  };

  const activeAppts = appointments.filter(a => a.status !== 'cancelled');

  return (
    <div className="dashboard-container">
      {/* Sidebar Navigation */}
      <aside className="dashboard-sidebar">
        <div>
          <div className="sidebar-header">
            <div className="brand-icon">+</div>
            <h2>MediBook</h2>
          </div>
          <nav className="sidebar-nav">
            <button
              className={`sidebar-nav-btn ${activeTab === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveTab('overview')}
            >
              📊 Overview
            </button>
            <button
              className={`sidebar-nav-btn ${activeTab === 'doctors' ? 'active' : ''}`}
              onClick={() => setActiveTab('doctors')}
            >
              👨‍⚕️ Doctors Directory
            </button>
            <button
              className={`sidebar-nav-btn ${activeTab === 'slots' ? 'active' : ''}`}
              onClick={() => setActiveTab('slots')}
            >
              📅 Slot Checker
            </button>
          </nav>
        </div>

        <div className="sidebar-footer">
          <div className="patient-profile-info">
            <p>{patient.name}</p>
            <span>{patient.contact}</span>
          </div>
          <button className="btn btn-outline" onClick={onLogout} style={{ width: '100%' }}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Dashboard Area */}
      <main className="dashboard-main">
        {/* Header bar */}
        <header className="dashboard-header">
          <div>
            <h2>Welcome back, {patient.name.split(' ')[0]}!</h2>
            <p>Here is your appointment overview.</p>
          </div>
        </header>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '100px' }}>Loading your dashboard…</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="tab-content">
                {/* Stats row */}
                <div className="dashboard-stats">
                  <div className="stat-card">
                    <div className="stat-card-icon">📅</div>
                    <div className="stat-card-info">
                      <h3>{activeAppts.length}</h3>
                      <p>Active Appointments</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-icon">👨‍⚕️</div>
                    <div className="stat-card-info">
                      <h3>{doctors.length}</h3>
                      <p>Available Specialists</p>
                    </div>
                  </div>
                </div>

                {/* Active Appointments panel */}
                <div className="dashboard-panel">
                  <div className="dashboard-panel-header">
                    <h3>Your Upcoming Appointments</h3>
                  </div>

                  {activeAppts.length === 0 ? (
                    <div className="no-appointments-card">
                      <span className="no-appointments-icon">📭</span>
                      <p>You have no active appointments booked.</p>
                      <button className="btn btn-primary" onClick={() => setIsChatOpen(true)} style={{ marginTop: '10px' }}>
                        Book via AI Assistant
                      </button>
                    </div>
                  ) : (
                    <div className="appointments-table-container">
                      <table className="appointments-table">
                        <thead>
                          <tr>
                            <th>Appointment ID</th>
                            <th>Doctor</th>
                            <th>Department</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                            <th>Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {activeAppts.map((appt) => (
                            <tr key={appt.id}>
                              <td>#{appt.id}</td>
                              <td><strong>{appt.doctor_name}</strong></td>
                              <td>{appt.department_name}</td>
                              <td>{new Date(appt.appointment_date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</td>
                              <td>{appt.appointment_time.slice(0, 5)}</td>
                              <td>
                                <span className={`status-badge status-badge--${appt.status}`}>
                                  {appt.status}
                                </span>
                              </td>
                              <td>
                                <button
                                  className="btn btn-danger btn-ghost"
                                  onClick={() => handleCancelAppointment(appt.id)}
                                >
                                  Cancel
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'doctors' && (
              <div className="dashboard-panel">
                <div className="dashboard-panel-header">
                  <h3>Our Medical Specialists</h3>
                </div>
                <div className="landing-doctors-grid">
                  {doctors.map((doc) => (
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
                        className="btn btn-secondary"
                        onClick={() => {
                          setCheckDocId(String(doc.id));
                          setActiveTab('slots');
                        }}
                      >
                        Check Free Slots
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'slots' && (
              <div className="dashboard-panel">
                <div className="dashboard-panel-header">
                  <h3>Real-time Appointment Slot Checker</h3>
                </div>
                <div className="slot-checker-grid">
                  <form onSubmit={handleCheckSlots} className="slot-checker-form">
                    <label htmlFor="slot-doctor">Select Specialist</label>
                    <select
                      id="slot-doctor"
                      value={checkDocId}
                      onChange={(e) => setCheckDocId(e.target.value)}
                      required
                    >
                      <option value="">-- Choose Doctor --</option>
                      {doctors.map(doc => (
                        <option key={doc.id} value={doc.id}>
                          {doc.name} ({doc.department_name})
                        </option>
                      ))}
                    </select>

                    <label htmlFor="slot-date">Choose Date</label>
                    <input
                      id="slot-date"
                      type="date"
                      value={checkDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setCheckDate(e.target.value)}
                      required
                    />

                    <button type="submit" className="btn btn-primary" disabled={checkingSlots || !checkDocId}>
                      {checkingSlots ? 'Checking slots…' : 'Search Available Slots'}
                    </button>
                  </form>

                  <div className="slots-result-panel">
                    <h4>Available Time Slots</h4>
                    {checkingSlots ? (
                      <p>Querying live slots database…</p>
                    ) : slotsError ? (
                      <p className="form-error">{slotsError}</p>
                    ) : checkedSlots.length > 0 ? (
                      <div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: '14px' }}>
                          Following slots are free on {checkDate}. To book one, click the chatbot in the bottom right and type e.g., <em>"Book {doctors.find(d => String(d.id) === checkDocId)?.name} for {checkedSlots[0]} on {checkDate}"</em>.
                        </p>
                        <div className="slot-chips">
                          {checkedSlots.map((slot) => (
                            <span key={slot} className="slot-chip" style={{ fontSize: '0.9rem', padding: '6px 12px' }}>
                              {slot.slice(0, 5)}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : checkDocId ? (
                      <p style={{ color: 'var(--color-text-muted)' }}>No free slots found for the selected specialist on this date.</p>
                    ) : (
                      <p style={{ color: 'var(--color-text-muted)' }}>Select a doctor and date to view slot availability.</p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Floating Chatbot Assistant Widget */}
      <button
        className={`chatbot-float-trigger ${isChatOpen ? 'chatbot-float-trigger--open' : ''}`}
        onClick={() => setIsChatOpen(!isChatOpen)}
        aria-label="Toggle chat assistant"
      >
        {isChatOpen ? '✕' : '💬'}
      </button>

      <div className={`chatbot-float-window ${isChatOpen ? 'chatbot-float-window--open' : ''}`}>
        <ChatWindow
          patient={patient}
          onLogout={onLogout}
          onAppointmentChange={handleAppointmentChanged}
        />
      </div>
    </div>
  );
}
