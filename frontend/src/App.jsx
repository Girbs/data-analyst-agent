import { useMemo, useState } from 'react'
import './App.css'

const initialChats = [
  {
    id: 'chat-1',
    title: 'Sales funnel review',
    createdAt: 'Today',
    messages: [
      {
        id: 'msg-1',
        role: 'assistant',
        content:
          'I can help analyze the funnel, summarize trends, and flag anything unusual in the numbers.',
        time: '09:12',
      },
      {
        id: 'msg-2',
        role: 'user',
        content: 'Compare this week with last week and highlight the biggest drop-offs.',
        time: '09:14',
      },
      {
        id: 'msg-3',
        role: 'assistant',
        content:
          'I will pull the stage-by-stage conversion rates, identify the largest leakage points, and keep the summary concise.',
        time: '09:14',
      },
    ],
  },
  {
    id: 'chat-2',
    title: 'Customer segment summary',
    createdAt: 'Yesterday',
    messages: [
      {
        id: 'msg-4',
        role: 'assistant',
        content:
          'Share the CSV or API payload and I will turn it into a segment-level summary with clear action items.',
        time: 'Yesterday',
      },
    ],
  },
  {
    id: 'chat-3',
    title: 'Q1 dashboard notes',
    createdAt: 'Mon',
    messages: [
      {
        id: 'msg-5',
        role: 'user',
        content: 'Summarize the dashboard into a short executive update.',
        time: 'Mon',
      },
      {
        id: 'msg-6',
        role: 'assistant',
        content:
          'Revenue was stable, traffic improved slightly, and the main risk is the slower conversion in the trial cohort.',
        time: 'Mon',
      },
    ],
  },
]

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function buildTitle(text) {
  const words = text.trim().split(/\s+/).slice(0, 4)
  return words.length ? words.join(' ') : 'New chat'
}

function formatTime(date = new Date()) {
  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })
}

function createId() {
  return crypto.randomUUID()
}

function fallbackReply(message) {
  return [
    'I could not reach the API, so I used a local fallback response.',
    `You said: “${message}”`,
    'Connect your Python service to replace this placeholder with model output.',
  ].join(' ')
}

function App() {
  const [chats, setChats] = useState(initialChats)
  const [activeChatId, setActiveChatId] = useState(initialChats[0].id)
  const [draft, setDraft] = useState('')
  const [isSending, setIsSending] = useState(false)

  const activeChat = useMemo(
    () => chats.find((chat) => chat.id === activeChatId) ?? chats[0],
    [activeChatId, chats],
  )

  async function handleSend(event) {
    event.preventDefault()

    const text = draft.trim()
    if (!text || isSending || !activeChat) {
      return
    }

    const userMessage = {
      id: createId(),
      role: 'user',
      content: text,
      time: formatTime(),
    }

    const chatId = activeChat.id
    const nextMessages = [...activeChat.messages, userMessage]
    const nextTitle =
      activeChat.messages.length === 0 ? buildTitle(text) : activeChat.title

    setDraft('')
    setIsSending(true)

    setChats((currentChats) =>
      currentChats.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              title: nextTitle,
              messages: nextMessages,
            }
          : chat,
      ),
    )

    try {
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chatId,
          message: text,
          messages: nextMessages.map(({ role, content }) => ({ role, content })),
        }),
      })

      const payload = await response.json()
      const assistantText =
        payload.reply ?? payload.message ?? payload.response ?? fallbackReply(text)

      const assistantMessage = {
        id: createId(),
        role: 'assistant',
        content: assistantText,
        time: formatTime(),
      }

      setChats((currentChats) =>
        currentChats.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                messages: [...chat.messages, assistantMessage],
              }
            : chat,
        ),
      )
    } catch {
      const assistantMessage = {
        id: createId(),
        role: 'assistant',
        content: fallbackReply(text),
        time: formatTime(),
      }

      setChats((currentChats) =>
        currentChats.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                messages: [...chat.messages, assistantMessage],
              }
            : chat,
        ),
      )
    } finally {
      setIsSending(false)
    }
  }

  function startNewChat() {
    const newChat = {
      id: createId(),
      title: 'New chat',
      createdAt: 'Just now',
      messages: [],
    }

    setChats((currentChats) => [newChat, ...currentChats])
    setActiveChatId(newChat.id)
    setDraft('')
  }

  return (
    <div className="app-shell">
      <aside className="history-panel" aria-label="Chat history">
        <div className="history-header">
          <div>
            <p className="eyebrow">History</p>
            <h2>Chat history</h2>
          </div>
          <button className="new-chat-button" type="button" onClick={startNewChat}>
            New chat
          </button>
        </div>

        <div className="history-list">
          {chats.map((chat) => {
            const preview = chat.messages.at(-1)?.content ?? 'No messages yet'

            return (
              <button
                key={chat.id}
                type="button"
                className={`history-item ${
                  chat.id === activeChatId ? 'history-item-active' : ''
                }`}
                onClick={() => setActiveChatId(chat.id)}
              >
                <div>
                  <strong>{chat.title}</strong>
                  <p>{preview}</p>
                </div>
                <span>{chat.createdAt}</span>
              </button>
            )
          })}
        </div>
      </aside>

      <main className="chat-panel">
        <header className="chat-header">
          <div>
            <p className="eyebrow">AI Agent Chat</p>
            <h1>{activeChat?.title ?? 'New chat'}</h1>
            <p className="subtle">
              Front end for a Python REST API that streams analysis, summaries,
              and follow-up actions.
            </p>
          </div>

          <div className="status-card">
            <span className="status-dot" />
            <div>
              <strong>Connected target</strong>
              <p>{apiBaseUrl}</p>
            </div>
          </div>
        </header>

        <section className="conversation" aria-label="Chat conversation">
          {activeChat?.messages?.length ? (
            activeChat.messages.map((message) => (
              <article
                key={message.id}
                className={`message-row ${
                  message.role === 'user' ? 'message-row-user' : 'message-row-assistant'
                }`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? 'You' : 'AI'}
                </div>
                <div className="message-bubble">
                  <div className="message-meta">
                    <strong>{message.role === 'user' ? 'You' : 'Agent'}</strong>
                    <span>{message.time}</span>
                  </div>
                  <p>{message.content}</p>
                </div>
              </article>
            ))
          ) : (
            <div className="empty-state">
              <p className="eyebrow">Start here</p>
              <h2>Ask the agent to analyze data, draft insights, or explain trends.</h2>
              <p>
                The composer below sends messages to your Python API and falls back
                gracefully if the endpoint is unavailable.
              </p>
            </div>
          )}
        </section>

        <form className="composer" onSubmit={handleSend}>
          <label className="composer-label" htmlFor="chat-input">
            Message the agent
          </label>
          <div className="composer-field">
            <textarea
              id="chat-input"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Ask for a data summary, comparison, recommendation, or next step..."
              rows="3"
            />
            <button type="submit" disabled={!draft.trim() || isSending}>
              {isSending ? 'Sending...' : 'Send'}
            </button>
          </div>
          <p className="composer-note">
            POST {apiBaseUrl}/chat with {`{ message, chatId, messages }`}.
          </p>
        </form>
      </main>
    </div>
  )
}

export default App
