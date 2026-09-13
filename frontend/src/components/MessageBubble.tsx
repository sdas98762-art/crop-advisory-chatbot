import type { Message } from '../types/message'
import SourcesList from './SourcesList'

interface Props {
  message: Message
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar */}
        <div className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div
            className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold
              ${isUser ? 'bg-crop-600 text-white' : 'bg-amber-100 text-amber-700 border border-amber-300'}`}
          >
            {isUser ? 'You' : '🌾'}
          </div>

          {/* Bubble */}
          <div
            className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
              ${isUser
                ? 'bg-crop-600 text-white rounded-br-sm'
                : message.isError
                  ? 'bg-red-50 text-red-700 border border-red-200 rounded-bl-sm'
                  : 'bg-white text-gray-800 border border-gray-200 shadow-sm rounded-bl-sm'
              }`}
          >
            {message.content}
          </div>
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-1 ml-10">
            <SourcesList sources={message.sources} />
          </div>
        )}
      </div>
    </div>
  )
}
