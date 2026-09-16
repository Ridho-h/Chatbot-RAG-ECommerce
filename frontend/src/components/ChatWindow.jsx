/**
 * Main chat window with welcome screen, messages, and input.
 */
import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import ThinkingIndicator from './ThinkingIndicator';

const SUGGESTIONS = [
  { icon: '🔌', text: 'What is the fastest charger?' },
  { icon: '⚡', text: 'Show me durable Type-C braided cables' },
  { icon: '⌚', text: 'Are there any smartwatches under ₹2000?' },
  { icon: '🖱️', text: 'Best rated wireless mouse' },
];

export default function ChatWindow({ messages, isLoading, onSendMessage }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-window">
      {isEmpty ? (
        <div className="welcome-screen">
          <div className="welcome-icon">🛒</div>
          <h2>Welcome to ShopAI</h2>
          <p>
            I'm your AI shopping assistant. Ask me about products, prices,
            ratings, or anything else — I'll search our product database
            and the web to find the best answers for you.
          </p>
          <div className="suggestions">
            {SUGGESTIONS.map((suggestion, i) => (
              <button
                key={i}
                className="suggestion-card"
                onClick={() => onSendMessage(suggestion.text)}
              >
                <div className="suggestion-icon">{suggestion.icon}</div>
                {suggestion.text}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="messages-container">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isLoading && <ThinkingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      )}

      <ChatInput onSend={onSendMessage} disabled={isLoading} />
    </div>
  );
}
