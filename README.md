# LBO Model Builder

A professional, fully-functional Leveraged Buyout (LBO) Model Builder for financial analysis and scenario testing.

## Features

✅ **Complete LBO Analysis**
- Transaction assumptions (entry, financing, equity, exit)
- 5-year operating projections with dynamic revenue/EBITDA modeling
- Professional Sources & Uses validation
- Detailed debt schedules (Senior, Subordinated, Revolver)
- Cash flow bridge with component breakdown
- Exit analysis with multiple scenarios
- Accurate sponsor returns (MOIC, IRR, actual calculations)

✅ **Advanced Analytics**
- Sensitivity analysis (Exit Multiple vs EBITDA, Entry vs Exit Multiple)
- Scenario Manager (Base/Downside/Upside cases)
- Returns attribution analysis
- Professional dashboard with KPIs and charts

✅ **Professional UI**
- Fully responsive design (desktop, tablet, mobile)
- Financial modeling aesthetic
- Real-time updates as assumptions change
- Comprehensive validation with clear error messages
- Tooltip explanations of financial terms

✅ **Real Calculations**
- No placeholder values or hard-coded results
- All financial formulas implemented accurately
- Dynamic updates when assumptions change
- Proper dependency tracking (assumption → calculations → results)

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

### Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000`

### Backend Setup (Python)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
API available at `http://localhost:8000`

### Database Setup
```bash
psql -U postgres
CREATE DATABASE lbo_model_builder;
\c lbo_model_builder
\i database/schema.sql
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for complete system design, data flow, and folder structure.

## Financial Formulas

See [docs/FORMULAS.md](./docs/FORMULAS.md) for detailed documentation of all financial calculations.

## API Documentation

See [docs/API.md](./docs/API.md) for complete API endpoint reference.

## Project Structure

```
lbo-model-builder/
├── frontend/          # Next.js React application
├── backend/           # Python FastAPI server
├── database/          # PostgreSQL schema
├── docs/              # Documentation
└── ARCHITECTURE.md    # System architecture
```

## Development Status

🔨 In active development. Core financial engine and APIs being built.

## License

MIT
