import { useParams } from 'react-router-dom';

export default function StudentAssessment() {
  const { studentId, assessmentId } = useParams<{
    studentId: string;
    assessmentId: string;
  }>();

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-slate-100">
            Oral Assessment
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Student ID: {studentId} | Assessment ID: {assessmentId}
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 p-8">
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Welcome to Your Oral Assessment
          </h2>
          <p className="text-slate-300">
            This is the student assessment interface. Features coming soon:
          </p>
          <ul className="list-disc list-inside mt-4 space-y-2 text-slate-300">
            <li>View questions one at a time</li>
            <li>Record audio responses</li>
            <li>Track progress</li>
            <li>Submit assessment</li>
            <li>View results and feedback</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
