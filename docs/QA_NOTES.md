# QA notes

- Desktop preview verified at 1280px: warm cream canvas, persistent rail, sticky top bar, dark hero card, two-column verification workspace, open simulator drawer, risk meter, and recent activity table all render without layout errors.
- Functional simulator verified: selecting **Fake electricity bill SMS** updates the risk score to 94, status to High risk, source to Incoming SMS, action to Do not open or pay, and replaces the signal breakdown with three alert/review signals. Activity count increments and a toast appears.
- Mobile preview verified at 375px: navigation collapses behind the menu button, the live monitor starts collapsed to avoid occluding the workspace, tabs scroll horizontally, hero content reflows, and the live monitor can be reopened from the floating trigger.
- TypeScript and production build checks pass. Vite emits a chunk-size advisory because the starter dependency bundle includes the full UI component set; it is non-blocking.

## Multi-page expansion QA

The expanded website was visually reviewed at desktop width across the Overview, Scan history, How it works, and Safety guide pages. The generated hero and architecture images render crisply and match the warm editorial brand direction. The history page shows mock URL and QR analytics with filter tabs and five previously analysed entries.

Dark mode was toggled through the navigation control and verified on the overview page and scan history page. The theme preference persists through local storage, and the control updates its accessible label between light and dark mode. Navigation from Overview to Scan history was verified through the live preview without a full-page reload.

## Final integration QA

The Live System Monitor now starts collapsed and is available through a floating bottom-right button; the panel opens as a right-side drawer with a scrim rather than occupying the page layout. The expanded dark-mode overrides were applied across the application shell, rail, cards, hero, forms, risk review, history table, and monitor drawer.

The frontend typecheck and production build pass after adding `client/src/lib/api.ts`. The backend Python package passes bytecode compilation and includes a Dockerfile, Render manifest, Gemini structured-output call, CORS configuration, `/health`, multipart image support, JSON support, and trace-aware logging. When `VITE_API_BASE_URL` is configured, every manual Studio submission calls the backend; local preview falls back to demo data only if the service is unavailable.

## Loading-state QA

While a Gemini request is pending, the risk review now shows an animated circular loading skeleton and the signal breakdown shows three shimmer rows. The previous result is replaced only after the response arrives, and the returned assessment enters with a short translate-and-fade transition. The UI also validates missing image input before making a request. TypeScript, production build, and backend Python compilation pass after the loading-state repair.
