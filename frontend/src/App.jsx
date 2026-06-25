import { useState } from 'react';
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import { clearPatient, loadPatient } from './components/LoginGate';

export default function App() {
  const [patient, setPatient] = useState(() => loadPatient());

  function handleLogin(patientData) {
    setPatient(patientData);
  }

  function handleLogout() {
    clearPatient();
    setPatient(null);
  }

  if (!patient) {
    return <LandingPage onLoginSuccess={handleLogin} />;
  }

  return <Dashboard patient={patient} onLogout={handleLogout} />;
}

