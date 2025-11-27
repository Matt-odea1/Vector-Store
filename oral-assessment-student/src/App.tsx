import { BrowserRouter, Routes, Route } from 'react-router-dom';
import TakeAssessment from './pages/TakeAssessment';
import ViewResults from './pages/ViewResults';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Assessment taking - URL format: /:studentId/:assessmentId */}
        <Route path="/:studentId/:assessmentId" element={<TakeAssessment />} />

        {/* Results viewing - URL format: /:studentId/results/:assessmentId */}
        <Route path="/:studentId/results/:assessmentId" element={<ViewResults />} />

        {/* Default/Home page */}
        <Route path="*" element={
          <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="bg-white rounded-lg shadow-md p-12 max-w-md text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Oral Assessment Platform
              </h1>
              <p className="text-gray-600 mb-6">
                Please use the assessment link provided by your instructor to begin.
              </p>
              <div className="text-sm text-gray-500 space-y-2">
                <p>URL format:</p>
                <code className="bg-gray-100 px-3 py-1 rounded">
                  /:studentId/:assessmentId
                </code>
              </div>
            </div>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
