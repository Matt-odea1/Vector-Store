export default function InstructorDashboard() {
  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-slate-100">
            Oral Assessment - Instructor Dashboard
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 p-8">
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Welcome to the Oral Assessment System
          </h2>
          <p className="text-slate-300">
            This is the instructor dashboard. Features coming soon:
          </p>
          <ul className="list-disc list-inside mt-4 space-y-2 text-slate-300">
            <li>Create new assessments</li>
            <li>Bulk upload students and code</li>
            <li>Generate questions automatically</li>
            <li>Monitor student progress</li>
            <li>View and evaluate results</li>
          </ul>
        </div>
      </main>
    </div>
  );
}
