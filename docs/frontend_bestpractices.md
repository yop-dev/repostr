# Frontend Best Practices

Scope: React + TypeScript, Tailwind CSS, Clerk (Auth), deployed on Vercel. This guide supports both Vite and Next.js. Prefer Next.js for server rendering and routing; use Vite for pure SPA.

---

## 1) Core Principles
- Readability over cleverness; reduce cognitive load.
- Type safety first (TypeScript strict mode on).
- Accessibility and performance are features.
- Minimize global state; prefer server state tools over Redux unless necessary.
- Keep components small, pure, and testable.

---

## 2) Project Structure
Choose one of the following depending on the stack.

A) Next.js (App Router) recommended
```
/frontend
  app/
    (marketing)/
      page.tsx
      layout.tsx
    (app)/
      uploads/
        page.tsx
      dashboard/
        page.tsx
    api/ (route handlers if needed)
    layout.tsx
    global-error.tsx
    error.tsx
    loading.tsx
  components/
    ui/
    forms/
    layout/
  features/
    uploads/
      components/
      hooks/
      api/
    content/
      components/
      api/
  hooks/
  lib/
    api/
    auth/
    utils/
  public/
  styles/
    globals.css
    tailwind.css
  types/
  tests/
  eslint.config.js
  tsconfig.json
```

B) Vite (SPA) with React Router
```
/frontend
  src/
    routes/
      index.tsx
      uploads.tsx
      dashboard.tsx
    components/
      ui/
      forms/
    features/
      uploads/
        components/
        hooks/
        api/
      content/
        components/
        api/
    hooks/
    lib/
      api/
      auth/
      utils/
    styles/
      globals.css
      tailwind.css
    types/
    main.tsx
  public/
  tests/
  eslint.config.js
  tsconfig.json
```

Guidelines
- Group by feature (features/<feature>/...) to keep domain logic cohesive.
- Reusable primitives live in components/ui.
- Shared helpers in lib (pure, framework-agnostic when possible).

---

## 3) Naming Conventions
- Directories: kebab-case (e.g., content-editor, upload-wizard)
- Components: PascalCase (e.g., UploadCard.tsx)
- Hooks: useXxx format (e.g., useUpload.ts)
- Files: camelCase for utilities (e.g., formatTime.ts)
- Types/Interfaces: PascalCase (no I- prefix), enums in PascalCase
- Tests: Same name + .test.ts(x) next to file or under tests/
- CSS Modules (if needed): component-name.module.css

---

## 4) TypeScript
- Enable strict: true and noImplicitAny: true.
- Prefer type over interface for data shapes; use interface for public component props if extending.
- Avoid any; use unknown then narrow.
- Define shared types in /shared and import via path aliases (e.g., @shared/types).

Path Aliases
- Next.js: set baseUrl and paths in tsconfig.compilerOptions; alias to @/ for frontend and @shared/ for shared.
- Vite: mirror the same with vite.config resolve.alias.

---

## 5) State Management
- Local UI state: useState/useReducer.
- Server state: TanStack Query (React Query) or SWR for fetching, caching, retries.
  - Keys: use tuples, e.g., ["uploads", userId].
  - Keep server state in the cache, not in global stores.
- Global client state (rare): Zustand or Context for simple cross-cutting concerns (theme, toasts).
- Forms: React Hook Form + Zod for schema validation and TS inference.

---

## 6) API Layer
- Centralize fetch logic under lib/api.
- Use a thin wrapper around fetch with:
  - Base URL, JSON serialization, error normalization
  - Auth: attach Clerk token via getToken() only when needed (server components/routes in Next can use server-side helpers).
- Define request/response types in /shared. Never use untyped any.
- Handle pagination, sorting, and filters with typed params.
- Prefer AbortController for cancellable requests on route change.

---

