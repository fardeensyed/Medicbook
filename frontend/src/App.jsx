import { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import LoginGate, { clearPatient, loadPatient } from './components/LoginGate';

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
    return <LoginGate onLogin={handleLogin} />;
  }

  return <ChatWindow patient={patient} onLogout={handleLogout} />;
}
