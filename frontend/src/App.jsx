// React hooks for state management and DOM access
import { useRef, useState } from 'react'
import './App.css'
import ChatCardContainer from './components/ChatCardContainer'
import NavSide from './components/navSide'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

function App() {
  const [inputValue, setInputValue] = useState('')
  const [messages, setMessages] = useState([
    { id: 1, text: 'Welcome', type: 'assistant' },
  ])
  const [sending, setSending] = useState(false)
  const inputRef = useRef(null)

  function handleInputChange(event) {
    setInputValue(event.target.value)

    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`
    }
  }

  function addMessage(text, type) {
    setMessages((prev) => [
      ...prev,
      { id: Date.now() + Math.random(), text, type },
    ])
  }

  async function sendrequestHandler() {
    const text = inputValue.trim()
    if (!text || sending) return

    addMessage(text, 'message')
    setInputValue('')

    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }

    setSending(true)

    try {
      const res = await fetch(
        `${apiBaseUrl}/chat?question=${encodeURIComponent(text)}`,
      )

      if (!res.ok) {
        throw new Error(res.statusText || 'Network error')
      }

      const contentType = res.headers.get('content-type') ?? ''
      let responseText = ''

      if (contentType.includes('application/json')) {
        const payload = await res.json()
        responseText = typeof payload === 'string'
          ? payload
          : payload.response ?? payload.message ?? payload.answer ?? JSON.stringify(payload)
      } else {
        responseText = await res.text()
      }

      responseText = String(responseText).trim()

      if (responseText.startsWith('"') && responseText.endsWith('"')) {
        responseText = responseText.slice(1, -1)
      }

      if (responseText) {
        addMessage(responseText, 'assistant')
      }
    } catch (err) {
      addMessage(String(err), 'assistant')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="main-container">
      <NavSide />
      <main>
        <h1>Welcome</h1>

        <div className="chat-container">
          {messages.map((message) => (
            <ChatCardContainer key={message.id} message={message} />
          ))}
        </div>

        <div className="input-section">
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={handleInputChange}
            placeholder="Enter your message..."
            className="input-field"
            rows="1"
          />
          <button className="send-button" onClick={sendrequestHandler} disabled={sending}>
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </main>
    </div>
  )
}

export default App
