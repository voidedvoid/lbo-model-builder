from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, DECIMAL, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# ============================================================================
# USER AND PROJECT MODELS
# ============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="projects")
    models = relationship("Model", back_populates="project", cascade="all, delete-orphan")

# ============================================================================
# MODEL
# ============================================================================

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    name = Column(String(255))
    description = Column(Text)
    company_name = Column(String(255))
    model_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    locked = Column(Boolean, default=False)
    
    project = relationship("Project", back_populates="models")
    assumptions = relationship("Assumptions", back_populates="model", cascade="all, delete-orphan")
    operating_projections = relationship("OperatingProjection", back_populates="model", cascade="all, delete-orphan")
    debt_instruments = relationship("DebtInstrument", back_populates="model", cascade="all, delete-orphan")
    debt_schedules = relationship("DebtSchedule", back_populates="model", cascade="all, delete-orphan")
    sources_uses = relationship("SourcesUses", back_populates="model", cascade="all, delete-orphan")
    exit_analysis = relationship("ExitAnalysis", back_populates="model", cascade="all, delete-orphan")
    returns_analysis = relationship("ReturnsAnalysis", back_populates="model", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="model", cascade="all, delete-orphan")
    sensitivity_analysis = relationship("SensitivityAnalysis", back_populates="model", cascade="all, delete-orphan")
    cash_flow_bridge = relationship("CashFlowBridge", back_populates="model", cascade="all, delete-orphan")
    model_versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

# ============================================================================
# ASSUMPTIONS
# ============================================================================

class Assumptions(Base):
    __tablename__ = "assumptions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    
    # Transaction Assumptions
    entry_enterprise_value = Column(DECIMAL(15, 2))
    entry_ebitda = Column(DECIMAL(15, 2))
    entry_ebitda_multiple = Column(DECIMAL(10, 2))
    existing_debt = Column(DECIMAL(15, 2), default=0)
    existing_cash = Column(DECIMAL(15, 2), default=0)
    transaction_fees = Column(DECIMAL(15, 2), default=0)
    financing_fees = Column(DECIMAL(15, 2), default=0)
    min_cash_balance = Column(DECIMAL(15, 2), default=10000000)
    
    # Financing Assumptions
    senior_debt_amount = Column(DECIMAL(15, 2))
    senior_debt_ebitda_multiple = Column(DECIMAL(10, 2))
    senior_interest_rate = Column(DECIMAL(6, 3), default=5.0)
    senior_amortization_rate = Column(DECIMAL(6, 3), default=2.0)
    
    subordinated_debt_amount = Column(DECIMAL(15, 2))
    subordinated_debt_ebitda_multiple = Column(DECIMAL(10, 2))
    subordinated_interest_rate = Column(DECIMAL(6, 3), default=8.0)
    subordinated_amortization_rate = Column(DECIMAL(6, 3), default=1.0)
    
    revolver_commitment = Column(DECIMAL(15, 2))
    revolver_interest_rate = Column(DECIMAL(6, 3), default=6.0)
    
    cash_sweep_percentage = Column(DECIMAL(5, 2), default=50.0)
    
    # Equity Assumptions
    sponsor_equity = Column(DECIMAL(15, 2))
    management_rollover = Column(DECIMAL(15, 2), default=0)
    other_equity = Column(DECIMAL(15, 2), default=0)
    
    # Exit Assumptions
    exit_year = Column(Integer, default=5)
    exit_ebitda_multiple = Column(DECIMAL(10, 2))
    exit_enterprise_value = Column(DECIMAL(15, 2))
    exit_debt = Column(DECIMAL(15, 2))
    exit_cash = Column(DECIMAL(15, 2))
    
    # Operating Model Assumptions
    projection_years = Column(Integer, default=5)
    base_year_revenue = Column(DECIMAL(15, 2))
    revenue_growth_year1 = Column(DECIMAL(6, 3))
    revenue_growth_year2 = Column(DECIMAL(6, 3))
    revenue_growth_year3 = Column(DECIMAL(6, 3))
    revenue_growth_year4 = Column(DECIMAL(6, 3))
    revenue_growth_year5 = Column(DECIMAL(6, 3))
    
    ebitda_margin_year1 = Column(DECIMAL(6, 3))
    ebitda_margin_year2 = Column(DECIMAL(6, 3))
    ebitda_margin_year3 = Column(DECIMAL(6, 3))
    ebitda_margin_year4 = Column(DECIMAL(6, 3))
    ebitda_margin_year5 = Column(DECIMAL(6, 3))
    
    capex_percentage_revenue = Column(DECIMAL(6, 3))
    tax_rate = Column(DECIMAL(6, 3), default=25.0)
    nwc_percentage_revenue = Column(DECIMAL(6, 3), default=10.0)
    da_percentage_revenue = Column(DECIMAL(6, 3), default=5.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    model = relationship("Model", back_populates="assumptions")

# ============================================================================
# OPERATING PROJECTIONS
# ============================================================================

class OperatingProjection(Base):
    __tablename__ = "operating_projections"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    year = Column(Integer)
    
    # Income Statement
    revenue = Column(DECIMAL(15, 2))
    revenue_growth_pct = Column(DECIMAL(6, 3))
    ebitda = Column(DECIMAL(15, 2))
    ebitda_margin_pct = Column(DECIMAL(6, 3))
    depreciation_amortization = Column(DECIMAL(15, 2))
    ebit = Column(DECIMAL(15, 2))
    interest_expense = Column(DECIMAL(15, 2))
    ebt = Column(DECIMAL(15, 2))
    tax_expense = Column(DECIMAL(15, 2))
    net_income = Column(DECIMAL(15, 2))
    
    # Balance Sheet Items
    accounts_receivable = Column(DECIMAL(15, 2))
    inventory = Column(DECIMAL(15, 2))
    accounts_payable = Column(DECIMAL(15, 2))
    other_working_capital = Column(DECIMAL(15, 2))
    
    # Cash Flow
    capex = Column(DECIMAL(15, 2))
    capex_pct_revenue = Column(DECIMAL(6, 3))
    change_nwc = Column(DECIMAL(15, 2))
    free_cash_flow = Column(DECIMAL(15, 2))
    
    # Cash Available for Debt Paydown
    cash_available_for_debt_paydown = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="operating_projections")

