const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.detail || data.message || `Request failed (${response.status})`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }

  return data;
}

export async function identifyPatient(name, emailOrPhone) {
  return request('/auth/identify', {
    method: 'POST',
    body: JSON.stringify({ name, email_or_phone: emailOrPhone }),
  });
}

export async function sendChat(patientId, sessionId, message) {
  return request('/chat', {
    method: 'POST',
    body: JSON.stringify({
      patient_id: patientId,
      session_id: sessionId,
      message,
    }),
  });
}

export async function loginPatient(emailOrPhone) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email_or_phone: emailOrPhone }),
  });
}

export async function registerPatient(name, emailOrPhone) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email_or_phone: emailOrPhone }),
  });
}

export async function getDoctors() {
  return request('/appointments/doctors');
}

export async function getDepartments() {
  return request('/appointments/departments');
}

export async function getPatientAppointments(patientId) {
  return request(`/appointments/patient/${patientId}`);
}

export async function cancelAppointment(appointmentId) {
  return request(`/appointments/${appointmentId}`, {
    method: 'DELETE',
  });
}

export async function getAvailableSlots(date, doctorId, departmentId) {
  let url = `/appointments/slots?date=${date}`;
  if (doctorId) {
    url += `&doctor_id=${doctorId}`;
  }
  if (departmentId) {
    url += `&department_id=${departmentId}`;
  }
  return request(url);
}

