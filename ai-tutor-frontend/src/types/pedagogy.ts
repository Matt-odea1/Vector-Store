/**
 * Type definitions for pedagogy modes
 */

export type PedagogyMode = 'socratic' | 'explanatory' | 'debugging' | 'assessment' | 'review'

export interface PedagogyModeInfo {
  id: PedagogyMode
  name: string
  description: string
  icon: string
  color: string
}

export const PEDAGOGY_MODES: PedagogyModeInfo[] = [
  {
    id: 'socratic',
    name: 'Socratic',
    description: 'Discovery through questioning - guides you to find answers',
    icon: '🤔',
    color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  },
  {
    id: 'explanatory',
    name: 'Explanatory',
    description: 'Direct instruction with clear explanations and examples',
    icon: '📖',
    color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  },
  {
    id: 'debugging',
    name: 'Debugging',
    description: 'Hint-based problem solving without giving away solutions',
    icon: '🐛',
    color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  },
  {
    id: 'assessment',
    name: 'Assessment',
    description: 'Tests understanding through questions and feedback',
    icon: '✅',
    color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  },
  {
    id: 'review',
    name: 'Review',
    description: 'Reinforces and consolidates previously learned material',
    icon: '📚',
    color: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
  },
]
