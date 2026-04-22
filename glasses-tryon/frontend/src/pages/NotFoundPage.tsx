import { Link } from 'react-router-dom'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-brand-500 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">Page not found</p>
        <Link to="/" className="px-6 py-3 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors">
          Back to catalog
        </Link>
      </div>
    </div>
  )
}