# ============================================================================
# DEBT INSTRUMENTS
# ============================================================================

class DebtInstrument(Base):
    __tablename__ = "debt_instruments"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    instrument_type = Column(String(50))  # 'senior_term_loan', 'subordinated_debt', 'revolver'
    name = Column(String(255))
    
    initial_balance = Column(DECIMAL(15, 2))
    interest_rate = Column(DECIMAL(6, 3))
    amortization_rate = Column(DECIMAL(6, 3))
    repayment_priority = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    model = relationship("Model", back_populates="debt_instruments")
    debt_schedules = relationship("DebtSchedule", back_populates="debt_instrument", cascade="all, delete-orphan")

# ============================================================================
# DEBT SCHEDULES
# ============================================================================

class DebtSchedule(Base):
    __tablename__ = "debt_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    debt_instrument_id = Column(Integer, ForeignKey("debt_instruments.id"), index=True)
    year = Column(Integer)
    
    beginning_balance = Column(DECIMAL(15, 2))
    mandatory_amortization = Column(DECIMAL(15, 2))
    optional_repayment = Column(DECIMAL(15, 2))
    draws = Column(DECIMAL(15, 2), default=0)
    repayments = Column(DECIMAL(15, 2), default=0)
    interest_rate = Column(DECIMAL(6, 3))
    cash_interest_expense = Column(DECIMAL(15, 2))
    ending_balance = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="debt_schedules")
    debt_instrument = relationship("DebtInstrument", back_populates="debt_schedules")

# ============================================================================
# SOURCES & USES
# ============================================================================

class SourcesUses(Base):
    __tablename__ = "sources_uses"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    
    # USES
    purchase_equity = Column(DECIMAL(15, 2))
    refinance_existing_debt = Column(DECIMAL(15, 2))
    transaction_fees = Column(DECIMAL(15, 2))
    financing_fees = Column(DECIMAL(15, 2))
    other_uses = Column(DECIMAL(15, 2), default=0)
    total_uses = Column(DECIMAL(15, 2))
    
    # SOURCES
    senior_debt = Column(DECIMAL(15, 2))
    subordinated_debt = Column(DECIMAL(15, 2))
    revolver = Column(DECIMAL(15, 2))
    sponsor_equity = Column(DECIMAL(15, 2))
    management_rollover = Column(DECIMAL(15, 2))
    other_equity = Column(DECIMAL(15, 2))
    total_sources = Column(DECIMAL(15, 2))
    
    # Metrics
    total_debt = Column(DECIMAL(15, 2))
    debt_ebitda_multiple = Column(DECIMAL(10, 2))
    equity_percentage = Column(DECIMAL(6, 3))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="sources_uses")

