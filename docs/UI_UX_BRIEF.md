# UI/UX Design Brief — ModelGate

**Version:** 1.0  
**Date:** 2026-10-17

## 1. Design Philosophy

**Principles:**
- Developer-first: technical accuracy over marketing polish
- Information density without clutter
- Status-at-a-glance visibility
- Clear data provenance (DEMO vs PROVIDER vs ESTIMATED)
- No fake metrics
- Accessible and keyboard-friendly
- Fast and responsive

**Tone:**
- Professional and precise
- Technical language (not simplified)
- Honest about limitations
- Data labels over icons alone

## 2. Visual Design

### 2.1 Color Palette

**Light Theme:**
- Background: #ffffff
- Surface: #f9fafb
- Border: #e5e7eb
- Text primary: #111827
- Text secondary: #6b7280
- Accent: #3b82f6
- Success: #10b981
- Warning: #f59e0b
- Error: #ef4444

**Dark Theme:**
- Background: #0f172a
- Surface: #1e293b
- Border: #334155
- Text primary: #f1f5f9
- Text secondary: #94a3b8
- Accent: #60a5fa
- Success: #34d399
- Warning: #fbbf24
- Error: #f87171

### 2.2 Typography

**Font Stack:** Inter, system-ui, sans-serif  
**Code:** 'Fira Code', 'SF Mono', monospace  

**Sizes:**
- Heading 1: 32px/40px
- Heading 2: 24px/32px
- Heading 3: 20px/28px
- Body: 16px/24px
- Small: 14px/20px
- Code: 14px/20px

### 2.3 Spacing

**Scale:** 4px base unit  
**Common:** 8px, 12px, 16px, 24px, 32px, 48px

### 2.4 Components

**Buttons:**
- Primary: filled accent color
- Secondary: outlined
- Destructive: red background
- Disabled: 50% opacity
- Height: 40px default

**Cards:**
- White/surface background
- 1px border
- 8px border-radius
- 16px padding

**Tables:**
- Zebra striping on hover
- Sticky headers on scroll
- Sortable columns
- Row actions on hover

**Badges:**
- Provider status: green (healthy), yellow (degraded), red (down)
- Data source: blue (PROVIDER), purple (ESTIMATED), gray (UNKNOWN/DEMO)
- Status: green (200), yellow (4xx), red (5xx)

### 2.5 Icons

**Source:** Lucide icons  
**Usage:** Always paired with text labels  
**Size:** 20px default  

## 3. Layout Structure

### 3.1 Navigation

**Top Bar:**
- Logo + name (left)
- Workspace selector (center-left)
- User menu (right)
- Theme toggle (right)

**Sidebar:**
- Overview (dashboard icon)
- Workspaces (folder icon)
- API Keys (key icon)
- Providers (server icon)
- Models (grid icon)
- Requests (list icon)
- Analytics (chart icon)
- Settings (gear icon)

**Responsive:**
- Desktop: permanent sidebar
- Tablet: collapsible sidebar
- Mobile: hamburger menu

### 3.2 Content Area

**Structure:**
- Breadcrumb navigation
- Page heading + primary action
- Filter/search bar (where applicable)
- Main content
- Pagination (bottom)

**Max width:** 1400px centered

## 4. Screen Designs

### 4.1 Overview Dashboard

**Layout:** 2-column grid

**Top Row (Metrics):**
- Total requests (24h)
- Success rate (24h)
- Avg latency P95 (24h)
- Active workspaces

**Second Row:**
- Request volume chart (7 days, line chart)
- Top models by usage (bar chart)

**Third Row:**
- Provider health status (grid of cards)
- Recent failed requests (table, last 10)

**States:**
- Empty: "No requests yet. Create an API key to get started."
- Loading: skeleton loaders
- Error: error message with retry button

### 4.2 Workspaces & Applications

**Workspaces List:**
- Card grid layout
- Each card: workspace name, app count, usage summary, actions menu
- Create workspace button (top right)

**Workspace Detail:**
- Tabs: Overview, Applications, Settings
- Overview: usage charts, quota utilization
- Applications table: name, API key count, last request, actions
- Create application button

**Application Detail:**
- API keys table
- Usage by key
- Quota settings
- Delete application (destructive)

### 4.3 API Key Management

