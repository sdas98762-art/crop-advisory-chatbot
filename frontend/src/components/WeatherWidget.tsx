import { useEffect, useState } from 'react'
import { getWeather, type WeatherResponse } from '../api/chatApi'

interface Props {
  location: string
}

export default function WeatherWidget({ location }: Props) {
  const [weather, setWeather] = useState<WeatherResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!location.trim()) {
      setWeather(null)
      return
    }
    setLoading(true)
    setError(null)
    getWeather(location)
      .then(setWeather)
      .catch(() => setError('Could not fetch weather.'))
      .finally(() => setLoading(false))
  }, [location])

  if (!location.trim()) return null

  return (
    <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 mb-4 shadow-sm flex items-center gap-4">
      <div className="text-3xl">🌤️</div>
      <div className="flex-1">
        {loading && <p className="text-sm text-gray-400">Fetching weather for {location}…</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
        {weather && !loading && (
          <div>
            <p className="text-sm font-semibold text-gray-700">
              {weather.location} — {weather.temperature}°C, {weather.condition}
            </p>
            <p className="text-xs text-gray-500">
              Humidity: {weather.humidity}% · {weather.forecast_summary}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
