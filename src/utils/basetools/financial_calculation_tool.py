# utils/basetools/financial_calculation_tool.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import re

class FinancialBreakdown(BaseModel):
    """Financial breakdown for a scholarship option"""
    scholarship_name: str = Field(..., description="Name of the scholarship")
    university: str = Field(..., description="University name")
    program_field: str = Field(..., description="Field of study")
    
    # Costs
    annual_tuition: float = Field(..., description="Annual tuition fee in USD")
    program_duration_years: int = Field(..., description="Program duration in years")
    total_tuition: float = Field(..., description="Total tuition cost")
    
    # Financial aid
    scholarship_amount_annual: float = Field(..., description="Annual scholarship amount")
    scholarship_total: float = Field(..., description="Total scholarship amount")
    government_aid_annual: float = Field(..., description="Annual government aid available")
    government_loan_annual: float = Field(..., description="Annual government loan available")
    
    # Net costs
    net_annual_cost: float = Field(..., description="Net annual cost after all aid")
    total_net_cost: float = Field(..., description="Total net cost for entire program")
    
    # Additional estimates
    estimated_living_cost_annual: float = Field(..., description="Estimated annual living costs")
    total_estimated_cost: float = Field(..., description="Total estimated cost including living")

class FinancialCalculationInput(BaseModel):
    """Input for financial calculation"""
    matched_scholarships: List[Dict[str, Any]] = Field(..., description="List of matched scholarships")
    student_profile: Dict[str, Any] = Field(..., description="Student profile information")
    search_results: List[str] = Field(..., description="Additional search results for financial information")

class FinancialCalculationOutput(BaseModel):
    """Output with financial calculations"""
    financial_breakdowns: List[FinancialBreakdown] = Field(..., description="Financial breakdown for each scholarship")
    best_financial_options: List[FinancialBreakdown] = Field(..., description="Top 3 most affordable options")
    financial_summary: str = Field(..., description="Summary of financial analysis")
    funding_recommendations: List[str] = Field(..., description="Recommendations for funding strategies")

def financial_calculation_tool(input: FinancialCalculationInput) -> FinancialCalculationOutput:
    """
    Calculate detailed financial breakdown for each matched scholarship,
    including tuition, aid, loans, and living costs.
    """
    breakdowns = []
    
    for scholarship in input.matched_scholarships:
        breakdown = _calculate_individual_breakdown(
            scholarship, 
            input.student_profile, 
            input.search_results
        )
        if breakdown:
            breakdowns.append(breakdown)
    
    # Sort by total net cost (lowest first)
    breakdowns.sort(key=lambda x: x.total_net_cost)
    
    # Get best financial options (top 3 most affordable)
    best_options = breakdowns[:3]
    
    # Generate summary and recommendations
    summary = _generate_financial_summary(breakdowns)
    recommendations = _generate_funding_recommendations(breakdowns, input.student_profile)
    
    return FinancialCalculationOutput(
        financial_breakdowns=breakdowns,
        best_financial_options=best_options,
        financial_summary=summary,
        funding_recommendations=recommendations
    )

