import BookingSummaryCard from './BookingSummaryCard';

const CARD_TYPES = new Set([
  'booking_confirmation',
  'cancellation_confirmation',
  'reschedule_confirmation',
  'available_slots',
]);

export default function MessageBubble({ role, text, structuredData }) {
  const isUser = role === 'user';
  const showCard = structuredData && CARD_TYPES.has(structuredData.type);

  return (
    <div className={`message-row ${isUser ? 'message-row--user' : 'message-row--bot'}`}>
      {!isUser && <div className="avatar avatar--bot" aria-hidden="true">M</div>}

      <div className="message-content">
        <div className={`bubble ${isUser ? 'bubble--user' : 'bubble--bot'}`}>
          <p>{text}</p>
        </div>
        {showCard && <BookingSummaryCard data={structuredData} />}
      </div>

      {isUser && <div className="avatar avatar--user" aria-hidden="true">You</div>}
    </div>
  );
}
