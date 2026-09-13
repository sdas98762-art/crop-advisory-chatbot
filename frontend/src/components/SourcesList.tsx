interface Props {
  sources: string[]
}

export default function SourcesList({ sources }: Props) {
  if (sources.length === 0) return null

  return (
    <div className="flex flex-wrap gap-1 mt-1">
      <span className="text-xs text-gray-400 mr-1">Sources:</span>
      {sources.map((src, i) => (
        <span
          key={i}
          className="text-xs bg-crop-50 text-crop-700 border border-crop-200 rounded-full px-2 py-0.5"
        >
          {src}
        </span>
      ))}
    </div>
  )
}
