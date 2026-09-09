from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

# ============================================================================
# ASSUMPTION SCHEMAS
# ============================================================================

class AssumptionBase(BaseModel):
    # Transaction Assumptions
    entry_enterprise_value: Optional[Decimal] = None
    entry_ebitda: Optional[Decimal] = None
    entry_ebitda_multiple: Optional[Decimal] = None
    existing_debt: Optional[Decimal] = 0
    existing_cash: Optional[Decimal] = 0
    transaction_fees: Optional[Decimal] = 0
    financing_fees: Optional[Decimal] = 0
    min_cash_balance: Optional[Decimal] = 10000000
    
    # Financing Assumptions
    senior_debt_amount: Optional[Decimal] = None
    senior_debt_ebitda_multiple: Optional[Decimal] = None
    senior_interest_rate: Optional[Decimal] = 5.0
    senior_amortization_rate: Optional[Decimal] = 2.0
    
    subordinated_debt_amount: Optional[Decimal] = None
    subordinated_debt_ebitda_multiple: Optional[Decimal] = None
    subordinated_interest_rate: Optional[Decimal] = 8.0
    subordinated_amortization_rate: Optional[Decimal] = 1.0
    
    revolver_commitment: Optional[Decimal] = None
    revolver_interest_rate: Optional[Decimal] = 6.0
    
    cash_sweep_percentage: Optional[Decimal] = 50.0
    
    # Equity Assumptions
    sponsor_equity: Optional[Decimal] = None
    management_rollover: Optional[Decimal] = 0
    other_equity: Optional[Decimal] = 0
    
    # Exit Assumptions
    exit_year: Optional[int] = 5
    exit_ebitda_multiple: Optional[Decimal] = None
    exit_enterprise_value: Optional[Decimal] = None
    exit_debt: Optional[Decimal] = None
    exit_cash: Optional[Decimal] = None
    
    # Operating Model Assumptions
    projection_years: Optional[int] = 5
    base_year_revenue: Optional[Decimal] = None
    revenue_growth_year1: Optional[Decimal] = None
    revenue_growth_year2: Optional[Decimal] = None
    revenue_growth_year3: Optional[Decimal] = None
    revenue_growth_year4: Optional[Decimal] = None
    revenue_growth_year5: Optional[Decimal] = None
    
    ebitda_margin_year1: Optional[Decimal] = None
    ebitda_margin_year2: Optional[Decimal] = None
    ebitda_margin_year3: Optional[Decimal] = None
    ebitda_margin_year4: Optional[Decimal] = None
    ebitda_margin_year5: Optional[Decimal] = None
    
    capex_percentage_revenue: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = 25.0
    nwc_percentage_revenue: Optional[Decimal] = 10.0
    da_percentage_revenue: Optional[Decimal] = 5.0

class AssumptionCreate(AssumptionBase):
    pass

class AssumptionUpdate(AssumptionBase):
    pass

class Assumption(AssumptionBase):
    id: int
    model_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# MODEL SCHEMAS
# ============================================================================

class ModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    company_name: Optional[str] = None

class ModelCreate(ModelBase):
    project_id: int

class Model(ModelBase):
    id: int
    project_id: int
    model_version: int
    created_at: datetime
    updated_at: datetime
    locked: bool
    
    class Config:
        from_attributes = True

# ============================================================================
# CALCULATION RESULT SCHEMAS
# ============================================================================

class OperatingProjectionData(BaseModel):
    year: int
    revenue: Decimal
    revenue_growth_pct: Decimal
    ebitda: Decimal
    ebitda_margin_pct: Decimal
    depreciation_amortization: Decimal
    ebit: Decimal
    interest_expense: Decimal
    ebt: Decimal
    tax_expense: Decimal
    net_income: Decimal
    accounts_receivable: Decimal
    inventory: Decimal
    accounts_payable: Decimal
    other_working_capital: Decimal
    capex: Decimal
    capex_pct_revenue: Decimal
    change_nwc: Decimal
    free_cash_flow: Decimal
    cash_available_for_debt_paydown: Decimal

class DebtScheduleData(BaseModel):
    instrument_name: str
    instrument_type: str
    year: int
    beginning_balance: Decimal
    mandatory_amortization: Decimal
    optional_repayment: Decimal
    draws: Decimal
    repayments: Decimal
    interest_rate: Decimal
    cash_interest_expense: Decimal
    ending_balance: Decimal

class SourcesUsesData(BaseModel):
    # USES
    purchase_equity: Decimal
    refinance_existing_debt: Decimal
    transaction_fees: Decimal
    financing_fees: Decimal
    other_uses: Decimal
    total_uses: Decimal
    
    # SOURCES
    senior_debt: Decimal
    subordinated_debt: Decimal
    revolver: Decimal
    sponsor_equity: Decimal
    management_rollover: Decimal
    other_equity: Decimal
    total_sources: Decimal
    
    # Metrics
    total_debt: Decimal
    debt_ebitda_multiple: Decimal
    equity_percentage: Decimal
    sources_uses_match: bool
    difference: Decimal

class ReturnsData(BaseModel):
    sponsor_initial_investment: Decimal
    sponsor_exit_equity_proceeds: Decimal
    sponsor_total_proceeds: Decimal
    moic: Decimal
    irr: Decimal
    total_profit: Decimal
    hold_period_years: Decimal
    ebitda_growth_contribution: Decimal
    multiple_expansion_contribution: Decimal
    debt_paydown_contribution: Decimal

class ExitAnalysisData(BaseModel):
    exit_year: int
    exit_ebitda: Decimal
    exit_ebitda_multiple: Decimal
    exit_enterprise_value: Decimal
    exit_debt: Decimal
    exit_cash: Decimal
    exit_equity_value: Decimal
    entry_enterprise_value: Decimal
    entry_ebitda: Decimal
    entry_ebitda_multiple: Decimal
    entry_debt: Decimal
    entry_cash: Decimal
    entry_equity_value: Decimal

class CalculationResults(BaseModel):
    model_id: int
    assumptions: Assumption
    operating_projections: List[OperatingProjectionData]
    debt_schedules: List[DebtScheduleData]
    sources_uses: SourcesUsesData
    exit_analysis: ExitAnalysisData
    returns: ReturnsData
    cash_flow_bridge: dict

# ============================================================================
# SENSITIVITY ANALYSIS SCHEMAS
# ============================================================================

class SensitivityResult(BaseModel):
    x_value: Decimal
    y_value: Decimal
    irr: Decimal
    moic: Decimal
    equity_value: Decimal

class SensitivityTableResult(BaseModel):
    sensitivity_type: str
    x_axis_label: str
    y_axis_label: str
    results: List[List[SensitivityResult]]

# ============================================================================
# SCENARIO SCHEMAS
# ============================================================================

class ScenarioBase(BaseModel):
    scenario_type: str
    name: str
    description: Optional[str] = None
    revenue_growth_adjustment: Optional[Decimal] = 0
    ebitda_margin_adjustment: Optional[Decimal] = 0
    capex_adjustment: Optional[Decimal] = 0
    working_capital_adjustment: Optional[Decimal] = 0
    interest_rate_adjustment: Optional[Decimal] = 0
    entry_multiple_adjustment: Optional[Decimal] = 0
    exit_multiple_adjustment: Optional[Decimal] = 0
    debt_level_adjustment: Optional[Decimal] = 0
    exit_year_override: Optional[int] = None

class ScenarioCreate(ScenarioBase):
    model_id: int

class Scenario(ScenarioBase):
    id: int
    model_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
