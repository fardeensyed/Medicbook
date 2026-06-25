function formatStatus(status) {
  if (!status) return '—';
  return status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function SlotsList({ doctors }) {
  if (!doctors?.length) {
    return <p className="card-muted">No slots available.</p>;
  }

  return (
    <div className="slots-list">
      {doctors.map((doc) => (
        <div key={doc.doctor_id || doc.doctor_name} className="slots-group">
          <p className="slots-doctor">{doc.doctor_name}</p>
          <div className="slot-chips">
            {(doc.slots || []).map((slot) => (
              <span key={slot} className="slot-chip">{slot}</span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function BookingSummaryCard({ data }) {
  if (!data?.type) return null;

  const titles = {
    booking_confirmation: 'Appointment Confirmed',
    cancellation_confirmation: 'Appointment Cancelled',
    reschedule_confirmation: 'Appointment Rescheduled',
    available_slots: 'Available Slots',
  };

  const title = titles[data.type] || 'Appointment Details';

  if (data.type === 'available_slots') {
    return (
      <div className="summary-card">
        <div className="summary-card-header">
          <span className="summary-card-icon" aria-hidden="true">📅</span>
          <h3>{title}</h3>
        </div>
        <dl className="summary-grid">
          <div>
            <dt>Date</dt>
            <dd>{data.date || '—'}</dd>
          </div>
          <div>
            <dt>Department</dt>
            <dd>{data.department || '—'}</dd>
          </div>
        </dl>
        <SlotsList doctors={data.doctors} />
      </div>
    );
  }

  return (
    <div className={`summary-card summary-card--${data.type}`}>
      <div className="summary-card-header">
        <span className="summary-card-icon" aria-hidden="true">✓</span>
        <h3>{title}</h3>
      </div>
      <dl className="summary-grid">
        <div>
          <dt>Doctor</dt>
          <dd>{data.doctor || '—'}</dd>
        </div>
        <div>
          <dt>Department</dt>
          <dd>{data.department || '—'}</dd>
        </div>
        <div>
          <dt>Date</dt>
          <dd>{data.date || '—'}</dd>
        </div>
        <div>
          <dt>Time</dt>
          <dd>{data.time || '—'}</dd>
        </div>
        <div>
          <dt>Appointment ID</dt>
          <dd>{data.appointment_id ?? '—'}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>
            <span className={`status-badge status-badge--${data.status || 'booked'}`}>
              {formatStatus(data.status)}
            </span>
          </dd>
        </div>
      </dl>
    </div>
  );
}
