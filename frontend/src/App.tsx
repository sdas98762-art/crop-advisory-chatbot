import ChatWindow from './components/ChatWindow'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-crop-50">
      <header className="w-full bg-crop-700 text-white py-4 px-6 shadow-md">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <span className="text-2xl">🌾</span>
          <div>
            <h1 className="text-xl font-bold leading-tight">Crop Advisory Chatbot</h1>
            <p className="text-crop-200 text-sm">AI-powered farming advice — disease, weather, fertilizer & more</p>
          </div>
        </div>
      </header>
      <main className="w-full max-w-3xl flex-1 flex flex-col px-4 py-6">
        <ChatWindow />
      </main>
    </div>
  )
}