## 7) Styling (Tailwind)
- Keep globals minimal; lean on utility classes.
- Use clsx/cva for conditional classes and variants.
- Extract repeated patterns into components/ui.
- Configure theme tokens in tailwind.config.js; avoid arbitrary values where a token fits.
- Respect prefers-color-scheme; use CSS variables for theming.

---

## 8) Accessibility (a11y)
- Use semantic HTML; headings in order; label inputs.
- Ensure focus states are visible; trap focus in modals.
- Prefer headless libraries (e.g., Radix UI) for accessible primitives.
- Provide alt text for images and captions for media.
- Test with keyboard only and screen readers for key flows.

---

## 9) Performance
- Next.js: leverage Server Components, edge caching, dynamic import for heavy client-only modules.
- Vite: code-split routes and lazy-load feature modules.
- Memoize expensive components with React.memo/useMemo/useCallback when profiling shows impact.
- Virtualize long lists (e.g., react-virtual or react-window).
- Use next/image or responsive <img> with sizes and loading="lazy".

---

## 10) Error Handling & UX
- Centralize error boundaries (Next: error.tsx in routes, root-level global-error.tsx).
- Normalize API errors; map to user-friendly messages.
- Use a non-blocking toast system for transient errors; show inline errors for forms.

---

## 11) Testing
- Unit: Vitest or Jest + @testing-library/react.
- Integration/Component: Testing Library with realistic user flows.
- E2E: Playwright; run in CI against preview URL.
- Snapshots only for stable UI primitives.
- Targets: >80% statements/branches on critical features.

Suggested structure
```
/tests
  unit/
  integration/
  e2e/
```

---

## 12) Linting, Formatting, and Quality Gates
- ESLint with typescript-eslint and eslint-plugin-react, eslint-plugin-security, eslint-plugin-tailwindcss.
- Prettier for formatting; align with Tailwind class sorting.
- Type-check in CI (tsc --noEmit).
- Run lint, type-check, unit tests on pre-push (Husky + lint-staged).

---

## 13) Environment Management
- Never commit .env.* files; use .env.local for dev.
- Next.js: public env vars must be prefixed with NEXT_PUBLIC_.
- Vite: public env vars must be prefixed with VITE_.
- Validate env at startup using Zod (e.g., env.ts) and fail fast with helpful messages.

Example (keys are placeholders):
- NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY={{NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}}
- CLERK_SECRET_KEY={{CLERK_SECRET_KEY}}
- NEXT_PUBLIC_SUPABASE_URL={{NEXT_PUBLIC_SUPABASE_URL}}

---

## 14) Accessibility & i18n readiness
- All text copy should be outside components to ease translation later.
- Avoid concatenating translated strings; prefer ICU messages.

---

## 15) Git & PR Conventions
- Conventional Commits (feat:, fix:, chore:, docs:, refactor:, perf:, test:).
- Small, focused PRs (<400 lines changed when possible).
- PR must pass: build, type-check, lint, unit tests, e2e smoke tests.
- Include screenshots/recordings for notable UI changes.

PR checklist
- [ ] Lint, type-check, tests pass
- [ ] Accessibility reviewed for new UI
- [ ] API types aligned with /shared
- [ ] Docs updated (README/CHANGELOG as needed)

---

## 16) Security
- Never interpolate unsanitized HTML; avoid dangerouslySetInnerHTML. If required, sanitize (DOMPurify) and document why.
- Content Security Policy (CSP) configured in Next.js headers (or meta for SPA).
- Do not store secrets in localStorage; use httpOnly cookies for server-managed sessions.
- Treat all user input as untrusted; validate in UI and re-validate on server.

---

## 17) Observability
- Use a lightweight client logger for non-PII events.
- Capture basic performance metrics (LCP, CLS) via web-vitals; send to backend for dashboards if needed.

---

## 18) When to add a new dependency
- Only if it reduces net code and complexity, is actively maintained, and has a permissive license.
- Prefer small focused libs over kitchen-sink frameworks.

