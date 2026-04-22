import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { PageSpinner } from '@/components/ui/PageSpinner'
import { ProtectedRoute } from '@/components/ProtectedRoute'

const CatalogPage = lazy(() => import('@/pages/CatalogPage'))
const ProductDetailPage = lazy(() => import('@/pages/ProductDetailPage'))
const TryOnPage = lazy(() => import('@/pages/TryOnPage'))
const AdminLoginPage = lazy(() => import('@/pages/admin/AdminLoginPage'))
const AdminDashboardPage = lazy(() => import('@/pages/admin/AdminDashboardPage'))
const AdminNewProductPage = lazy(() => import('@/pages/admin/AdminNewProductPage'))
const AdminEditProductPage = lazy(() => import('@/pages/admin/AdminEditProductPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

export default function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageSpinner />}>
        <Routes>
          <Route path="/" element={<CatalogPage />} />
          <Route path="/product/:id" element={<ProductDetailPage />} />
          <Route path="/try-on" element={<TryOnPage />} />
          <Route path="/try-on/:productId" element={<TryOnPage />} />

          <Route path="/admin/login" element={<AdminLoginPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/products/new"
            element={
              <ProtectedRoute>
                <AdminNewProductPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/products/:id/edit"
            element={
              <ProtectedRoute>
                <AdminEditProductPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}
