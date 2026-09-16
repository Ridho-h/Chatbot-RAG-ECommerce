import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * Individual message bubble with product source cards.
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className="message-avatar">
        {isUser ? '👤' : 'AI'}
      </div>

      <div>
        <div className={`message-content ${message.isError ? 'error-msg' : ''}`}>
          {isUser ? (
            message.content.split('\n').map((line, i) => (
              <p key={i}>{line || '\u00A0'}</p>
            ))
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Product source cards */}
        {message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <span className="sources-label">📦 Product Sources</span>
            {message.sources.map((source, i) => (
              <div className="source-card" key={i}>
                <div className="source-name">{source.product_name}</div>
                <div className="source-meta">
                  <span>💰 {source.discounted_price}</span>
                  <span>⭐ {source.rating}</span>
                  <span>📝 {source.rating_count} reviews</span>
                </div>
                {source.product_link && source.product_link !== 'N/A' && (
                  <a href={source.product_link} target="_blank" rel="noopener noreferrer">
                    View on Amazon →
                  </a>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Thinking time */}
        {!isUser && message.thinkingTime && (
          <div className="message-time">
            ⚡ {(message.thinkingTime / 1000).toFixed(1)}s
          </div>
        )}
      </div>
    </div>
  );
}
