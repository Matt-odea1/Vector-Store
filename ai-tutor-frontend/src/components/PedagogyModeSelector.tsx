/**
 * Pedagogy mode selector component - Compact design
 */
import { useChatStore } from '../store/chatStore'
import { PEDAGOGY_MODES } from '../types/pedagogy'
import type { PedagogyMode } from '../types/pedagogy'

export const PedagogyModeSelector = () => {
  const { pedagogyMode, setPedagogyMode } = useChatStore()

  return (
    <div className="px-4 py-2 border-b border-gray-200 bg-white">
      <div className="max-w-4xl mx-auto flex items-center space-x-3">
        <label htmlFor="pedagogy-mode" className="text-xs font-medium text-gray-600 whitespace-nowrap">
          Mode:
        </label>
        <div className="relative">
          <select
            id="pedagogy-mode"
            value={pedagogyMode}
            onChange={(e) => setPedagogyMode(e.target.value as PedagogyMode)}
            className="appearance-none rounded-lg border border-gray-300 bg-white px-3 py-1.5 pr-8 text-sm font-medium text-gray-900 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500/20 cursor-pointer hover:border-gray-400 transition-all"
          >
            {PEDAGOGY_MODES.map((mode) => (
              <option key={mode.id} value={mode.id}>
                {mode.icon} {mode.name}
              </option>
            ))}
          </select>
          {/* Custom dropdown icon */}
          <div className="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}
