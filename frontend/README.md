# StrideTrack Frontend

React application providing the analytics dashboard for StrideTrack biomechanical data visualization.

## Architecture

This frontend follows a **feature-based architecture** with clear separation of concerns:

```
Pages → Components → Hooks → API Client → Backend
```

**Design Principles:**

- **Pages:** Route-level components orchestrating feature views
- **Components:** Reusable UI components (feature-specific and shared)
- **Hooks:** Data fetching and state management via TanStack Query
- **Types:** Zod schemas for runtime validation and TypeScript types
- **Utils:** Shared utilities for validation and formatting

## Directory Structure

```
frontend/
├── src/
│   ├── main.tsx                      # App entry point
│   ├── App.tsx                       # Root component with routing
│   ├── axios.config.ts               # Axios client configuration
│   ├── pages/                        # Route-level components
│   │   └── ExamplePage.tsx           # Example CRUD page
│   ├── components/                   # Reusable components
│   │   ├── ui/                       # Base UI components (shadcn)
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   └── label.tsx
│   │   ├── example/                  # Feature-specific components
│   │   │   ├── TrainingRunForm.tsx
│   │   │   └── TrainingRunsList.tsx
│   │   ├── QueryError.tsx            # Shared error state component
│   │   └── QueryLoading.tsx          # Shared loading state component
│   ├── hooks/                        # TanStack Query hooks
│   │   └── exampleTrainingRuns.hooks.ts
│   ├── types/                        # Zod schemas and TypeScript types
│   │   ├── example.types.ts
│   │   └── buttonVariants.types.ts
│   ├── utils/                        # Shared utilities
│   │   ├── validation.ts             # Zod validation helpers
│   │   └── format.ts                 # Formatting utilities
│   └── lib/                          # Third-party integrations
│       └── utils.ts                  # cn() utility for Tailwind
├── public/                           # Static assets
├── index.html                        # HTML entry point
├── package.json                      # Dependencies (bun)
├── bun.lockb                         # Locked dependencies
├── vite.config.ts                    # Vite configuration
├── tailwind.config.js                # Tailwind CSS configuration
├── tsconfig.json                     # TypeScript configuration
├── tsconfig.app.json                 # App-specific TS config
├── tsconfig.node.json                # Node-specific TS config
├── eslint.config.js                  # ESLint configuration
├── postcss.config.js                 # PostCSS configuration
└── components.json                   # shadcn/ui configuration
```

## Data Flow

**Query Flow:**

1. Component calls **Hook** (e.g., `useGetAllTrainingRuns()`)
2. Hook returns `{ data, isLoading, error, refetch }` with named properties
3. Component renders based on state (loading, error, success)
4. TanStack Query handles caching, background refetching

**Mutation Flow:**

1. Component calls **Hook** (e.g., `useCreateTrainingRun()`)
2. Hook returns `{ mutateAsync, isPending, error }` with named properties
3. Component calls mutation function with validated data
4. On success, related queries are automatically invalidated

**Validation Flow:**

- Zod schemas validate API responses via `validateResponse()`
- Zod schemas validate form data before mutations
- TypeScript types derived from Zod schemas for type safety

## Hooks Pattern

Hooks return named properties for cleaner component usage:

**GET Queries:**

```typescript
const {
  trainingRuns,
  trainingRunsIsLoading,
  trainingRunsError,
  trainingRunsRefetch,
} = useGetAllTrainingRuns();
```

**Mutations:**

```typescript
const {
  createTrainingRun,
  createTrainingRunIsLoading,
  createTrainingRunError,
} = useCreateTrainingRun();
```

## Tech Stack

- **Runtime:** Bun
- **Framework:** React 19 + Vite
- **Routing:** React Router v7
- **State:** TanStack Query v5
- **Styling:** Tailwind CSS v3
- **Components:** shadcn/ui (Radix primitives)
- **Validation:** Zod
- **HTTP Client:** Axios
- **TypeScript:** v5.9 (strict mode)

## Development

**Run locally:**

```bash
cd frontend
bun install        # Install dependencies
bun run dev        # Start dev server (http://localhost:5173)
```

**Available scripts:**

| Command           | Description              |
| ----------------- | ------------------------ |
| `bun run dev`     | Start development server |
| `bun run build`   | Type-check and build     |
| `bun run lint`    | Run ESLint               |
| `bun run preview` | Preview production build |

**Add new feature:**

1. Create types in `src/types/<feature>.types.ts`
2. Create hooks in `src/hooks/<feature>.hooks.ts`
3. Create components in `src/components/<feature>/`
4. Create page in `src/pages/<Feature>Page.tsx`
5. Add route in `src/App.tsx`

## Environment Variables

Create a `.env` file (see `.env.example` if available):

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Design Patterns

**TanStack Query:**
Server state management with automatic caching, background refetching, and optimistic updates.

**Zod Validation:**
Runtime validation of API responses ensures type safety beyond TypeScript's compile-time checks.

**Component Composition:**
Base UI components (shadcn/ui) composed into feature-specific components for consistent styling.

**Named Hook Returns:**
Hooks return descriptively named properties (e.g., `trainingRunsIsLoading`) for clearer component code.

## File Naming Conventions

- `*.hooks.ts` - TanStack Query hooks
- `*.types.ts` - Zod schemas and TypeScript types
- `*.service.ts` - API service functions (if separated from hooks)
- Components use PascalCase: `TrainingRunForm.tsx`

## API Type & Hook Generation (Orval)

This project uses **Orval** to automatically generate TypeScript types and TanStack Query hooks from the FastAPI OpenAPI specification. This ensures the frontend stays fully aligned with backend contracts and eliminates manually maintained API types and hooks.

### Prerequisites

- Backend running locally
- OpenAPI spec available at: ${VITE_API_URL}/openapi.json

(Default: `http://localhost:8000/openapi.json`)

### Regenerating API Code

From the `frontend/` directory, run:

```bash
bun run api:gen
```
