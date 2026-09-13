export type MessageRole = 'user' | 'bot'

export interface Message {
  id: string
  role: MessageRole
  content: string
  sources?: string[]
  weatherContext?: string | null
  isError?: boolean
}
