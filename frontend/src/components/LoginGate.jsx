import { useState } from 'react';
import { identifyPatient } from '../api/client';

const STORAGE_KEYS = {
  patientId: 'medibook_patient_id',
  name: 'medibook_patient_name',
  contact: 'medibook_email_or_phone',
};

export function loadPatient() {
  const patientId = localStorage.getItem(STORAGE_KEYS.patientId);
  const name = localStorage.getItem(STORAGE_KEYS.name);
  const contact = localStorage.getItem(STORAGE_KEYS.contact);
  if (!patientId) return null;
  return { patientId: Number(patientId), name, contact };
}

export function savePatient({ patient_id, name, email_or_phone }) {
  localStorage.setItem(STORAGE_KEYS.patientId, String(patient_id));
  localStorage.setItem(STORAGE_KEYS.name, name);
  localStorage.setItem(STORAGE_KEYS.contact, email_or_phone);
}

export function clearPatient() {
  Object.values(STORAGE_KEYS).forEach((key) => localStorage.removeItem(key));
}

export default function LoginGate({ onLogin }) {
  const [name, setName] = useState('');
  const [contact, setContact] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await identifyPatient(name.trim(), contact.trim());
      savePatient(data);
      onLogin({
        patientId: data.patient_id,
        name: data.name,
        contact: data.email_or_phone,
      });
    } catch (err) {
      setError(err.message || 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="brand-icon" aria-hidden="true">+</div>
          <h1>MediBook</h1>
          <p>Your medical appointment assistant</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="name">Full name</label>
          <input
            id="name"
            type="text"
            placeholder="Jane Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            autoComplete="name"
          />

          <label htmlFor="contact">Email or phone</label>
          <input
            id="contact"
            type="text"
            placeholder="jane@example.com"
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            required
            autoComplete="email"
          />

          {error && <p className="form-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Continue to chat'}
          </button>
        </form>

        <p className="login-note">
          No password needed — we use your name and contact to identify your appointments.
        </p>
      </div>
    </div>
  );
}