def _calculate_individual_breakdown(scholarship: Dict[str, Any], student: Dict[str, Any], search_results: List[str]) -> Optional[FinancialBreakdown]:
    """Calculate financial breakdown for individual scholarship"""
    try:
        # Extract basic information
        scholarship_name = scholarship.get('scholarship_name', 'Unknown Scholarship')
        university = scholarship.get('university', 'Unknown University')
        field = student.get('target_field', 'Unknown Field')
        target_location = student.get('target_location', 'Unknown Location')
        
        # Get tuition information
        annual_tuition = _extract_tuition_cost(university, field, target_location, search_results)
        program_duration = _estimate_program_duration(student.get('academic_level', 'undergraduate'))
        total_tuition = annual_tuition * program_duration
        
        # Calculate scholarship amounts
        scholarship_annual, scholarship_total = _calculate_scholarship_amounts(
            scholarship.get('scholarship_amount', ''), 
            annual_tuition, 
            program_duration
        )
        
        # Get government aid information
        gov_aid_annual, gov_loan_annual = _extract_government_aid(target_location, search_results)
        
        # Calculate net costs
        total_annual_aid = scholarship_annual + gov_aid_annual + gov_loan_annual
        net_annual_cost = max(0, annual_tuition - total_annual_aid)
        total_net_cost = net_annual_cost * program_duration
        
        # Estimate living costs
        living_cost_annual = _estimate_living_costs(target_location)
        total_estimated_cost = total_net_cost + (living_cost_annual * program_duration)
        
        return FinancialBreakdown(
            scholarship_name=scholarship_name,
            university=university,
            program_field=field,
            annual_tuition=annual_tuition,
            program_duration_years=program_duration,
            total_tuition=total_tuition,
            scholarship_amount_annual=scholarship_annual,
            scholarship_total=scholarship_total,
            government_aid_annual=gov_aid_annual,
            government_loan_annual=gov_loan_annual,
            net_annual_cost=net_annual_cost,
            total_net_cost=total_net_cost,
            estimated_living_cost_annual=living_cost_annual,
            total_estimated_cost=total_estimated_cost
        )
    
    except Exception as e:
        print(f"Error calculating breakdown for {scholarship.get('scholarship_name', 'Unknown')}: {e}")
        return None

def _extract_tuition_cost(university: str, field: str, location: str, search_results: List[str]) -> float:
    """Extract tuition cost from search results or estimate"""
    
    # Search for tuition information in search results
    for result in search_results:
        tuition = _parse_tuition_from_text(result, university, field)
        if tuition > 0:
            return tuition
    
    # Fallback to estimates by location and field
    return _estimate_tuition_by_location_and_field(location, field)

def _parse_tuition_from_text(text: str, university: str, field: str) -> float:
    """Parse tuition cost from text"""
    text_lower = text.lower()
    university_lower = university.lower()
    
    # Only consider results that mention the university
    if university_lower not in text_lower:
        return 0
    
    # Look for tuition patterns
    tuition_patterns = [
        r'tuition[:\s]*\$?([0-9,]+)(?:\s*per\s*year)?',
        r'annual\s*tuition[:\s]*\$?([0-9,]+)',
        r'yearly\s*fee[:\s]*\$?([0-9,]+)',
        r'cost\s*per\s*year[:\s]*\$?([0-9,]+)',
        r'\$([0-9,]+)\s*per\s*year',
        r'\$([0-9,]+)\s*annually'
    ]
    
    for pattern in tuition_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                # Remove commas and convert to float
                cost = float(match.replace(',', ''))
                # Filter reasonable tuition ranges (5K to 100K USD)
                if 5000 <= cost <= 100000:
                    return cost
            except ValueError:
                continue
    
    return 0

def _estimate_tuition_by_location_and_field(location: str, field: str) -> float:
    """Estimate tuition based on location and field"""
    location_lower = location.lower()
    field_lower = field.lower()
    
    # Base tuition by location/country
    base_tuition = {
        'usa': 35000,
        'united states': 35000,
        'canada': 25000,
        'uk': 30000,
        'united kingdom': 30000,
        'australia': 28000,
        'germany': 8000,
        'netherlands': 12000,
        'france': 10000,
        'singapore': 20000,
        'japan': 15000,
        'south korea': 12000
    }
    
    # Get base tuition
    tuition = 25000  # Default
    for country, cost in base_tuition.items():
        if country in location_lower:
            tuition = cost
            break
    
    # Adjust for field
    field_multipliers = {
        'medicine': 1.5,
        'medical': 1.5,
        'law': 1.3,
        'business': 1.2,
        'mba': 1.4,
        'engineering': 1.1,
        'computer science': 1.1,
        'arts': 0.9,
        'humanities': 0.9,
        'education': 0.8
    }
    
    for field_key, multiplier in field_multipliers.items():
        if field_key in field_lower:
            tuition *= multiplier
            break
    
    return round(tuition, 2)

