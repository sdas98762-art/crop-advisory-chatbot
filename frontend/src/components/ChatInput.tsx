import { useRef, useState, type KeyboardEvent, type ChangeEvent } from 'react'

interface Props {
  onSend: (message: string, image?: File) => void
  location: string
  onLocationChange: (loc: string) => void
  disabled: boolean
}

const MAX_IMAGE_SIZE = 5 * 1024 * 1024 // 5 MB

export default function ChatInput({ onSend, location, onLocationChange, disabled }: Props) {
  const [text, setText] = useState('')
  const [image, setImage] = useState<File | null>(null)
  const [showLocation, setShowLocation] = useState(false)
  const [imageError, setImageError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  function handleSend() {
    const trimmed = text.trim()
    if (!trimmed && !image) return
    onSend(trimmed, image ?? undefined)
    setText('')
    setImage(null)
    setImageError(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setImageError('Only image files are supported.')
      return
    }
    if (file.size > MAX_IMAGE_SIZE) {
      setImageError('Image must be under 5 MB.')
      return
    }
    setImageError(null)
    setImage(file)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-3">
      {/* Location toggle */}
      <div className="flex items-center gap-2 mb-2">
        <button
          type="button"
          onClick={() => setShowLocation((v) => !v)}
          className="text-xs text-crop-600 hover:text-crop-800 underline"
        >
          {showLocation ? 'Hide location' : '📍 Add location for weather-aware advice'}
        </button>
        {location && (
          <span className="text-xs bg-crop-100 text-crop-700 rounded-full px-2 py-0.5">
            {location}
          </span>
        )}
      </div>

      {showLocation && (
        <input
          type="text"
          value={location}
          onChange={(e) => onLocationChange(e.target.value)}
          placeholder="Enter city name (e.g. Pune, Delhi)"
          className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 mb-2 focus:outline-none focus:ring-2 focus:ring-crop-400"
        />
      )}

      {/* Image preview */}
      {image && (
        <div className="flex items-center gap-2 mb-2 text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
          <span>📷 {image.name}</span>
          <button
            type="button"
            onClick={() => { setImage(null); if (fileRef.current) fileRef.current.value = '' }}
            className="ml-auto text-red-400 hover:text-red-600"
          >
            ✕ Remove
          </button>
        </div>
      )}
      {imageError && <p className="text-xs text-red-500 mb-1">{imageError}</p>}

      {/* Text input + actions */}
      <div className="flex items-end gap-2">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={image ? 'Describe the crop (optional) and press Enter…' : 'Ask about crops, diseases, fertilizers, irrigation…'}
          rows={2}
          disabled={disabled}
          className="flex-1 resize-none text-sm border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-crop-400 disabled:opacity-50"
        />

        {/* Image upload button */}
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          title="Upload leaf photo for disease diagnosis"
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-amber-50 hover:bg-amber-100 border border-amber-200 flex items-center justify-center text-lg"
        >
          📷
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={disabled || (!text.trim() && !image)}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-crop-600 hover:bg-crop-700 disabled:opacity-40 flex items-center justify-center text-white text-lg"
        >
          ➤
        </button>
      </div>
      <p className="text-xs text-gray-400 mt-1">Press Enter to send · Shift+Enter for new line</p>
    </div>
  )
}
