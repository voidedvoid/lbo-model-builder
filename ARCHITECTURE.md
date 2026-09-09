# LBO Model Builder - System Architecture

## Overview
A professional Leveraged Buyout (LBO) Model Builder featuring real-time financial calculations, scenario analysis, sensitivity analysis, and comprehensive returns analysis.

## Technology Stack
- **Frontend**: Next.js 14, React, TypeScript, TailwindCSS
- **Backend**: Python (FastAPI), NumPy, Pandas
- **Database**: PostgreSQL
- **Deployment**: Ready for Vercel (Frontend), Railway/Heroku (Backend), AWS RDS (DB)

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│                     Next.js Frontend (TypeScript)               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Dashboard │ Assumptions │ Operating │ Sources │ Debt │... │  │
│  │ (Charts)  │ (Forms)     │ (Tables)  │ & Uses  │Sch...│    │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  API LAYER (Next.js API Routes)                 │
│  /api/models, /api/assumptions, /api/calculate, etc.           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Python FastAPI Server)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Financial Calculation Engine (Python)           │  │
│  │  • Operating Model Calculator                           │  │
│  │  • Debt Schedule Engine                                 │  │
│  │  • Cash Flow Bridge                                     │  │
│  │  • Exit Analysis                                        │  │
│  │  • Returns Calculator (IRR, MOIC)                      │  │
│  │  • Sensitivity Analysis                                │  │
│  │  • Scenario Manager                                    │  │
│  │  • Input Validation                                    │  │
│  └────────────────────────────────────���─────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                          │
│  • users, projects, models, assumptions, operating_projections │
│  • debt_instruments, debt_schedules, scenarios, returns         │
│  • model_versions, audit_logs                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow (User Changes Assumption)
1. User edits assumption in Next.js form → validates client-side
2. Form submits to `/api/assumptions/update`
3. Next.js API route sends to Python backend `/calculate`
4. Python engine recalculates all dependent models (Operating → Debt → Cash Flow → Returns)
5. Results returned as JSON
6. Frontend updates all affected tables/charts
7. Data persisted to PostgreSQL

