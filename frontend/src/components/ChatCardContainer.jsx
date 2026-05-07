import React from 'react'

export default function ChatCardContainer({ message }) {
  const isUser = message.type === 'message'
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-bubble">{message.text}</div>
    </div>
  )
}
