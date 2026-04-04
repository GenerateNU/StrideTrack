## Frontend Rules

- Use Zod schemas for all form validation and API response parsing
- Use TanStack Query for all server state — no manual fetch/useEffect patterns for data fetching
- Use React Router for navigation
- Use TailwindCSS for styling — reference `frontend/tailwind.config.js` for theme values
- Use Bun as the package manager (not npm or yarn)
- File naming conventions: `*.hooks.ts` for hooks, `*.service.ts` for services
- Prefer named exports over default exports
- ESLint config is in `frontend/eslint.config.js`, Prettier config in `frontend/.prettierrc`
