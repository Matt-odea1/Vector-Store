# C9 Oral Assessment Frontend

AI-powered oral coding assessment system for educators and students.

## Overview

The Oral Assessment System enables instructors to:
- Create and manage coding assessments
- Bulk upload student code submissions
- Automatically generate personalized oral questions using AI
- Monitor student progress in real-time
- Evaluate responses with AI-powered grading

Students can:
- Take oral assessments with audio recording
- Answer questions one at a time
- Track their progress
- View detailed results and feedback

## Tech Stack

- **React 19** with TypeScript
- **Vite 7** - Build tool and dev server
- **React Router** - Client-side routing
- **Zustand** - State management
- **Tailwind CSS** - Styling with dark theme
- **Axios** - HTTP client
- **MediaRecorder API** - Audio recording
- **AWS S3** - Audio file storage (via backend)

## Getting Started

### Prerequisites

- Node.js 20.19+ or 22.12+
- npm or yarn
- Backend server running (FastAPI on port 8000)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Update .env with your backend URL
# VITE_API_BASE_URL=http://localhost:8000
```

### Development

```bash
# Start dev server (runs on port 5174)
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint
npm run lint:fix

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── instructor/    # Instructor-specific components
│   ├── student/       # Student-specific components
│   └── shared/        # Reusable UI components
├── pages/
│   ├── instructor/    # Instructor dashboard pages
│   ├── student/       # Student assessment pages
│   └── NotFound.tsx
├── services/
│   ├── api.ts        # Backend API client
│   ├── audio.ts      # Audio recording service
│   └── s3.ts         # S3 upload service
├── store/            # Zustand state stores
├── types/            # TypeScript type definitions
└── utils/            # Utility functions
```

## Features

### Instructor Features
- Create assessments with custom parameters
- Bulk CSV upload of students and code
- Batch AI question generation
- Real-time progress monitoring
- Batch evaluation with AI
- Results dashboard with analytics

### Student Features
- Audio recording with pause/resume
- One question at a time delivery
- Progress tracking
- Auto-save and recovery
- Results and feedback view
- Audio playback of responses

## Environment Variables

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags (optional)
VITE_ENABLE_AUDIO_RECORDING=true
VITE_MAX_RECORDING_DURATION=300
VITE_MAX_FILE_SIZE_MB=50
```

## Browser Support

- Chrome/Edge 85+ (recommended)
- Firefox 88+
- Safari 14.1+

**Note**: Audio recording requires HTTPS in production (localhost works with HTTP).

## Design System

### Colors
- **Primary**: Indigo (#6366f1, #4f46e5)
- **Background**: Dark slate (#0f172a, #1e293b)
- **Success**: Green (#10b981)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)

### Typography
- **Font Family**: Inter (headings & body), Fira Code (code)
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

## API Integration

The frontend communicates with the FastAPI backend for:
- Assessment CRUD operations
- Student data management
- Question generation (AI)
- Audio transcription (Deepgram)
- Response evaluation (AI)
- S3 pre-signed URLs

See `src/services/api.ts` for complete API client.

## Development Roadmap

### Milestone 1: Project Foundation ✅
- [x] Vite project setup
- [x] Tailwind CSS configuration
- [x] Routing structure
- [x] API service layer
- [x] Audio recording service

### Milestone 2: Instructor Dashboard - Setup
- [ ] Assessment creation form
- [ ] CSV bulk upload
- [ ] Question generation UI
- [ ] Progress monitoring

### Milestone 3: Student Assessment Interface
- [ ] Question display
- [ ] Audio recorder component
- [ ] Progress tracking
- [ ] S3 upload integration

### Milestone 4: Monitoring & Evaluation
- [ ] Real-time progress dashboard
- [ ] Batch evaluation
- [ ] Results visualization

### Milestone 5: Student Results View
- [ ] Score display
- [ ] Feedback presentation
- [ ] Audio playback

### Milestone 6: Polish & Production
- [ ] Error handling
- [ ] Loading states
- [ ] Performance optimization
- [ ] Documentation

## License

Proprietary - All rights reserved
