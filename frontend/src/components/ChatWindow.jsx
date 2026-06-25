import { useEffect, useRef, useState } from 'react';
import { sendChat } from '../api/client';
import MessageBubble from './MessageBubble';

function createSessionId() {
  return crypto.randomUUID();
}

const WELCOME_MESSAGE = {
  role: 'bot',
  text: "Hello! I'm MediBook, your appointment assistant. I can help you book, check, cancel, or reschedule appointments. How can I help you today?",
  structuredData: null,
};

export default function ChatWindow({ patient, onLogout }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(createSessionId);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', text, structuredData: null }]);
    setLoading(true);

    try {
      const data = await sendChat(patient.patientId, sessionId, text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: data.reply,
          structuredData: data.structured_data,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: err.message || 'Something went wrong. Please try again.',
          structuredData: { type: 'error', error: err.message },
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div className="chat-header-brand">
          <div className="brand-icon brand-icon--sm" aria-hidden="true">+</div>
          <div>
            <h1>MediBook</h1>
            <p>Signed in as {patient.name}</p>
          </div>
        </div>
        <button type="button" className="btn-ghost" onClick={onLogout}>
          Sign out
        </button>
      </header>

      <main className="chat-main">
        <div className="messages" role="log" aria-live="polite" aria-label="Chat messages">
          {messages.map((msg, index) => (
            <MessageBubble
              key={`${index}-${msg.text.slice(0, 20)}`}
              role={msg.role}
              text={msg.text}
              structuredData={msg.structuredData}
            />
          ))}
          {loading && (
            <div className="message-row message-row--bot">
              <div className="avatar avatar--bot" aria-hidden="true">M</div>
              <div className="bubble bubble--bot bubble--typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-bar" onSubmit={handleSend}>
          <input
            type="text"
            placeholder="Type your message… e.g. Book a cardiologist for Friday"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            aria-label="Message"
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
