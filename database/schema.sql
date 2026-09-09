-- PostgreSQL Schema for LBO Model Builder
-- Complete database structure for financial modeling application

-- ============================================================================
-- USERS AND PROJECTS
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MODELS
-- ============================================================================

CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    company_name VARCHAR(255),
    model_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locked BOOLEAN DEFAULT FALSE
);

-- ============================================================================
-- ASSUMPTIONS (Transaction, Financing, Equity, Exit)
-- ============================================================================

CREATE TABLE assumptions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    
    -- Transaction Assumptions
    entry_enterprise_value NUMERIC(15, 2),
    entry_ebitda NUMERIC(15, 2),
    entry_ebitda_multiple NUMERIC(10, 2),
    existing_debt NUMERIC(15, 2) DEFAULT 0,
    existing_cash NUMERIC(15, 2) DEFAULT 0,
    transaction_fees NUMERIC(15, 2) DEFAULT 0,
    financing_fees NUMERIC(15, 2) DEFAULT 0,
    min_cash_balance NUMERIC(15, 2) DEFAULT 10000000, -- $10M default
    
    -- Financing Assumptions
    senior_debt_amount NUMERIC(15, 2),
    senior_debt_ebitda_multiple NUMERIC(10, 2),
    senior_interest_rate NUMERIC(6, 3) DEFAULT 5.000, -- percentage
    senior_amortization_rate NUMERIC(6, 3) DEFAULT 2.000, -- % of original
    
    subordinated_debt_amount NUMERIC(15, 2),
    subordinated_debt_ebitda_multiple NUMERIC(10, 2),
    subordinated_interest_rate NUMERIC(6, 3) DEFAULT 8.000,
    subordinated_amortization_rate NUMERIC(6, 3) DEFAULT 1.000,
    
    revolver_commitment NUMERIC(15, 2),
    revolver_interest_rate NUMERIC(6, 3) DEFAULT 6.000,
    
    cash_sweep_percentage NUMERIC(5, 2) DEFAULT 50.00, -- 0-100%
    
    -- Equity Assumptions
    sponsor_equity NUMERIC(15, 2),
    management_rollover NUMERIC(15, 2) DEFAULT 0,
    other_equity NUMERIC(15, 2) DEFAULT 0,
    
    -- Exit Assumptions
    exit_year INTEGER DEFAULT 5,
    exit_ebitda_multiple NUMERIC(10, 2),
    exit_enterprise_value NUMERIC(15, 2),
    exit_debt NUMERIC(15, 2),
    exit_cash NUMERIC(15, 2),
    
    -- Operating Model Assumptions
    projection_years INTEGER DEFAULT 5,
    base_year_revenue NUMERIC(15, 2),
    revenue_growth_year1 NUMERIC(6, 3),
    revenue_growth_year2 NUMERIC(6, 3),
    revenue_growth_year3 NUMERIC(6, 3),
    revenue_growth_year4 NUMERIC(6, 3),
    revenue_growth_year5 NUMERIC(6, 3),
    
    ebitda_margin_year1 NUMERIC(6, 3),
    ebitda_margin_year2 NUMERIC(6, 3),
    ebitda_margin_year3 NUMERIC(6, 3),
    ebitda_margin_year4 NUMERIC(6, 3),
    ebitda_margin_year5 NUMERIC(6, 3),
    
    capex_percentage_revenue NUMERIC(6, 3),
    tax_rate NUMERIC(6, 3) DEFAULT 25.000,
    nwc_percentage_revenue NUMERIC(6, 3) DEFAULT 10.000,
    da_percentage_revenue NUMERIC(6, 3) DEFAULT 5.000,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assumptions_model_id ON assumptions(model_id);

-- ============================================================================
-- OPERATING PROJECTIONS (Year-by-year P&L)
-- ============================================================================

