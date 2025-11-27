import { useParams } from 'react-router-dom';
import { useEffect } from 'react';
import { useAssessmentStore } from '../store/assessmentStore';
import ResultsCard from '../components/ResultsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  getGradeFromPercentage,
  getGradeColor,
  formatTimestamp,
} from '../utils/helpers';

export default function ViewResults() {
  const { studentId: urlStudentId, assessmentId: urlAssessmentId } = useParams<{
    studentId: string;
    assessmentId: string;
  }>();

  const {
    studentId,
    assessmentId,
    results,
    isResultsReady,
    isLoading,
    error,
    setStudentInfo,
    loadResults,
    clearError,
  } = useAssessmentStore();

  // Initialize and load results
  useEffect(() => {
    if (urlStudentId && urlAssessmentId) {
      setStudentInfo(urlStudentId, urlAssessmentId);
    }
  }, [urlStudentId, urlAssessmentId, setStudentInfo]);

  useEffect(() => {
    if (studentId && assessmentId && !isResultsReady) {
      loadResults();
    }
  }, [studentId, assessmentId, isResultsReady, loadResults]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="lg" message="Loading results..." />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <ErrorMessage error={error} onDismiss={clearError} />
          {error.message?.includes('not ready') && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                Your assessment is being evaluated. This usually takes a few minutes.
                Please check back soon!
              </p>
            </div>
          )}
          <button
            onClick={() => loadResults()}
            className="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No results state
  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No Results Available
          </h2>
          <p className="text-gray-600 mb-4">
            Results for this assessment are not available yet.
          </p>
          <button
            onClick={() => loadResults()}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
          >
            Check Again
          </button>
        </div>
      </div>
    );
  }

  const grade = getGradeFromPercentage(results.percentage);
  const gradeColorClass = getGradeColor(grade);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Assessment Results
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Student: {studentId} | Assessment: {assessmentId?.slice(0, 8)}...
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Score Card */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="text-center">
            <div className="mb-4">
              <div className="text-6xl font-bold text-gray-900 mb-2">
                {results.percentage}%
              </div>
              <div className={`inline-block px-6 py-2 rounded-full text-2xl font-semibold ${gradeColorClass}`}>
                Grade: {grade}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6 mt-6 pt-6 border-t">
              <div>
                <div className="text-3xl font-bold text-blue-600">
                  {results.totalScore}
                </div>
                <div className="text-sm text-gray-600">Total Score</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-purple-600">
                  {results.maxScore}
                </div>
                <div className="text-sm text-gray-600">Max Score</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-green-600">
                  {results.questions.length}
                </div>
                <div className="text-sm text-gray-600">Questions</div>
              </div>
            </div>

            {results.completedAt && (
              <div className="mt-4 text-sm text-gray-500">
                Completed: {formatTimestamp(results.completedAt)}
              </div>
            )}
          </div>
        </div>

        {/* Question Results */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Question Details
          </h2>
          <div className="space-y-4">
            {results.questions.map((questionResult) => (
              <ResultsCard
                key={questionResult.questionId}
                result={questionResult}
              />
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            What's Next?
          </h3>
          <p className="text-blue-800">
            Review the feedback for each question to understand your strengths and areas for improvement.
            Focus on the suggested improvements to enhance your understanding.
          </p>
        </div>
      </main>
    </div>
  );
}