**List View:**
- Table: Key prefix (mg_xxx...xxx), application, created, last used, status, actions
- Create key button (top right)

**Create Key Modal:**
- Application selector
- Permissions checkboxes (read, write, admin)
- Expiration (optional date picker)
- Create button
- Display full key once (with copy button + warning)

**Key Detail:**
- Metadata (created, last used, permissions)
- Usage stats (requests, tokens)
- Quota settings
- Revoke button (destructive, requires confirmation)

### 4.4 Provider Configuration

**List View:**
- Card grid: provider name, status badge, model count, health, configure button
- Add provider button

**Provider Form:**
- Provider type selector
- Base URL (validated)
- API key/credentials (password input, never displayed again)
- Health check toggle
- Timeout settings (connect, read, total)
- Retry policy settings
- Save button

**Provider Detail:**
- Status: healthy/degraded/down + last check time
- Available models table
- Recent requests chart
- Error rate chart
- Test connection button

**Demo Provider Card:**
- Special badge "DEMO MODE"
- Pre-configured, cannot edit
- "Demo provider returns deterministic responses. Configure a real provider above."

### 4.5 Model Catalog

**List/Grid View:**
- Filterable by provider, capability
- Sortable by name, provider
- Each entry: model name, provider, capabilities badges, status indicator

**Model Detail:**
- Provider
- Full model ID
- Capabilities (chat, streaming, function calling, vision)
- Context window (if known, otherwise "Unknown")
- Pricing (if configured, otherwise "Not configured")
- Availability status
- Recent usage stats

### 4.6 Routing Policy Editor

**Structure:**
- Workspace selector
- Default model selector
- Allowed providers (multi-select)
- Allowed models (multi-select from catalog)
- Fallback policy:
  - Enable fallback toggle
  - Fallback model selector (must be from allowed list)
  - Fallback conditions (original provider down, timeout, error 5xx)
- Save button

### 4.7 Request Logs

**List View:**
- Filter bar: date range, status, model, provider, application
- Search: request ID or partial prompt
- Table columns:
  - Request ID (monospace, copyable)
  - Timestamp
  - Application
  - Model requested
  - Provider used
  - Status (colored badge)
  - Latency (ms)
  - Tokens (input/output/total, with source badge)
  - Actions (view icon)
- Pagination (50 per page)

**Empty States:**
- No requests: "No requests found. Send your first request to /v1/chat/completions"
- No results: "No requests match your filters. Try adjusting your search."

### 4.8 Request Detail

**Layout:** Single column

**Sections:**
1. **Header:** Request ID (large monospace), timestamp, status badge
2. **Metadata:** Application, workspace, model (requested vs actual), provider, latency, retry count
3. **Usage:** Tokens (input/output/total) with source badge (PROVIDER/ESTIMATED/UNKNOWN/DEMO)
4. **Request:** Redacted prompt preview (first 200 chars), "View full request" button → modal
5. **Response:** Redacted response preview (first 200 chars), "View full response" button → modal
6. **Timeline:** Table of upstream attempts (provider, status, latency, error)
7. **Error Details:** If failed, error message and classification
8. **Metadata:** Full JSON expand/collapse

**Redaction Notice:**
"Sensitive data may be redacted. Configure redaction rules in Settings."

### 4.9 Token Usage Analytics

**Filters:**
- Date range picker (last 7/30/90 days, custom)
- Workspace selector
- Application selector
- Model selector
- Provider selector

**Charts:**
1. Token usage over time (area chart, stacked by input/output)
2. Usage by model (pie chart)
3. Usage by provider (bar chart)
4. Usage by application (bar chart)

**Table:**
- Aggregated stats: date, requests, input tokens, output tokens, total tokens, estimated cost
- Export button (CSV/JSON)

**Data Labels:**
- All charts show legend with source badges (PROVIDER, ESTIMATED, UNKNOWN, DEMO)
- Tooltip on hover shows exact values

### 4.10 Quota & Rate Limit Settings

**Structure:** Form per API key or workspace

**Rate Limits:**
- Requests per minute (input + enabled toggle)
- Requests per hour (input + enabled toggle)
- Requests per day (input + enabled toggle)

