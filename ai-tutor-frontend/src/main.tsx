import { StrictMode, Suspense, lazy, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { HelmetProvider } from 'react-helmet-async'
import './index.css'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'
import { initErrorTracking } from './utils/errorTracking'
import { initAnalytics, trackPageView } from './utils/analytics'
import { initPerformanceTracking } from './utils/performance'

// Initialize monitoring services
initErrorTracking()
initAnalytics()
initPerformanceTracking()

// Lazy load routes for code splitting
const App = lazy(() => import('./App.tsx'))
const DataUsage = lazy(() => import('./pages/DataUsage.tsx'))

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen bg-gray-50">
    <div className="flex flex-col items-center space-y-4">
      <svg className="animate-spin h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
      <p className="text-gray-600 font-medium">Loading...</p>
    </div>
  </div>
)

// Analytics tracking wrapper
const AnalyticsWrapper = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation()

  useEffect(() => {
    trackPageView({
      path: location.pathname,
      title: document.title,
    })
  }, [location])

  return <>{children}</>
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HelmetProvider>
      <ErrorBoundary>
        <BrowserRouter>
          <AnalyticsWrapper>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<App />} />
                <Route path="/data-usage" element={<DataUsage />} />
              </Routes>
            </Suspense>
          </AnalyticsWrapper>
        </BrowserRouter>
      </ErrorBoundary>
    </HelmetProvider>
  </StrictMode>,
)
