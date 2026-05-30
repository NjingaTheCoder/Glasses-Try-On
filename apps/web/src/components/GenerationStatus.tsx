import type { Generation } from '../types'

interface GenerationStatusProps {
  generation: Generation
}

export default function GenerationStatus({ generation }: GenerationStatusProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'QUEUED':
        return 'bg-gray-100 text-gray-800'
      case 'PROCESSING':
        return 'bg-yellow-100 text-yellow-800'
      case 'SUCCEEDED':
        return 'bg-green-100 text-green-800'
      case 'FAILED':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'QUEUED':
        return '⏳'
      case 'PROCESSING':
        return '⚙️'
      case 'SUCCEEDED':
        return '✅'
      case 'FAILED':
        return '❌'
      default:
        return '○'
    }
  }

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(generation.status)}`}>
      <span className="mr-1">{getStatusIcon(generation.status)}</span>
      <span>{generation.status}</span>
    </div>
  )
}