**Quotas:**
- Total request quota (input + enabled toggle)
- Token quota (input + enabled toggle)
- Reset policy selector (never, daily, weekly, monthly, manual)

**Concurrent Limits:**
- Max concurrent requests (input + enabled toggle)

**Preview:**
- "Current usage: X / Y (Z% utilized)" with progress bar

**Actions:**
- Save button
- Reset quota button (requires confirmation)

### 4.11 Provider Health Dashboard

**Grid Layout:**
- One card per configured provider
- Each card:
  - Provider name
  - Status indicator (large, colored)
  - Uptime % (last 24h)
  - Avg latency P95
  - Error rate %
  - Last successful request timestamp
  - Last health check timestamp
  - "View details" link

**Provider Detail View:**
- Health over time chart (24h, success rate %)
- Latency over time chart (24h, P50/P95/P99)
- Error rate chart (24h)
- Recent errors table
- Recent successful requests table

**Empty State:**
"No providers configured. Add a provider to start routing requests."

### 4.12 Fallback Policy Configuration

**Per Workspace:**

**Structure:**
1. Enable fallback toggle
2. Primary provider selector
3. Fallback provider selector
4. Fallback model selector
5. Conditions (checkboxes):
   - Primary provider unavailable
   - Primary request timeout
   - Primary returns 5xx error
   - Primary rate limited (optional)
6. Max fallback attempts (input, default 1)
7. Save button

**Preview:**
"When [primary] fails due to [conditions], retry with [fallback model] on [fallback provider] up to [N] times."

**Audit Log:**
- Table of recent fallback events: timestamp, request ID, reason, outcome

### 4.13 Usage Export

**Form:**
- Date range picker
- Workspace selector (or "All")
- Application selector (or "All")
- Format selector (CSV, JSON)
- Include request details toggle (may increase file size)
- Export button

**Output:**
- Download file: `modelgate-usage-YYYY-MM-DD.csv`
- Progress indicator for large exports
- Success message with download link

**CSV Columns:**
request_id, timestamp, workspace, application, model_requested, model_actual, provider, status, latency_ms, input_tokens, output_tokens, total_tokens, usage_source, estimated_cost, error_message

### 4.14 Workspace Members & Permissions

**MVP:** Out of scope (single user)

**Future:**
- Members table: email, role, added date, last active, actions
- Invite member form: email, role selector (viewer, developer, admin)
- Role permissions matrix table

### 4.15 API Documentation

**Structure:**
- Navigation: Getting Started, Authentication, Endpoints, Models, Errors, Rate Limits
- Code examples: curl, Python, JavaScript, TypeScript
- Interactive API explorer (optional)

**Getting Started:**
1. Create workspace
2. Create application
3. Generate API key
4. Send first request (code example)
5. View usage in dashboard

**Authentication:**
- Header format: `Authorization: Bearer mg_xxxxx`
- Key management link

**Endpoints:**

**POST /v1/chat/completions**

Request:
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 150
}
```

Response:
```json
{
  "id": "req_xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-3.5-turbo",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "Hello! How can I help?"},
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 8,
    "total_tokens": 23,
    "source": "PROVIDER"
  }
}
```

**Errors:**
- 400: Bad request (validation error)
- 401: Unauthorized (invalid/missing API key)
- 403: Forbidden (insufficient permissions)
- 404: Not found (unknown model)
- 429: Rate limited or quota exceeded
- 500: Internal server error
- 502: Provider error
- 504: Provider timeout

Error format:
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded: 60 requests per minute",
    "type": "rate_limit_error"
  }
}
```

### 4.16 System Health & Settings

**System Health:**
- Database status
- Redis status (if used)
- Disk space
- Memory usage
- Request queue depth

**Settings:**
- System name
- Contact email
- Data retention policy (days)
- Log redaction rules
- Default timeouts
- Default retry policy
- Theme preference
- Save button

## 5. Interaction Patterns

### 5.1 Loading States

**Pattern:** Skeleton loaders matching content structure  
**Duration:** Show immediately, no delay  
**Timeout:** Show error after 10 seconds  

### 5.2 Error States

**Pattern:**
- Icon + error message
- Retry button (if transient)
- Help link (if configuration needed)

**Examples:**
- "Failed to load requests. Retry"
- "No provider configured. Add provider"
- "Database connection lost. Check system health"

