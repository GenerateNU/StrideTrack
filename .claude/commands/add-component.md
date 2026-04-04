Create a new React component following StrideTrack project conventions.

Component name: $ARGUMENTS

For the component "$ARGUMENTS":

1. **Component file** — Create in the appropriate `frontend/src/components/` subdirectory
   - Use TypeScript with proper prop type definitions
   - Use TailwindCSS for styling
   - Use named exports (not default exports)

2. **Data fetching** — If the component needs data:
   - Create a custom hook in `frontend/src/hooks/` following `*.hooks.ts` naming
   - Use TanStack Query (`useQuery`, `useMutation`) for all server state
   - Never use raw `fetch` or `useEffect` for data fetching

3. **Form validation** — If the component has forms:
   - Use Zod schemas for validation
   - Use React Hook Form for form state management

4. **Routing** — If this is a page component:
   - Place in `frontend/src/pages/`
   - Add route in the React Router configuration

Check existing components in the same directory for patterns and conventions before creating.