CREATE TABLE operating_projections (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    
    -- Income Statement
    revenue NUMERIC(15, 2),
    revenue_growth_pct NUMERIC(6, 3),
    ebitda NUMERIC(15, 2),
    ebitda_margin_pct NUMERIC(6, 3),
    depreciation_amortization NUMERIC(15, 2),
    ebit NUMERIC(15, 2),
    interest_expense NUMERIC(15, 2),
    ebt NUMERIC(15, 2),
    tax_expense NUMERIC(15, 2),
    net_income NUMERIC(15, 2),
    
    -- Balance Sheet Items
    accounts_receivable NUMERIC(15, 2),
    inventory NUMERIC(15, 2),
    accounts_payable NUMERIC(15, 2),
    other_working_capital NUMERIC(15, 2),
    
    -- Cash Flow
    capex NUMERIC(15, 2),
    capex_pct_revenue NUMERIC(6, 3),
    change_nwc NUMERIC(15, 2),
    free_cash_flow NUMERIC(15, 2),
    
    -- Cash Available for Debt Paydown
    cash_available_for_debt_paydown NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operating_projections_model_year ON operating_projections(model_id, year);

-- ============================================================================
-- DEBT INSTRUMENTS (Senior, Subordinated, Revolver definitions)
-- ============================================================================

CREATE TABLE debt_instruments (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    instrument_type VARCHAR(50) NOT NULL, -- 'senior_term_loan', 'subordinated_debt', 'revolver'
    name VARCHAR(255),
    
    -- Debt Characteristics
    initial_balance NUMERIC(15, 2),
    interest_rate NUMERIC(6, 3),
    amortization_rate NUMERIC(6, 3), -- % of original per year
    repayment_priority INTEGER DEFAULT 0, -- Lower number = higher priority
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debt_instruments_model_id ON debt_instruments(model_id);

-- ============================================================================
-- DEBT SCHEDULES (Year-by-year debt tracking)
-- ============================================================================

CREATE TABLE debt_schedules (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    debt_instrument_id INTEGER NOT NULL REFERENCES debt_instruments(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    
    beginning_balance NUMERIC(15, 2),
    mandatory_amortization NUMERIC(15, 2),
    optional_repayment NUMERIC(15, 2),
    draws NUMERIC(15, 2) DEFAULT 0, -- for revolver
    repayments NUMERIC(15, 2) DEFAULT 0, -- for revolver
    interest_rate NUMERIC(6, 3),
    cash_interest_expense NUMERIC(15, 2),
    ending_balance NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debt_schedules_model_year ON debt_schedules(model_id, year);
CREATE INDEX idx_debt_schedules_instrument ON debt_schedules(debt_instrument_id);

-- ============================================================================
-- SOURCES & USES
-- ============================================================================

CREATE TABLE sources_uses (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    
    -- USES
    purchase_equity NUMERIC(15, 2),
    refinance_existing_debt NUMERIC(15, 2),
    transaction_fees NUMERIC(15, 2),
    financing_fees NUMERIC(15, 2),
    other_uses NUMERIC(15, 2) DEFAULT 0,
    total_uses NUMERIC(15, 2),
    
    -- SOURCES
    senior_debt NUMERIC(15, 2),
    subordinated_debt NUMERIC(15, 2),
    revolver NUMERIC(15, 2),
    sponsor_equity NUMERIC(15, 2),
    management_rollover NUMERIC(15, 2),
    other_equity NUMERIC(15, 2),
    total_sources NUMERIC(15, 2),
    
    -- Metrics
    total_debt NUMERIC(15, 2),
    debt_ebitda_multiple NUMERIC(10, 2),
    equity_percentage NUMERIC(6, 3),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_uses_model_id ON sources_uses(model_id);

-- ============================================================================
-- EXIT ANALYSIS
-- ============================================================================

CREATE TABLE exit_analysis (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    exit_year INTEGER NOT NULL,
    
    -- Exit Year Metrics
    exit_ebitda NUMERIC(15, 2),
    exit_ebitda_multiple NUMERIC(10, 2),
    exit_enterprise_value NUMERIC(15, 2),
    exit_debt NUMERIC(15, 2),
    exit_cash NUMERIC(15, 2),
    exit_equity_value NUMERIC(15, 2),
    
    -- Entry vs Exit
    entry_enterprise_value NUMERIC(15, 2),
    entry_ebitda NUMERIC(15, 2),
    entry_ebitda_multiple NUMERIC(10, 2),
    entry_debt NUMERIC(15, 2),
    entry_cash NUMERIC(15, 2),
    entry_equity_value NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exit_analysis_model_id ON exit_analysis(model_id);

-- ============================================================================
-- RETURNS ANALYSIS (MOIC, IRR, Proceeds)
-- ============================================================================

CREATE TABLE returns_analysis (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    scenario_id INTEGER REFERENCES scenarios(id) ON DELETE SET NULL,
    
    -- Sponsor Investment
    sponsor_initial_investment NUMERIC(15, 2),
    management_rollover_investment NUMERIC(15, 2),
    total_sponsor_investment NUMERIC(15, 2),
    
    -- Exit Proceeds
    sponsor_exit_equity_proceeds NUMERIC(15, 2),
    cumulative_distributions NUMERIC(15, 2) DEFAULT 0,
    sponsor_total_proceeds NUMERIC(15, 2),
    
    -- Returns Metrics
    moic NUMERIC(10, 3), -- Money Multiple of Invested Capital
    irr NUMERIC(6, 3), -- Internal Rate of Return %
    total_profit NUMERIC(15, 2),
    hold_period_years NUMERIC(5, 1),
    
    -- Contribution Analysis
    ebitda_growth_contribution NUMERIC(15, 2),
    multiple_expansion_contribution NUMERIC(15, 2),
    debt_paydown_contribution NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_returns_analysis_model_id ON returns_analysis(model_id);

-- ============================================================================
-- SCENARIOS (Base Case, Downside, Upside)
-- ============================================================================

CREATE TABLE scenarios (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    scenario_type VARCHAR(50) NOT NULL, -- 'base', 'downside', 'upside', 'custom'
    name VARCHAR(255),
    description TEXT,
    
    -- Scenario Assumption Overrides
    revenue_growth_adjustment NUMERIC(6, 3) DEFAULT 0, -- % adjustment to base
    ebitda_margin_adjustment NUMERIC(6, 3) DEFAULT 0,
    capex_adjustment NUMERIC(6, 3) DEFAULT 0,
    working_capital_adjustment NUMERIC(6, 3) DEFAULT 0,
    interest_rate_adjustment NUMERIC(6, 3) DEFAULT 0,
    entry_multiple_adjustment NUMERIC(6, 3) DEFAULT 0,
    exit_multiple_adjustment NUMERIC(6, 3) DEFAULT 0,
    debt_level_adjustment NUMERIC(6, 3) DEFAULT 0,
    exit_year_override INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scenarios_model_id ON scenarios(model_id);

-- ============================================================================
-- SENSITIVITY ANALYSIS RESULTS
-- ============================================================================

CREATE TABLE sensitivity_analysis (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    sensitivity_type VARCHAR(100) NOT NULL, -- 'exit_multiple_vs_ebitda', 'entry_vs_exit_multiple', etc.
    
    -- Sensitivity Parameters
    x_axis_label VARCHAR(100),
    y_axis_label VARCHAR(100),
    x_value NUMERIC(10, 3),
    y_value NUMERIC(10, 3),
    
    -- Results
    irr NUMERIC(6, 3),
    moic NUMERIC(10, 3),
    equity_value NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensitivity_analysis_model ON sensitivity_analysis(model_id, sensitivity_type);

-- ============================================================================
-- MODEL VERSIONS (Audit Trail)
-- ============================================================================

CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    assumptions_json JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

CREATE INDEX idx_model_versions_model_id ON model_versions(model_id);

-- ============================================================================
-- CASH FLOW BRIDGE (Detailed cash flow components)
-- ============================================================================

CREATE TABLE cash_flow_bridge (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    
    net_income NUMERIC(15, 2),
    add_depreciation_amortization NUMERIC(15, 2),
    subtract_capex NUMERIC(15, 2),
    subtract_change_nwc NUMERIC(15, 2),
    free_cash_flow NUMERIC(15, 2),
    
    subtract_mandatory_amortization NUMERIC(15, 2),
    subtract_optional_repayment NUMERIC(15, 2),
    change_in_cash NUMERIC(15, 2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cash_flow_bridge_model_year ON cash_flow_bridge(model_id, year);

-- Create scenarios table reference
ALTER TABLE returns_analysis 
ADD CONSTRAINT fk_returns_scenarios 
FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE SET NULL;

-- Create indexes for common queries
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_models_project_id ON models(project_id);
