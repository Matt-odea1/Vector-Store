import { Link } from 'react-router-dom';
import CreateAssessmentForm from '../components/CreateAssessmentForm';

export default function CreateAssessment() {
  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <Link to="/assessments" className="text-slate-400 hover:text-slate-300">
              ← Back
            </Link>
            <h1 className="text-2xl font-bold text-slate-100">
              Create New Assessment
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 p-8">
          <CreateAssessmentForm />
        </div>
      </main>
    </div>
  );
}
