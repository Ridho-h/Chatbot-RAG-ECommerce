/**
 * Chat input with auto-expanding textarea and send button.
 */
import { useState, useRef, useEffect } from 'react';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [text]);

  const handleSubmit = () => {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about products, prices, reviews..."
          rows={1}
          disabled={disabled}
        />
        <button
          className="send-btn"
          onClick={handleSubmit}
          disabled={disabled || !text.trim()}
          title="Send message"
        >
          ➤
        </button>
      </div>
      <p className="input-hint">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