## Folder Structure
```
lbo-model-builder/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── api/                # API routes (proxy to Python backend)
│   │   ├── dashboard/          # Dashboard page
│   │   ├── model/              # Model workspace
│   │   │   ├── assumptions/
│   │   │   ├── operating/
│   │   │   ├── sources-uses/
│   │   │   ├── debt-schedule/
│   │   │   ├── cash-flow/
│   │   │   ├── exit-analysis/
│   │   │   ├── returns/
│   │   │   ├── sensitivity/
│   │   │   └── scenarios/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── layout/
│   │   ├── forms/
│   │   ├── tables/
│   │   ├── charts/
│   │   └── common/
│   ├── lib/
│   │   ├── api.ts             # API client functions
│   │   ├── types.ts           # TypeScript types
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── styles/
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── backend/                     # Python FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/               # API routes
│   │   │   ├── models.py
│   │   │   ├── assumptions.py
│   │   │   ├── calculations.py
│   │   │   ├── scenarios.py
│   │   │   └── sensitivity.py
│   │   ├── core/              # Core business logic
│   │   │   ├── lbo_model.py   # Main LBO model class
│   │   │   ├── operating_model.py
│   │   │   ├── debt_schedule.py
│   │   │   ├── cash_flow.py
│   │   │   ├── exit_analysis.py
│   │   │   ├── returns_calculator.py
│   │   │   ├── sensitivity_analysis.py
│   │   │   └── validations.py
│   │   ├── db/                # Database layer
│   │   │   ├── database.py
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   └── crud.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── assumption.py
│   │   │   ├── model.py
│   │   │   └── results.py
│   │   └── utils/
│   │       └── helpers.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── database/
│   └── schema.sql             # PostgreSQL schema
├── docs/
│   ├── FORMULAS.md            # Financial formulas documented
│   ├── API.md                 # API endpoint documentation
│   └── DEPLOYMENT.md
├── .gitignore
├── README.md
└── ARCHITECTURE.md (this file)

## Key Financial Formulas

### Operating Model
- **EBITDA** = Revenue × EBITDA Margin %
- **EBIT** = EBITDA - D&A
- **EBT** = EBIT - Interest Expense
- **Net Income** = EBT × (1 - Tax Rate)
- **Free Cash Flow** = Net Income + D&A - CapEx - Δ NWC

### Debt Schedule
- **Cash Interest** = Beginning Balance × Interest Rate
- **Mandatory Amortization** = User-specified or % of EBITDA
- **Optional Repayment** = Cash Available for Debt Paydown × Cash Sweep %
- **Ending Balance** = Beginning Balance - Mandatory Amortization - Optional Repayment (cannot go negative)

### Exit Analysis
- **Exit Enterprise Value** = Exit EBITDA × Exit Multiple
- **Exit Equity Value** = Exit EV - Exit Debt + Exit Cash
- **Sponsor Proceeds** = Exit Equity Value - Sponsor Initial Investment Reinvested

### Returns
- **MOIC** = Sponsor Exit Proceeds ÷ Sponsor Initial Investment
- **IRR** = Internal Rate of Return calculated from actual cash flow timeline

### Sources & Uses
- **Total Uses** = Purchase Equity + Refinance Debt + Transaction Fees + Financing Fees + Other
- **Total Sources** = Senior Debt + Sub Debt + Revolver + Sponsor Equity + Management Rollover + Other
- **Validation**: Total Sources MUST = Total Uses

## API Endpoints (Python Backend)

### Models
- `POST /api/models` - Create new LBO model
- `GET /api/models/{model_id}` - Load model
- `PUT /api/models/{model_id}` - Update model metadata

### Assumptions
- `POST /api/assumptions` - Save assumptions
- `GET /api/assumptions/{model_id}` - Load assumptions
- `PUT /api/assumptions/{model_id}` - Update assumptions

### Calculations
- `POST /api/calculate` - Run all calculations given assumptions
- `POST /api/calculate/debt-schedule` - Calculate debt schedule only
- `POST /api/calculate/returns` - Calculate returns (IRR, MOIC)
- `POST /api/calculate/sensitivity` - Run sensitivity analysis

### Scenarios
- `POST /api/scenarios` - Create scenario
- `GET /api/scenarios/{model_id}` - List scenarios
- `PUT /api/scenarios/{scenario_id}` - Update scenario
- `POST /api/scenarios/{scenario_id}/calculate` - Calculate with scenario assumptions

## Database Schema
See `database/schema.sql` for complete PostgreSQL schema including:
- users
- projects
- models
- assumptions (transaction, financing, equity, exit)
- operating_projections (revenue, ebitda, capex, etc. for each year)
- debt_instruments (senior, subordinated, revolver definitions)
- debt_schedules (year-by-year debt balances, interest, amortization)
- scenarios (base, downside, upside cases)
- returns (MOIC, IRR, equity value, proceeds)
- model_versions (audit trail)

## Frontend State Management
- React Context for model state
- Local form state for inputs
- Real-time calculation via API calls
- Suspense boundaries for async operations

## Validation Strategy
1. **Client-side**: Immediate feedback on invalid inputs (negative revenue, etc.)
2. **Server-side**: Full validation before calculation
3. **Financial logic**: Debt cannot go negative, Sources must equal Uses, dates must be logical
4. **Error messages**: Clear, actionable guidance to user

## Performance Considerations
- Calculations run on Python backend (efficient NumPy operations)
- Results cached in database
- Frontend queries only necessary data
- Sensitivity analysis generates grid results server-side
- Charts use lightweight libraries (Recharts)

## Security
- PostgreSQL only accessed by Python backend
- API authentication via JWT tokens (future)
- Input sanitization on all endpoints
- CORS properly configured

## Responsive Design Strategy
- Desktop: Full layout with sidebar navigation
- Tablet: Adaptive layout, collapsible sidebar
- Mobile: Bottom navigation or hamburger menu
- All tables support horizontal scroll within container (not page-level)
- Forms stack vertically on mobile
- Charts resize with container
- Continuous responsive adaptation (not breakpoint-based)

## Development Workflow
1. Backend calculations proven independently
2. API endpoints tested with Python test suite
3. Frontend components built and connected to API
4. End-to-end integration testing
5. Responsive design verified at multiple viewport sizes