def _estimate_program_duration(academic_level: str) -> int:
    """Estimate program duration based on academic level"""
    level_duration = {
        'undergraduate': 4,
        'bachelor': 4,
        'graduate': 2,
        'master': 2,
        'mba': 2,
        'doctorate': 4,
        'phd': 4
    }
    
    for level, duration in level_duration.items():
        if level in academic_level.lower():
            return duration
    
    return 4  # Default to undergraduate

def _calculate_scholarship_amounts(scholarship_amount_text: str, annual_tuition: float, duration: int) -> tuple:
    """Calculate annual and total scholarship amounts"""
    amount_text_lower = scholarship_amount_text.lower()
    
    # Full tuition coverage
    if any(keyword in amount_text_lower for keyword in ['full tuition', 'full scholarship', '100%']):
        return annual_tuition, annual_tuition * duration
    
    # Percentage coverage
    percentage_match = re.search(r'(\d+)%', amount_text_lower)
    if percentage_match:
        percentage = float(percentage_match.group(1)) / 100
        annual_amount = annual_tuition * percentage
        return annual_amount, annual_amount * duration
    
    # Specific dollar amounts
    dollar_patterns = [
        r'\$([0-9,]+)\s*per\s*year',
        r'\$([0-9,]+)\s*annually',
        r'up to\s*\$([0-9,]+)',
        r'\$([0-9,]+)'
    ]
    
    for pattern in dollar_patterns:
        match = re.search(pattern, amount_text_lower)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
                if amount <= annual_tuition:  # Reasonable check
                    return amount, amount * duration
            except ValueError:
                continue
    
    # Default: assume 50% coverage if amount not specified
    default_annual = annual_tuition * 0.5
    return default_annual, default_annual * duration

def _extract_government_aid(location: str, search_results: List[str]) -> tuple:
    """Extract government aid and loan information"""
    location_lower = location.lower()
    
    # Search in results first
    for result in search_results:
        aid, loan = _parse_government_aid_from_text(result, location)
        if aid > 0 or loan > 0:
            return aid, loan
    
    # Fallback to estimates
    return _estimate_government_aid_by_location(location)

def _parse_government_aid_from_text(text: str, location: str) -> tuple:
    """Parse government aid information from text"""
    text_lower = text.lower()
    
    # Look for aid patterns
    aid_patterns = [
        r'government\s*aid[:\s]*\$?([0-9,]+)',
        r'federal\s*aid[:\s]*\$?([0-9,]+)',
        r'grant[:\s]*\$?([0-9,]+)',
        r'pell\s*grant[:\s]*\$?([0-9,]+)'
    ]
    
    loan_patterns = [
        r'student\s*loan[:\s]*\$?([0-9,]+)',
        r'government\s*loan[:\s]*\$?([0-9,]+)',
        r'federal\s*loan[:\s]*\$?([0-9,]+)'
    ]
    
    aid_amount = 0
    loan_amount = 0
    
    for pattern in aid_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                aid_amount = max(aid_amount, float(match.group(1).replace(',', '')))
            except ValueError:
                continue
    
    for pattern in loan_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                loan_amount = max(loan_amount, float(match.group(1).replace(',', '')))
            except ValueError:
                continue
    
    return aid_amount, loan_amount

def _estimate_government_aid_by_location(location: str) -> tuple:
    """Estimate government aid based on location"""
    location_lower = location.lower()
    
    # Government aid estimates by country
    aid_estimates = {
        'usa': (6000, 12000),  # Pell Grant, Federal loans
        'united states': (6000, 12000),
        'canada': (3000, 8000),  # Provincial grants, OSAP
        'uk': (0, 10000),  # Student loans
        'australia': (0, 7000),  # HECS-HELP
        'germany': (500, 5000),  # BAföG
        'france': (400, 4000),
        'netherlands': (300, 6000)
    }
    
    for country, (aid, loan) in aid_estimates.items():
        if country in location_lower:
            return aid, loan
    
    return 0, 0  # No government aid available