### 5.3 Empty States

**Pattern:**
- Icon + heading + description + primary action

**Examples:**
- "No API keys yet. Create your first API key to start sending requests."
- "No requests in the last 24 hours. Send a test request from the API documentation."

### 5.4 Form Validation

**Pattern:**
- Inline validation on blur
- Error message below field
- Red border on invalid field
- Disable submit until valid

**Examples:**
- "Base URL must start with https://"
- "API key is required"
- "Rate limit must be a positive integer"

### 5.5 Confirmations

**Pattern:** Modal dialog for destructive actions

**Structure:**
- Heading: "Delete application?"
- Description: "This will revoke all API keys and delete all data. This cannot be undone."
- Cancel button (default focus)
- Confirm button (destructive color)

### 5.6 Toasts

**Pattern:** Bottom-right notification

**Types:**
- Success: green, auto-dismiss 3s
- Error: red, dismiss on click
- Warning: yellow, auto-dismiss 5s
- Info: blue, auto-dismiss 3s

**Examples:**
- "API key created successfully"
- "Provider configuration saved"
- "Failed to revoke key. Retry"

### 5.7 Copy to Clipboard

**Pattern:** Button with icon → success state

**Interaction:**
1. Click copy button
2. Button icon changes to checkmark
3. Toast: "Copied to clipboard"
4. Revert after 2s

### 5.8 Search & Filter

**Pattern:**
- Search input with magnifying glass icon
- Filter dropdowns (multi-select where appropriate)
- "Clear filters" link when active
- Result count display

## 6. Accessibility

### 6.1 Keyboard Navigation

- All interactive elements focusable (tab order)
- Visible focus indicators (2px blue outline)
- Skip to main content link
- Modal focus trap
- ESC closes modals/dropdowns

### 6.2 Screen Readers

- Semantic HTML (nav, main, aside, header)
- ARIA labels on icons
- ARIA live regions for dynamic content
- Form labels associated with inputs
- Table headers properly marked

### 6.3 Contrast

- Text contrast ratio ≥4.5:1 (WCAG AA)
- Interactive elements ≥3:1
- Focus indicators ≥3:1

### 6.4 Text

- Resizable up to 200% without breaking layout
- No text in images (except logos)
- Line height ≥1.5 for body text

## 7. Responsive Breakpoints

**Desktop:** ≥1024px (full layout)  
**Tablet:** 768px–1023px (collapsible sidebar)  
**Mobile:** <768px (hamburger menu, stacked layout)  

**Adjustments:**
- Tables → scrollable or card layout on mobile
- Charts → simplified or scrollable on mobile
- Filters → drawer/modal on mobile
- Multi-column → single column on mobile

## 8. Performance

**Goals:**
- Initial page load: <2s
- Time to interactive: <3s
- Chart render: <500ms
- Table render (50 rows): <300ms

**Techniques:**
- Code splitting
- Lazy loading charts
- Virtualized tables for >100 rows
- Debounced search inputs (300ms)
- Optimistic UI updates

## 9. Data Provenance Labels

**Critical:** Always distinguish real from estimated/demo data.

**Badge Design:**
- Small pill badge next to data
- Color-coded
- Tooltip with explanation

**Labels:**
- **PROVIDER:** Green, "Reported by provider"
- **ESTIMATED:** Purple, "Estimated using tokenizer"
- **UNKNOWN:** Gray, "Usage unknown (display as —)"
- **DEMO:** Blue, "Demo/mock data (no real API call)"

**Usage:**
- Next to token counts in tables/cards
- In chart legends
- On analytics pages
- In exported CSVs

## 10. Implementation Notes

**Component Library:** shadcn/ui (Radix primitives + Tailwind)  
**Charts:** Recharts or Chart.js  
**Tables:** TanStack Table  
**Forms:** React Hook Form + Zod validation  
**Date pickers:** date-fns + Radix Calendar  
**Icons:** Lucide React  

**State Management:**
- React Query for server state
- Zustand for client state (theme, sidebar collapsed)
- No Redux (overkill for MVP)

**Routing:**
- Next.js App Router
- File-based routing
- Server components where appropriate

**API Client:**
- Axios or fetch wrapper
- Automatic auth header injection
- Error interceptor
- Loading state tracking
