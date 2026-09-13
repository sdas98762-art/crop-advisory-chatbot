// Typed API client for the Crop Advisory Chatbot backend

export interface ChatResponse {
  response: string
  sources: string[]
  weather_context: string | null
}

export interface DiagnoseTextRequest {
  crop: string
  symptoms: string
}

export interface DiagnoseResponse {
  disease_name: string
  description: string
  management_steps: string[]
  sources: string[]
}

export interface WeatherResponse {
  location: string
  temperature: number
  condition: string
  humidity: number
  forecast_summary: string
}

const BASE = '/api'

export async function sendMessage(
  message: string,
  location?: string,
  sessionId?: string,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, location: location ?? null, session_id: sessionId ?? null }),
  })
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`)
  return res.json()
}

export async function diagnoseImage(
  image: File,
  crop: string,
): Promise<DiagnoseResponse> {
  const form = new FormData()
  form.append('image', image)
  form.append('crop', crop)
  const res = await fetch(`${BASE}/diagnose/image`, {
    method: 'POST',
    body: form,
  })
  if (!res.ok) throw new Error(`Diagnose API error: ${res.status}`)
  return res.json()
}

export async function diagnoseText(
  crop: string,
  symptoms: string,
): Promise<DiagnoseResponse> {
  const res = await fetch(`${BASE}/diagnose/text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crop, symptoms }),
  })
  if (!res.ok) throw new Error(`Diagnose text API error: ${res.status}`)
  return res.json()
}

export async function getWeather(location: string): Promise<WeatherResponse> {
  const res = await fetch(`${BASE}/weather?location=${encodeURIComponent(location)}`)
  if (!res.ok) throw new Error(`Weather API error: ${res.status}`)
  return res.json()
}
