from decimal import Decimal
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime

class Validations:
    """Input validation for LBO model assumptions"""
    
    @staticmethod
    def validate_revenue(revenue: Decimal) -> Tuple[bool, str]:
        """Validate revenue is positive"""
        if revenue is None:
            return False, "Revenue cannot be empty"
        if revenue <= 0:
            return False, "Revenue must be positive"
        return True, ""
    
    @staticmethod
    def validate_multiple(multiple: Decimal, field_name: str) -> Tuple[bool, str]:
        """Validate EBITDA multiple is positive"""
        if multiple is None:
            return False, f"{field_name} cannot be empty"
        if multiple <= 0:
            return False, f"{field_name} must be positive"
        return True, ""
    
    @staticmethod
    def validate_percentage(value: Decimal, field_name: str, allow_zero: bool = True) -> Tuple[bool, str]:
        """Validate percentage is between 0 and 100"""
        if value is None:
            return False, f"{field_name} cannot be empty"
        if value < 0 or value > 100:
            return False, f"{field_name} must be between 0 and 100"
        if not allow_zero and value == 0:
            return False, f"{field_name} cannot be zero"
        return True, ""
    
    @staticmethod
    def validate_debt_not_negative(debt: Decimal, field_name: str) -> Tuple[bool, str]:
        """Validate debt is not negative"""
        if debt is None:
            debt = Decimal(0)
        if debt < 0:
            return False, f"{field_name} cannot be negative"
        return True, ""
    
    @staticmethod
    def validate_sources_uses_match(sources: Decimal, uses: Decimal, tolerance: Decimal = Decimal("0.01")) -> Tuple[bool, str]:
        """Validate sources equal uses (with small tolerance for rounding)"""
        difference = abs(sources - uses)
        if difference > tolerance:
            return False, f"Sources and Uses do not match. Difference: ${difference:,.2f}"
        return True, ""
    
    @staticmethod
    def validate_exit_year_logic(exit_year: int, projection_years: int) -> Tuple[bool, str]:
        """Validate exit year is within projection period"""
        if exit_year <= 0:
            return False, "Exit year must be positive"
        if exit_year > projection_years:
            return False, f"Exit year ({exit_year}) cannot exceed projection period ({projection_years} years)"
        return True, ""
    
    @staticmethod
    def validate_interest_rate(rate: Decimal, field_name: str) -> Tuple[bool, str]:
        """Validate interest rate is reasonable"""
        if rate is None:
            return False, f"{field_name} cannot be empty"
        if rate < 0 or rate > 50:
            return False, f"{field_name} must be between 0% and 50%"
        return True, ""

class OperatingModelCalculator:
    """Calculate operating projections (revenue, EBITDA, etc.)"""
    
    @staticmethod
    def calculate_projections(assumptions: Dict) -> List[Dict]:
        """
        Calculate 5-year (or custom) operating projections.
        
        Returns:
            List of dicts with year-by-year P&L items
        """
        projections = []
        base_revenue = float(assumptions.get('base_year_revenue', 0))
        projection_years = int(assumptions.get('projection_years', 5))
        
        previous_nwc = base_revenue * float(assumptions.get('nwc_percentage_revenue', 10)) / 100
        
        for year in range(1, projection_years + 1):
            # Get growth assumptions for this year
            growth_key = f'revenue_growth_year{year}'
            revenue_growth = float(assumptions.get(growth_key, 0)) / 100
            
            # Calculate revenue
            if year == 1:
                revenue = base_revenue * (1 + revenue_growth)
            else:
                revenue = projections[year - 2]['revenue'] * (1 + revenue_growth)
            
            # Get EBITDA margin for this year
            margin_key = f'ebitda_margin_year{year}'
            ebitda_margin = float(assumptions.get(margin_key, 0)) / 100
            ebitda = revenue * ebitda_margin
            
            # Calculate other P&L items
            da_pct = float(assumptions.get('da_percentage_revenue', 5)) / 100
            depreciation_amortization = revenue * da_pct
            ebit = ebitda - depreciation_amortization
            
            # Interest expense calculated in debt schedule
            interest_expense = Decimal(0)  # Will be populated after debt schedule
            ebt = ebit - float(interest_expense)
            
            tax_rate = float(assumptions.get('tax_rate', 25)) / 100
            tax_expense = max(ebt * tax_rate, 0)
            net_income = ebt - tax_expense
            
            # Working capital
            nwc_pct = float(assumptions.get('nwc_percentage_revenue', 10)) / 100
            current_nwc = revenue * nwc_pct
            change_nwc = current_nwc - previous_nwc
            previous_nwc = current_nwc
            
            # CapEx
            capex_pct = float(assumptions.get('capex_percentage_revenue', 5)) / 100
            capex = revenue * capex_pct
            
            # Free cash flow
            fcf = net_income + depreciation_amortization - capex - change_nwc
            
            # Cash available for debt paydown
            cash_available = ebitda - tax_expense - capex - change_nwc
            
            projections.append({
                'year': year,
                'revenue': round(revenue, 2),
                'revenue_growth_pct': round(revenue_growth * 100, 2),
                'ebitda': round(ebitda, 2),
                'ebitda_margin_pct': round(ebitda_margin * 100, 2),
                'depreciation_amortization': round(depreciation_amortization, 2),
                'ebit': round(ebit, 2),
                'interest_expense': 0,  # Will be updated after debt schedule
                'ebt': round(ebt, 2),
                'tax_expense': round(tax_expense, 2),
                'net_income': round(net_income, 2),
                'accounts_receivable': round(revenue * 0.1, 2),  # 10 days sales outstanding
                'inventory': round(revenue * 0.05, 2),  # 5% of revenue
                'accounts_payable': round(revenue * 0.08, 2),  # 8% of revenue
                'other_working_capital': round(revenue * 0.02, 2),  # 2% of revenue
                'capex': round(capex, 2),
                'capex_pct_revenue': round(capex_pct * 100, 2),
                'change_nwc': round(change_nwc, 2),
                'free_cash_flow': round(fcf, 2),
                'cash_available_for_debt_paydown': round(cash_available, 2)
            })
        
        return projections

