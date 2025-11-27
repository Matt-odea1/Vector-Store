interface CodeEditorHeaderProps {
  onClose: () => void;
}

export const CodeEditorHeader = ({ onClose }: CodeEditorHeaderProps) => {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50">
      <div className="flex items-center space-x-2">
        <h3 className="text-sm font-semibold text-gray-900">Python Editor</h3>
      </div>
      <button
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 transition-colors p-1.5 rounded hover:bg-white"
        aria-label="Close editor"
        title="Close editor"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};