def _estimate_living_costs(location: str) -> float:
    """Estimate annual living costs by location"""
    location_lower = location.lower()
    
    # Living cost estimates by location
    living_costs = {
        'usa': 15000,
        'united states': 15000,
        'new york': 20000,
        'california': 18000,
        'canada': 12000,
        'toronto': 15000,
        'vancouver': 16000,
        'uk': 12000,
        'london': 15000,
        'australia': 18000,
        'sydney': 20000,
        'melbourne': 18000,
        'germany': 10000,
        'berlin': 12000,
        'munich': 14000,
        'france': 9000,
        'paris': 12000,
        'netherlands': 11000,
        'amsterdam': 13000,
        'singapore': 14000,
        'japan': 12000,
        'tokyo': 15000
    }
    
    # Check for specific cities first, then countries
    for place, cost in sorted(living_costs.items(), key=len, reverse=True):
        if place in location_lower:
            return cost
    
    return 12000  # Default

def _generate_financial_summary(breakdowns: List[FinancialBreakdown]) -> str:
    """Generate summary of financial analysis"""
    if not breakdowns:
        return "No financial information available for the scholarships."
    
    summary_parts = []
    
    # Overall statistics
    avg_net_cost = sum(b.total_net_cost for b in breakdowns) / len(breakdowns)
    min_cost = min(b.total_net_cost for b in breakdowns)
    max_cost = max(b.total_net_cost for b in breakdowns)
    
    summary_parts.append(f"Analyzed {len(breakdowns)} scholarship options.")
    summary_parts.append(f"Net costs range from ${min_cost:,.0f} to ${max_cost:,.0f} for the complete program.")
    summary_parts.append(f"Average net cost: ${avg_net_cost:,.0f}.")
    
    # Best options
    fully_funded = [b for b in breakdowns if b.total_net_cost == 0]
    if fully_funded:
        summary_parts.append(f"{len(fully_funded)} scholarships offer full funding with no remaining costs.")
    
    # Cost categories
    low_cost = [b for b in breakdowns if b.total_net_cost < 20000]
    medium_cost = [b for b in breakdowns if 20000 <= b.total_net_cost < 50000]
    high_cost = [b for b in breakdowns if b.total_net_cost >= 50000]
    
    if low_cost:
        summary_parts.append(f"{len(low_cost)} options have low net costs (under $20,000).")
    if medium_cost:
        summary_parts.append(f"{len(medium_cost)} options have medium net costs ($20,000-$50,000).")
    if high_cost:
        summary_parts.append(f"{len(high_cost)} options have high net costs (over $50,000).")
    
    return " ".join(summary_parts)

def _generate_funding_recommendations(breakdowns: List[FinancialBreakdown], student: Dict[str, Any]) -> List[str]:
    """Generate funding strategy recommendations"""
    recommendations = []
    
    if not breakdowns:
        return ["Unable to provide funding recommendations without financial data."]
    
    # Find best options
    min_cost = min(b.total_net_cost for b in breakdowns)
    best_options = [b for b in breakdowns if b.total_net_cost == min_cost]
    
    if min_cost == 0:
        recommendations.append("Prioritize fully-funded scholarships to minimize financial burden.")
    elif min_cost < 10000:
        recommendations.append("Focus on low-cost options that require minimal additional funding.")
    else:
        recommendations.append("Consider additional funding sources as all options require significant investment.")
    
    # Analyze funding gaps
    avg_cost = sum(b.total_net_cost for b in breakdowns) / len(breakdowns)
    
    if avg_cost > 30000:
        recommendations.extend([
            "Explore additional scholarships and grants to reduce costs.",
            "Consider part-time work or teaching assistantships while studying.",
            "Look into education loans with favorable terms."
        ])
    
    # Regional recommendations
    target_location = student.get('target_location', '').lower()
    if 'usa' in target_location or 'united states' in target_location:
        recommendations.append("Apply for FAFSA to access federal aid programs.")
    elif 'canada' in target_location:
        recommendations.append("Investigate provincial student aid programs.")
    elif 'uk' in target_location:
        recommendations.append("Consider UK student loan programs for international students.")
    
    # Profile-based recommendations
    profile_score = student.get('profile_score', 5)
    if profile_score >= 8:
        recommendations.append("Your strong profile qualifies you for merit-based scholarships.")
    elif profile_score < 6:
        recommendations.append("Focus on improving your profile to qualify for more scholarships.")
    
    return recommendations