class DebtScheduleCalculator:
    """Calculate debt schedules for all debt instruments"""
    
    @staticmethod
    def calculate_debt_schedules(assumptions: Dict, operating_projections: List[Dict]) -> List[Dict]:
        """
        Calculate year-by-year debt schedule for all instruments.
        
        Instruments:
        - Senior Term Loan: Mandatory amortization + optional repayment from cash sweep
        - Subordinated Debt: Similar structure
        - Revolver: Only interest until cash flow needs it or cash sweep pays it down
        """
        debt_schedules = []
        projection_years = len(operating_projections)
        
        # Define debt instruments
        debt_instruments = [
            {
                'name': 'Senior Term Loan',
                'type': 'senior_term_loan',
                'beginning_balance': float(assumptions.get('senior_debt_amount', 0)),
                'interest_rate': float(assumptions.get('senior_interest_rate', 5)) / 100,
                'amortization_rate': float(assumptions.get('senior_amortization_rate', 2)) / 100,
                'priority': 1
            },
            {
                'name': 'Subordinated Debt',
                'type': 'subordinated_debt',
                'beginning_balance': float(assumptions.get('subordinated_debt_amount', 0)),
                'interest_rate': float(assumptions.get('subordinated_interest_rate', 8)) / 100,
                'amortization_rate': float(assumptions.get('subordinated_amortization_rate', 1)) / 100,
                'priority': 2
            },
            {
                'name': 'Revolver',
                'type': 'revolver',
                'beginning_balance': 0,  # Typically starts undrawn
                'interest_rate': float(assumptions.get('revolver_interest_rate', 6)) / 100,
                'commitment': float(assumptions.get('revolver_commitment', 0)),
                'priority': 3
            }
        ]
        
        cash_sweep_pct = float(assumptions.get('cash_sweep_percentage', 50)) / 100
        min_cash = float(assumptions.get('min_cash_balance', 10000000))
        
        for year_idx, year_data in enumerate(operating_projections):
            year = year_idx + 1
            cash_available = year_data['cash_available_for_debt_paydown']
            optional_repayment_available = cash_available * cash_sweep_pct
            
            for instrument in debt_instruments:
                if year_idx == 0:
                    beginning_balance = instrument['beginning_balance']
                else:
                    # Get ending balance from previous year's schedule
                    prev_schedule = next(
                        (s for s in debt_schedules if s['year'] == year - 1 and s['instrument_name'] == instrument['name']),
                        None
                    )
                    beginning_balance = prev_schedule['ending_balance'] if prev_schedule else instrument['beginning_balance']
                
                # Calculate interest
                interest_rate = instrument['interest_rate']
                cash_interest = beginning_balance * interest_rate
                
                # Calculate mandatory amortization
                if instrument['type'] == 'revolver':
                    mandatory_amortization = 0
                else:
                    mandatory_amortization = beginning_balance * instrument['amortization_rate']
                
                # Calculate optional repayment (from cash sweep)
                # Allocate based on priority: Senior first, then Sub, then Revolver
                optional_repayment = 0
                if optional_repayment_available > 0:
                    if instrument['priority'] == 1:  # Senior gets first priority
                        repayment_to_senior = min(optional_repayment_available, beginning_balance - mandatory_amortization)
                        optional_repayment = repayment_to_senior
                        optional_repayment_available -= repayment_to_senior
                    elif instrument['priority'] == 2:  # Then subordinated
                        repayment_to_sub = min(optional_repayment_available, beginning_balance - mandatory_amortization)
                        optional_repayment = repayment_to_sub
                        optional_repayment_available -= repayment_to_sub
                
                # Calculate ending balance (cannot go negative)
                total_repayment = mandatory_amortization + optional_repayment
                ending_balance = max(beginning_balance - total_repayment, 0)
                
                debt_schedules.append({
                    'instrument_name': instrument['name'],
                    'instrument_type': instrument['type'],
                    'year': year,
                    'beginning_balance': round(beginning_balance, 2),
                    'mandatory_amortization': round(mandatory_amortization, 2),
                    'optional_repayment': round(optional_repayment, 2),
                    'draws': 0,  # Revolver draws handled separately
                    'repayments': 0,  # Revolver repayments handled separately
                    'interest_rate': round(interest_rate * 100, 3),
                    'cash_interest_expense': round(cash_interest, 2),
                    'ending_balance': round(ending_balance, 2)
                })
        
        return debt_schedules

