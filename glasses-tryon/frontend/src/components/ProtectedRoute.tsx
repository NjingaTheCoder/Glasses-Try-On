import { type ReactNode, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { PageSpinner } from '@/components/ui/PageSpinner'

interface Props {
  children: ReactNode
}

export function ProtectedRoute({ children }: Props) {
  const { user, loading, init } = useAuthStore()

  // Subscribe to Firebase auth state exactly once per mount
  useEffect(() => {
    const unsubscribe = init()
    return unsubscribe
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (loading) return <PageSpinner />
  if (!user) return <Navigate to="/admin/login" replace />
  return <>{children}</>
}
