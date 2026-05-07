// React hooks for state management, side effects, and DOM access
import { useEffect, useRef, useState } from 'react'
import './App.css'
import ChatCardContainer from './components/ChatCardContainer'
import NavSide from './components/navSide'

// API endpoint configuration: use VITE_API_BASE_URL environment variable if provided,
// otherwise default to localhost:8000 for local development
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

/**
 * App Component
 * 
 * Fetches the backend root endpoint (GET /) and displays the returned model and evaluation data.
 * The backend returns JSON with structure: { model: {...}, evaluation: {...} }
 */
function App() {
  // State for storing fetched model and evaluation data
  const [model, setModel] = useState(null)
  const [evaluation, setEvaluation] = useState(null)
  // State for tracking loading and error states during fetch
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  // State for storing the input text value
  const [inputValue, setInputValue] = useState('')
  // Messages for chat display: type 'message' (user) or 'assistant'
  const [messages, setMessages] = useState([])
  const inputRef = useRef(null)

  /**
   * useEffect Hook: Runs once on component mount to fetch backend data
   * 
   * - Fetches the root endpoint (/) from the backend API
   * - Handles loading, success, and error states
   * - Parses evaluation data if it comes as a JSON string
   * - Uses 'mounted' flag to prevent state updates after unmount (memory leak prevention)
   */
  useEffect(() => {
    // Flag to track if component is still mounted (prevents state updates after unmount)
    let mounted = true

    async function fetchRoot() {
      setLoading(true)
      setError(null)
      try {
        // Fetch the backend root endpoint
        const res = await fetch(`${apiBaseUrl}/`)
        if (!res.ok) throw new Error(res.statusText || 'Network error')
        const payload = await res.json()

        // Only update state if component is still mounted
        if (!mounted) return

        // Extract and store model info
        setModel(payload.model ?? null)

        /**
         * Handle evaluation data
         * Backend may return evaluation as:
         *   - A JSON object (directly usable)
         *   - A JSON string (needs parsing)
         * Try to parse if it's a string; if parsing fails, keep the original string
         */
        let evalData = payload.evaluation ?? null
        if (typeof evalData === 'string') {
          try {
            evalData = JSON.parse(evalData)
          } catch {
            // If parsing fails, keep the original string for display
          }
        }

        setEvaluation(evalData)
      } catch (err) {
        if (!mounted) return
        // Store error message for display to user
        setError(String(err))
      } finally {
        if (mounted) setLoading(false)
      }
    }

    // Trigger the fetch on component mount
    fetchRoot()

    // Cleanup function: mark component as unmounted to prevent memory leaks
    return () => {
      mounted = false
    }
  }, []) // Empty dependency array: runs only once on mount

  function handleInputChange(event) {
    setInputValue(event.target.value)

    let inputTest = event.target.value
    console.log('Input value***************:', inputTest)

    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`
    }
  }

    function addAssistantMessage(text) {
      setMessages((prev) => [...prev, { id: Date.now() + Math.random(), text, type: 'assistant' }])
    }

    function sendrequestHandler() {
      const text = inputValue?.trim()
      if (!text) return
      // add user message
      setMessages((prev) => [...prev, { id: Date.now() + Math.random(), text, type: 'message' }])
      setInputValue('')

      // NOTE: when an assistant response is received from backend,
      // call addAssistantMessage(responseText) to append it.
      // For quick demonstration, append a placeholder assistant reply after a short delay.
      setTimeout(() => addAssistantMessage('Assistant response'), 700)
    }

  // Render the UI
  return (
    <div className="main-container">
      <NavSide />
      <main>
        <h1>Data Analyst Agent</h1>

        {/* Conditional rendering based on loading/error/success states */}
        {loading ? (
          // Show loading message while fetching
          <p className="muted">Loading…</p>
        ) : error ? (
          // Show error message if fetch failed
          <div className="error">Error: {error}</div>
        ) : (
          // Display model and evaluation data if fetch succeeded
          <>
            <div className="result">
              {/* Display Model Information */}
              <div className="row">
                <div className="label">Model</div>
                <div className="value">
                  {model ? (
                    <>
                      {/* Show model provider and name */}
                      <div className="model-line">{model.provider} / {model.name}</div>
                      {/* Show version if available */}
                      {model.version ? <div className="model-sub">Version: {model.version}</div> : null}
                    </>
                  ) : (
                    <span className="muted">No model info returned</span>
                  )}
                </div>
              </div>

              {/* Display Evaluation Information */}
              <div className="row">
                <div className="label">Evaluation</div>
                <div className="value">
                  {evaluation ? (
                    // If evaluation is an object, display as formatted JSON; otherwise show as text
                    typeof evaluation === 'object' ? (
                      <pre className="eval-json">{JSON.stringify(evaluation, null, 2)}</pre>
                    ) : (
                      <div>{String(evaluation)}</div>
                    )
                  ) : (
                    <span className="muted">No evaluation returned</span>
                  )}
                </div>
              </div>
            </div>

            {/* Input field and button */}
            <div className="chat-container">
              {messages.length === 0 ? (
                <div className="muted">No messages yet</div>
              ) : (
                messages.map((m) => <ChatCardContainer key={m.id} message={m} />)
              )}
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
              <button className="send-button" onClick={sendrequestHandler}>Send</button>
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default App