class CashFlowCalculator:
    """Calculate cash flow bridge with clear component breakdown"""
    
    @staticmethod
    def calculate_cash_flow_bridge(operating_projections: List[Dict], debt_schedules: List[Dict]) -> List[Dict]:
        """
        Calculate cash flow bridge:
        Net Income + D&A - CapEx - ΔNW C = Free Cash Flow
        Free Cash Flow - Mandatory Amortization - Optional Repayment = Change in Cash
        """
        bridge = []
        
        for proj in operating_projections:
            year = proj['year']
            
            # Get total interest expense and total debt amortization for this year
            year_debt_schedules = [d for d in debt_schedules if d['year'] == year]
            total_interest = sum(d['cash_interest_expense'] for d in year_debt_schedules)
            total_mandatory = sum(d['mandatory_amortization'] for d in year_debt_schedules)
            total_optional = sum(d['optional_repayment'] for d in year_debt_schedules)
            
            # Update interest in operating projection
            net_income = proj['net_income']
            da = proj['depreciation_amortization']
            capex = proj['capex']
            change_nwc = proj['change_nwc']
            
            free_cash_flow = net_income + da - capex - change_nwc
            change_in_cash = free_cash_flow - total_mandatory - total_optional
            
            bridge.append({
                'year': year,
                'net_income': round(net_income, 2),
                'add_depreciation_amortization': round(da, 2),
                'subtract_capex': round(capex, 2),
                'subtract_change_nwc': round(change_nwc, 2),
                'free_cash_flow': round(free_cash_flow, 2),
                'subtract_mandatory_amortization': round(total_mandatory, 2),
                'subtract_optional_repayment': round(total_optional, 2),
                'change_in_cash': round(change_in_cash, 2)
            })
        
        return bridge

class SourcesUsesCalculator:
    """Calculate Sources and Uses of funds"""
    
    @staticmethod
    def calculate_sources_uses(assumptions: Dict) -> Dict:
        """
        Build Sources & Uses table:
        
        USES: Purchase Equity + Refinance Debt + Fees + Other
        SOURCES: All debt + All equity
        
        Validation: Sources must equal Uses
        """
        entry_ev = float(assumptions.get('entry_enterprise_value', 0))
        entry_ebitda = float(assumptions.get('entry_ebitda', 0))
        entry_multiple = float(assumptions.get('entry_ebitda_multiple', 0))
        
        # Calculate entry EV if missing
        if entry_ev == 0 and entry_ebitda > 0 and entry_multiple > 0:
            entry_ev = entry_ebitda * entry_multiple
        
        existing_debt = float(assumptions.get('existing_debt', 0))
        existing_cash = float(assumptions.get('existing_cash', 0))
        transaction_fees = float(assumptions.get('transaction_fees', 0))
        financing_fees = float(assumptions.get('financing_fees', 0))
        
        # USES
        purchase_equity = entry_ev - existing_debt + existing_cash  # Purchase price less assumed debt
        refinance_existing_debt = existing_debt
        total_uses = purchase_equity + refinance_existing_debt + transaction_fees + financing_fees
        
        # SOURCES
        senior_debt = float(assumptions.get('senior_debt_amount', 0))
        if senior_debt == 0 and entry_ebitda > 0:
            # Calculate from multiple if not provided
            senior_multiple = float(assumptions.get('senior_debt_ebitda_multiple', 3))
            senior_debt = entry_ebitda * senior_multiple
        
        subordinated_debt = float(assumptions.get('subordinated_debt_amount', 0))
        if subordinated_debt == 0 and entry_ebitda > 0:
            sub_multiple = float(assumptions.get('subordinated_debt_ebitda_multiple', 1.5))
            subordinated_debt = entry_ebitda * sub_multiple
        
        sponsor_equity = float(assumptions.get('sponsor_equity', 0))
        management_rollover = float(assumptions.get('management_rollover', 0))
        other_equity = float(assumptions.get('other_equity', 0))
        
        revolver = float(assumptions.get('revolver_commitment', 0))
        
        total_sources = senior_debt + subordinated_debt + revolver + sponsor_equity + management_rollover + other_equity
        
        # Calculate metrics
        total_debt = senior_debt + subordinated_debt
        debt_ebitda = total_debt / entry_ebitda if entry_ebitda > 0 else 0
        total_equity = sponsor_equity + management_rollover + other_equity
        total_cap = total_debt + total_equity
        equity_pct = (total_equity / total_cap * 100) if total_cap > 0 else 0
        
        difference = abs(total_sources - total_uses)
        sources_match = difference < 0.01  # Small tolerance for rounding
        
        return {
            # USES
            'purchase_equity': round(purchase_equity, 2),
            'refinance_existing_debt': round(refinance_existing_debt, 2),
            'transaction_fees': round(transaction_fees, 2),
            'financing_fees': round(financing_fees, 2),
            'other_uses': 0,
            'total_uses': round(total_uses, 2),
            
            # SOURCES
            'senior_debt': round(senior_debt, 2),
            'subordinated_debt': round(subordinated_debt, 2),
            'revolver': round(revolver, 2),
            'sponsor_equity': round(sponsor_equity, 2),
            'management_rollover': round(management_rollover, 2),
            'other_equity': round(other_equity, 2),
            'total_sources': round(total_sources, 2),
            
            # METRICS
            'total_debt': round(total_debt, 2),
            'debt_ebitda_multiple': round(debt_ebitda, 2),
            'equity_percentage': round(equity_pct, 2),
            'sources_uses_match': sources_match,
            'difference': round(difference, 2)
        }

