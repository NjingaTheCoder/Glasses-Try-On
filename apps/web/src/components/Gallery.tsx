import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/client'
import GenerationStatus from './GenerationStatus'

export default function Gallery() {
  const { data: generationsData, refetch } = useQuery({
    queryKey: ['generations'],
    queryFn: () => apiClient.getGenerations(),
    refetchInterval: (query) => {
      // Refetch every 5 seconds if there are pending/processing generations
      const hasActive = query.state.data?.results.some(
        (gen) => gen.status === 'QUEUED' || gen.status === 'PROCESSING'
      )
      return hasActive ? 5000 : false
    },
  })

  if (!generationsData?.results.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        No try-on results yet. Generate your first try-on above!
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {generationsData.results.map((generation) => (
        <div key={generation.id} className="card">
          <div className="mb-3">
            <GenerationStatus generation={generation} />
          </div>

          {generation.status === 'SUCCEEDED' && generation.output_url ? (
            <img
              src={generation.output_url}
              alt={`Try-on result for ${generation.product_title}`}
              className="w-full h-64 object-cover rounded-lg mb-3"
            />
          ) : generation.status === 'PROCESSING' ? (
            <div className="w-full h-64 bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-3"></div>
                <p className="text-gray-600">Generating...</p>
              </div>
            </div>
          ) : generation.status === 'QUEUED' ? (
            <div className="w-full h-64 bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
              <p className="text-gray-600">Queued for processing...</p>
            </div>
          ) : (
            <div className="w-full h-64 bg-red-50 rounded-lg mb-3 flex items-center justify-center">
              <div className="text-center p-4">
                <p className="text-red-600 font-semibold mb-2">Generation Failed</p>
                {generation.error_message && (
                  <p className="text-sm text-gray-600">{generation.error_message}</p>
                )}
              </div>
            </div>
          )}

          <h3 className="font-bold mb-1">{generation.product_title}</h3>
          <p className="text-sm text-gray-500">
            {new Date(generation.created_at).toLocaleDateString()}
          </p>

          {generation.processing_time_seconds && (
            <p className="text-xs text-gray-400 mt-1">
              Processing time: {generation.processing_time_seconds.toFixed(1)}s
            </p>
          )}
        </div>
      ))}
    </div>
  )
}