# ============================================================================
# EXIT ANALYSIS
# ============================================================================

class ExitAnalysis(Base):
    __tablename__ = "exit_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    exit_year = Column(Integer)
    
    exit_ebitda = Column(DECIMAL(15, 2))
    exit_ebitda_multiple = Column(DECIMAL(10, 2))
    exit_enterprise_value = Column(DECIMAL(15, 2))
    exit_debt = Column(DECIMAL(15, 2))
    exit_cash = Column(DECIMAL(15, 2))
    exit_equity_value = Column(DECIMAL(15, 2))
    
    entry_enterprise_value = Column(DECIMAL(15, 2))
    entry_ebitda = Column(DECIMAL(15, 2))
    entry_ebitda_multiple = Column(DECIMAL(10, 2))
    entry_debt = Column(DECIMAL(15, 2))
    entry_cash = Column(DECIMAL(15, 2))
    entry_equity_value = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="exit_analysis")

# ============================================================================
# RETURNS ANALYSIS
# ============================================================================

class ReturnsAnalysis(Base):
    __tablename__ = "returns_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    
    sponsor_initial_investment = Column(DECIMAL(15, 2))
    management_rollover_investment = Column(DECIMAL(15, 2))
    total_sponsor_investment = Column(DECIMAL(15, 2))
    
    sponsor_exit_equity_proceeds = Column(DECIMAL(15, 2))
    cumulative_distributions = Column(DECIMAL(15, 2), default=0)
    sponsor_total_proceeds = Column(DECIMAL(15, 2))
    
    moic = Column(DECIMAL(10, 3))
    irr = Column(DECIMAL(6, 3))
    total_profit = Column(DECIMAL(15, 2))
    hold_period_years = Column(DECIMAL(5, 1))
    
    ebitda_growth_contribution = Column(DECIMAL(15, 2))
    multiple_expansion_contribution = Column(DECIMAL(15, 2))
    debt_paydown_contribution = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="returns_analysis")

# ============================================================================
# SCENARIOS
# ============================================================================

class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    scenario_type = Column(String(50))  # 'base', 'downside', 'upside', 'custom'
    name = Column(String(255))
    description = Column(Text)
    
    revenue_growth_adjustment = Column(DECIMAL(6, 3), default=0)
    ebitda_margin_adjustment = Column(DECIMAL(6, 3), default=0)
    capex_adjustment = Column(DECIMAL(6, 3), default=0)
    working_capital_adjustment = Column(DECIMAL(6, 3), default=0)
    interest_rate_adjustment = Column(DECIMAL(6, 3), default=0)
    entry_multiple_adjustment = Column(DECIMAL(6, 3), default=0)
    exit_multiple_adjustment = Column(DECIMAL(6, 3), default=0)
    debt_level_adjustment = Column(DECIMAL(6, 3), default=0)
    exit_year_override = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    model = relationship("Model", back_populates="scenarios")

# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

class SensitivityAnalysis(Base):
    __tablename__ = "sensitivity_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    sensitivity_type = Column(String(100))
    
    x_axis_label = Column(String(100))
    y_axis_label = Column(String(100))
    x_value = Column(DECIMAL(10, 3))
    y_value = Column(DECIMAL(10, 3))
    
    irr = Column(DECIMAL(6, 3))
    moic = Column(DECIMAL(10, 3))
    equity_value = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="sensitivity_analysis")

# ============================================================================
# CASH FLOW BRIDGE
# ============================================================================

class CashFlowBridge(Base):
    __tablename__ = "cash_flow_bridge"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    year = Column(Integer)
    
    net_income = Column(DECIMAL(15, 2))
    add_depreciation_amortization = Column(DECIMAL(15, 2))
    subtract_capex = Column(DECIMAL(15, 2))
    subtract_change_nwc = Column(DECIMAL(15, 2))
    free_cash_flow = Column(DECIMAL(15, 2))
    
    subtract_mandatory_amortization = Column(DECIMAL(15, 2))
    subtract_optional_repayment = Column(DECIMAL(15, 2))
    change_in_cash = Column(DECIMAL(15, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    model = relationship("Model", back_populates="cash_flow_bridge")

# ============================================================================
# MODEL VERSIONS
# ============================================================================

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), index=True)
    version_number = Column(Integer)
    assumptions_json = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    
    model = relationship("Model", back_populates="model_versions")
