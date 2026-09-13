import { useEffect, useRef, useState } from 'react'
import { sendMessage, diagnoseImage } from '../api/chatApi'
import type { Message } from '../types/message'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import WeatherWidget from './WeatherWidget'

function makeId() {
  return Math.random().toString(36).slice(2)
}

const WELCOME: Message = {
  id: 'welcome',
  role: 'bot',
  content:
    '👋 Hello! I\'m your Crop Advisory Assistant.\n\nI can help you with:\n• 🌱 Crop selection & season planning\n• 🦠 Disease diagnosis (describe symptoms or upload a leaf photo)\n• 🌦️ Weather-based farming advice\n• 💧 Fertilizer & irrigation recommendations\n\nHow can I help you today?',
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [loading, setLoading] = useState(false)
  const [location, setLocation] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend(text: string, image?: File) {
    // Add user message
    const userMsg: Message = {
      id: makeId(),
      role: 'user',
      content: image ? (text ? `${text}\n[📷 ${image.name}]` : `[📷 ${image.name}]`) : text,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      let botContent: string
      let sources: string[] = []

      if (image) {
        // Disease diagnosis via image
        const crop = text.trim() || 'unknown crop'
        const result = await diagnoseImage(image, crop)
        botContent =
          `**Disease Identified:** ${result.disease_name}\n\n` +
          `${result.description}\n\n` +
          `**Management Steps:**\n` +
          result.management_steps.map((s, i) => `${i + 1}. ${s}`).join('\n')
        sources = result.sources
      } else {
        // General advisory chat
        const result = await sendMessage(text, location || undefined)
        botContent = result.response
        sources = result.sources
      }

      const botMsg: Message = {
        id: makeId(),
        role: 'bot',
        content: botContent,
        sources,
      }
      setMessages((prev) => [...prev, botMsg])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: makeId(),
          role: 'bot',
          content: 'Sorry, I couldn\'t reach the advisory service. Please try again.',
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)]">
      {/* Weather widget */}
      <WeatherWidget location={location} />

      {/* Message list */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-1 mb-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex justify-start mb-3">
            <div className="flex items-end gap-2">
              <div className="w-8 h-8 rounded-full bg-amber-100 border border-amber-300 flex items-center justify-center text-sm">
                🌾
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1 items-center">
                  <span className="w-2 h-2 bg-crop-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-crop-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-crop-400 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        location={location}
        onLocationChange={setLocation}
        disabled={loading}
      />
    </div>
  )
}
