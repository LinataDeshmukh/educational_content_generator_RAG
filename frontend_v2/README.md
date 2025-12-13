# Learnify - Frontend v2

Modern Next.js React frontend for the RAG Educational Content Generator.

## Features

- **Upload PDF** - Upload and index PDF documents (up to 300 pages)
- **Chat** - Ask questions about your material using RAG-powered responses
- **Quiz** - Generate multiple choice and short answer quizzes with:
  - Detailed statistical analysis
  - Visual performance charts
  - Breakdown by question type
  - Answer history visualization
- **Competitive Quiz** - Adaptive quiz (30 questions) with:
  - Q-Learning difficulty adjustment
  - Real-time statistics with progress bars
  - Comprehensive final analytics
  - Difficulty distribution analysis
- **Summary** - Generate comprehensive document summaries (short, medium, long)
- **Flashcards** - Create and study flashcards
- **Light/Dark Mode** - Toggle between themes
- **Collapsible Sidebar** - Clean navigation experience
- **Document Names** - Display actual filenames throughout the app

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend server running on http://localhost:8000

### Installation

```bash
cd frontend_v2
npm install
```

### Configuration

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - Lightweight state management
- **Lucide React** - Icon library

## Project Structure

```
frontend_v2/
├── app/                      # Next.js App Router pages
│   ├── layout.tsx           # Root layout with sidebar and theme
│   ├── page.tsx             # Home page
│   ├── upload/              # PDF upload page
│   ├── chat/                # Chat with document
│   ├── quiz/                # Quiz generation with statistics
│   ├── competitive-quiz/    # Adaptive quiz with analytics
│   ├── summary/             # Summary generation
│   ├── flashcards/          # Flashcard generation
│   └── globals.css          # Global styles and theme variables
├── components/              # Shared React components
│   ├── Sidebar.tsx          # Collapsible navigation sidebar
│   ├── Header.tsx           # Top header with document name
│   └── ThemeProvider.tsx    # Light/dark mode provider
├── lib/                     # Utilities
│   ├── api.ts              # API client for backend communication
│   └── store.ts            # Zustand state management
└── public/                 # Static assets
```

## Key Features

### Statistical Analysis

**Quiz Statistics:**
- Overall performance metrics with progress bars
- Visual bar charts showing correct/incorrect/unanswered breakdown
- Question type breakdown (Multiple Choice vs Short Answer)
- Answer history with visual grid representation
- Detailed performance analytics

**Competitive Quiz Analytics:**
- Real-time statistics during quiz
- Final comprehensive statistics
- Difficulty distribution (Low/Medium/Hard)
- Reward tracking
- Performance trends
- Visual answer history grid

### UI/UX

- **Minimal Design** - Clean, educational theme
- **Light/Dark Mode** - Toggle between themes
- **Collapsible Sidebar** - Space-efficient navigation
- **Responsive** - Works on all screen sizes
- **Visual Feedback** - Progress bars, charts, and indicators
- **Document Names** - Actual filenames displayed throughout

## State Management

The app uses Zustand for global state management:

- Document ID and filename
- Quiz data and answers
- Chat messages
- Backend connection status
- Theme preference
- Sidebar state

## API Integration

The frontend communicates with the FastAPI backend through the `lib/api.ts` client:

- Health checks
- PDF upload
- Document listing
- Chat queries
- Quiz generation and evaluation
- Competitive quiz management
- Summary and flashcard generation

## Development

### Adding a New Page

1. Create a new file in `app/` directory (e.g., `app/new-page/page.tsx`)
2. Add route to sidebar in `components/Sidebar.tsx`
3. Update store if needed in `lib/store.ts`

### Styling

The app uses Tailwind CSS with custom theme variables defined in `app/globals.css`:
- Light/dark mode colors
- Accent colors
- Card and border styles

### State Management

Add new state to `lib/store.ts`:
```typescript
const useStore = create((set) => ({
  // existing state
  newState: null,
  setNewState: (value) => set({ newState: value }),
}))
```

## Troubleshooting

### Backend Connection Issues

- Ensure backend is running on http://localhost:8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for errors
- Verify CORS is configured in backend

### Build Issues

- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

## License

This project is for educational purposes.