class ExitAnalysisCalculator:
    """Calculate exit scenario analysis"""
    
    @staticmethod
    def calculate_exit(assumptions: Dict, operating_projections: List[Dict], debt_schedules: List[Dict]) -> Dict:
        """
        Calculate exit analysis for specified exit year.
        
        Exit EV = Exit EBITDA × Exit Multiple
        Exit Equity Value = Exit EV - Exit Debt + Exit Cash
        """
        exit_year = int(assumptions.get('exit_year', 5))
        entry_ev = float(assumptions.get('entry_enterprise_value', 0))
        entry_ebitda = float(assumptions.get('entry_ebitda', 0))
        entry_multiple = float(assumptions.get('entry_ebitda_multiple', 0))
        existing_cash = float(assumptions.get('existing_cash', 0))
        
        # Recalculate entry EV if needed
        if entry_ev == 0 and entry_ebitda > 0 and entry_multiple > 0:
            entry_ev = entry_ebitda * entry_multiple
        
        # Get exit year EBITDA from projections
        exit_proj = next((p for p in operating_projections if p['year'] == exit_year), None)
        if not exit_proj:
            exit_ebitda = 0
        else:
            exit_ebitda = float(exit_proj['ebitda'])
        
        # Get exit multiple
        exit_multiple = float(assumptions.get('exit_ebitda_multiple', entry_multiple))
        
        # Calculate exit EV
        exit_ev = exit_ebitda * exit_multiple if exit_ebitda > 0 else 0
        
        # Get exit debt from debt schedules
        exit_debt_schedules = [d for d in debt_schedules if d['year'] == exit_year]
        exit_debt = sum(d['ending_balance'] for d in exit_debt_schedules)
        
        # Get exit cash (often assumed at entry level or specified)
        exit_cash = float(assumptions.get('exit_cash', existing_cash))
        
        # Calculate exit equity value
        exit_equity_value = exit_ev - exit_debt + exit_cash
        
        return {
            'exit_year': exit_year,
            'exit_ebitda': round(exit_ebitda, 2),
            'exit_ebitda_multiple': round(exit_multiple, 2),
            'exit_enterprise_value': round(exit_ev, 2),
            'exit_debt': round(exit_debt, 2),
            'exit_cash': round(exit_cash, 2),
            'exit_equity_value': round(exit_equity_value, 2),
            'entry_enterprise_value': round(entry_ev, 2),
            'entry_ebitda': round(entry_ebitda, 2),
            'entry_ebitda_multiple': round(entry_multiple, 2),
            'entry_debt': sum(float(assumptions.get(f'{x}_amount', 0)) for x in ['senior_debt', 'subordinated_debt']),
            'entry_cash': round(existing_cash, 2),
            'entry_equity_value': round(entry_ev - sum(float(assumptions.get(f'{x}_amount', 0)) for x in ['senior_debt', 'subordinated_debt']) + existing_cash, 2)
        }
