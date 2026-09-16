/**
 * Animated thinking/loading indicator with bouncing dots.
 */
export default function ThinkingIndicator() {
  return (
    <div className="message bot" style={{ alignSelf: 'flex-start' }}>
      <div className="message-avatar">AI</div>
      <div className="thinking-indicator">
        <div className="thinking-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <span className="thinking-text">Thinking...</span>
      </div>
    </div>
  );
}
