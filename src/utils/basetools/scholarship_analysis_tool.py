# utils/basetools/scholarship_analysis_tool.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re

class ScholarshipInfo(BaseModel):
    """Individual scholarship information"""
    name: str = Field(..., description="Scholarship name")
    university: str = Field(..., description="University offering the scholarship")
    target_region: str = Field(..., description="Target region/country for applicants")
    target_age_group: str = Field(..., description="Target age group")
    target_gender: Optional[str] = Field(None, description="Target gender if specified")
    target_religion: Optional[str] = Field(None, description="Target religion if specified")
    field_of_study: str = Field(..., description="Field of study or 'All' if general")
    academic_requirements: List[str] = Field(..., description="Academic requirements")
    required_certificates: List[str] = Field(..., description="Required certificates and minimum scores")
    required_extracurricular: List[str] = Field(..., description="Required/preferred extracurricular activities")
    scholarship_amount: str = Field(..., description="Scholarship amount or percentage")
    deadline: str = Field(..., description="Application deadline")
    additional_requirements: List[str] = Field(..., description="Other specific requirements")

class ScholarshipAnalysisInput(BaseModel):
    """Input for scholarship analysis"""
    search_results: List[str] = Field(..., description="Web search results content about scholarships")
    target_university: str = Field(..., description="Target university name")
    target_field: str = Field(..., description="Target field of study")

class ScholarshipAnalysisOutput(BaseModel):
    """Output containing analyzed scholarship information"""
    scholarships: List[ScholarshipInfo] = Field(..., description="List of analyzed scholarships")
    analysis_summary: str = Field(..., description="Summary of scholarship opportunities")
    total_scholarships_found: int = Field(..., description="Total number of scholarships identified")

def scholarship_analysis_tool(input: ScholarshipAnalysisInput) -> ScholarshipAnalysisOutput:
    """
    Analyze scholarship information from web search results and structure it
    for easy comparison with student profiles.
    """
    scholarships = []
    
    for content in input.search_results:
        if not content.strip():
            continue
            
        # Extract scholarships from each search result
        extracted_scholarships = _extract_scholarships_from_content(
            content, 
            input.target_university, 
            input.target_field
        )
        scholarships.extend(extracted_scholarships)
    
    # Remove duplicates and clean up
    scholarships = _remove_duplicate_scholarships(scholarships)
    
    # Generate analysis summary
    summary = _generate_analysis_summary(scholarships, input.target_university, input.target_field)
    
    return ScholarshipAnalysisOutput(
        scholarships=scholarships,
        analysis_summary=summary,
        total_scholarships_found=len(scholarships)
    )

def _extract_scholarships_from_content(content: str, target_university: str, target_field: str) -> List[ScholarshipInfo]:
    """Extract scholarship information from content text"""
    scholarships = []
    content_lower = content.lower()
    
    # Split content into potential scholarship sections
    sections = _split_into_scholarship_sections(content)
    
    for section in sections:
        scholarship = _parse_scholarship_section(section, target_university, target_field)
        if scholarship:
            scholarships.append(scholarship)
    
    return scholarships

def _split_into_scholarship_sections(content: str) -> List[str]:
    """Split content into individual scholarship sections"""
    # Common scholarship section delimiters
    delimiters = [
        r'\n\n\d+\.',  # Numbered lists
        r'\n\n[A-Z][a-zA-Z\s]+Scholarship',  # Scholarship names
        r'\n\n•',  # Bullet points
        r'\n\n-',  # Dashes
        r'Scholarship Name:',
        r'Award:',
        r'Eligibility:'
    ]
    
    sections = [content]
    
    for delimiter in delimiters:
        new_sections = []
        for section in sections:
            splits = re.split(delimiter, section, flags=re.IGNORECASE)
            new_sections.extend([s.strip() for s in splits if s.strip()])
        sections = new_sections
    
    return [s for s in sections if len(s) > 100]  # Filter out very short sections

def _parse_scholarship_section(section: str, target_university: str, target_field: str) -> Optional[ScholarshipInfo]:
    """Parse individual scholarship section"""
    try:
        # Extract scholarship name
        name = _extract_scholarship_name(section)
        if not name:
            return None
        
        # Extract university
        university = _extract_university(section, target_university)
        
        # Extract target demographics
        target_region = _extract_target_region(section)
        target_age_group = _extract_target_age_group(section)
        target_gender = _extract_target_gender(section)
        target_religion = _extract_target_religion(section)
        
        # Extract field of study
        field_of_study = _extract_field_of_study(section, target_field)
        
        # Extract requirements
        academic_requirements = _extract_academic_requirements(section)
        required_certificates = _extract_required_certificates(section)
        required_extracurricular = _extract_required_extracurricular(section)
        
        # Extract scholarship details
        scholarship_amount = _extract_scholarship_amount(section)
        deadline = _extract_deadline(section)
        additional_requirements = _extract_additional_requirements(section)
        
        return ScholarshipInfo(
            name=name,
            university=university,
            target_region=target_region,
            target_age_group=target_age_group,
            target_gender=target_gender,
            target_religion=target_religion,
            field_of_study=field_of_study,
            academic_requirements=academic_requirements,
            required_certificates=required_certificates,
            required_extracurricular=required_extracurricular,
            scholarship_amount=scholarship_amount,
            deadline=deadline,
            additional_requirements=additional_requirements
        )
    
    except Exception as e:
        print(f"Error parsing scholarship section: {e}")
        return None

def _extract_scholarship_name(section: str) -> Optional[str]:
    """Extract scholarship name from section"""
    # Look for common scholarship name patterns
    patterns = [
        r'([A-Z][a-zA-Z\s]+Scholarship)',
        r'Scholarship Name:\s*([^\n]+)',
        r'Name:\s*([^\n]+)',
        r'^([A-Z][a-zA-Z\s]+(?:Award|Grant|Fellowship))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, section, re.MULTILINE)
        if match:
            name = match.group(1).strip()
            if len(name) > 5 and 'scholarship' in name.lower():
                return name
    
    # Fallback: use first line if it looks like a title
    first_line = section.split('\n')[0].strip()
    if len(first_line) < 100 and any(word in first_line.lower() for word in ['scholarship', 'award', 'grant']):
        return first_line
    
    return None

def _extract_university(section: str, target_university: str) -> str:
    """Extract university name"""
    section_lower = section.lower()
    target_lower = target_university.lower()
    
    if target_lower in section_lower:
        return target_university
    
    # Look for university patterns
    university_patterns = [
        r'University of ([A-Z][a-zA-Z\s]+)',
        r'([A-Z][a-zA-Z\s]+University)',
        r'([A-Z][a-zA-Z\s]+College)',
        r'([A-Z][a-zA-Z\s]+Institute)'
    ]
    
    for pattern in university_patterns:
        match = re.search(pattern, section)
        if match:
            return match.group(0).strip()
    
    return target_university  # Default to target university

def _extract_target_region(section: str) -> str:
    """Extract target region for applicants"""
    section_lower = section.lower()
    
    # Region keywords
    region_keywords = {
        'international': ['international', 'global', 'worldwide', 'any country'],
        'developing_countries': ['developing countries', 'emerging economies'],
        'asia': ['asia', 'asian'],
        'southeast_asia': ['southeast asia', 'asean'],
        'africa': ['africa', 'african'],
        'latin_america': ['latin america', 'south america'],
        'europe': ['europe', 'european'],
        'specific_countries': []
    }
    
    for region, keywords in region_keywords.items():
        if any(keyword in section_lower for keyword in keywords):
            return region
    
    # Look for specific country mentions
    countries = ['vietnam', 'china', 'india', 'thailand', 'indonesia', 'malaysia', 'philippines']
    mentioned_countries = [country for country in countries if country in section_lower]
    if mentioned_countries:
        return f"specific_countries: {', '.join(mentioned_countries)}"
    
    return 'all'  # Default

def _extract_target_age_group(section: str) -> str:
    """Extract target age group"""
    section_lower = section.lower()
    
    # Age-related keywords
    if any(keyword in section_lower for keyword in ['undergraduate', 'bachelor', 'first year']):
        return '18-22'
    elif any(keyword in section_lower for keyword in ['graduate', 'master', 'postgraduate']):
        return '23-26'
    elif any(keyword in section_lower for keyword in ['phd', 'doctorate', 'doctoral']):
        return '25-30'
    elif any(keyword in section_lower for keyword in ['high school', 'secondary']):
        return 'under_18'
    
    return 'all'  # Default

def _extract_target_gender(section: str) -> Optional[str]:
    """Extract target gender"""
    section_lower = section.lower()
    
    if any(keyword in section_lower for keyword in ['women', 'female', 'girls']):
        return 'female'
    elif any(keyword in section_lower for keyword in ['men', 'male', 'boys']):
        return 'male'
    
    return None  # Gender neutral

def _extract_target_religion(section: str) -> Optional[str]:
    """Extract target religion"""
    section_lower = section.lower()
    
    religions = {
        'christian': ['christian', 'catholic', 'protestant'],
        'muslim': ['muslim', 'islamic'],
        'jewish': ['jewish'],
        'buddhist': ['buddhist'],
        'hindu': ['hindu']
    }
    
    for religion, keywords in religions.items():
        if any(keyword in section_lower for keyword in keywords):
            return religion
    
    return None  # Religion neutral

def _extract_field_of_study(section: str, target_field: str) -> str:
    """Extract field of study"""
    section_lower = section.lower()
    target_lower = target_field.lower()
    
    if target_lower in section_lower:
        return target_field
    
    # Common field keywords
    fields = {
        'engineering': ['engineering', 'computer science', 'technology'],
        'business': ['business', 'mba', 'management', 'economics'],
        'medicine': ['medicine', 'medical', 'healthcare', 'nursing'],
        'science': ['science', 'physics', 'chemistry', 'biology'],
        'arts': ['arts', 'humanities', 'literature', 'history'],
        'law': ['law', 'legal'],
        'education': ['education', 'teaching']
    }
    
    for field, keywords in fields.items():
        if any(keyword in section_lower for keyword in keywords):
            return field
    
    return 'all'  # Default

def _extract_academic_requirements(section: str) -> List[str]:
    """Extract academic requirements"""
    requirements = []
    section_lower = section.lower()
    
    # GPA requirements
    gpa_patterns = [
        r'gpa\s*(?:of\s*)?(\d+\.?\d*)',
        r'grade point average\s*(?:of\s*)?(\d+\.?\d*)',
        r'minimum\s*gpa\s*(\d+\.?\d*)'
    ]
    
    for pattern in gpa_patterns:
        match = re.search(pattern, section_lower)
        if match:
            requirements.append(f"Minimum GPA: {match.group(1)}")
    
    # Academic standing
    if any(keyword in section_lower for keyword in ['honor', 'distinction', 'dean\'s list']):
        requirements.append("Academic honors required")
    
    if any(keyword in section_lower for keyword in ['top 10%', 'top ten percent']):
        requirements.append("Top 10% academic standing")
    
    return requirements if requirements else ["Standard academic performance"]

def _extract_required_certificates(section: str) -> List[str]:
    """Extract required certificates and scores"""
    certificates = []
    section_lower = section.lower()
    
    # IELTS
    ielts_pattern = r'ielts\s*(?:score\s*)?(?:of\s*)?(\d+\.?\d*)'
    ielts_match = re.search(ielts_pattern, section_lower)
    if ielts_match:
        certificates.append(f"IELTS: minimum {ielts_match.group(1)}")
    elif 'ielts' in section_lower:
        certificates.append("IELTS required")
    
    # TOEFL
    toefl_pattern = r'toefl\s*(?:score\s*)?(?:of\s*)?(\d+)'
    toefl_match = re.search(toefl_pattern, section_lower)
    if toefl_match:
        certificates.append(f"TOEFL: minimum {toefl_match.group(1)}")
    elif 'toefl' in section_lower:
        certificates.append("TOEFL required")
    
    # SAT
    sat_pattern = r'sat\s*(?:score\s*)?(?:of\s*)?(\d+)'
    sat_match = re.search(sat_pattern, section_lower)
    if sat_match:
        certificates.append(f"SAT: minimum {sat_match.group(1)}")
    elif 'sat' in section_lower:
        certificates.append("SAT required")
    
    # GRE
    gre_pattern = r'gre\s*(?:score\s*)?(?:of\s*)?(\d+)'
    gre_match = re.search(gre_pattern, section_lower)
    if gre_match:
        certificates.append(f"GRE: minimum {gre_match.group(1)}")
    elif 'gre' in section_lower:
        certificates.append("GRE required")
    
    return certificates if certificates else ["No specific certificates mentioned"]

def _extract_required_extracurricular(section: str) -> List[str]:
    """Extract required extracurricular activities"""
    activities = []
    section_lower = section.lower()
    
    activity_keywords = {
        'leadership': ['leadership', 'president', 'captain', 'head'],
        'volunteer': ['volunteer', 'community service', 'charity'],
        'research': ['research', 'publication', 'thesis'],
        'sports': ['sports', 'athletics', 'team'],
        'arts': ['arts', 'music', 'drama', 'creative']
    }
    
    for activity, keywords in activity_keywords.items():
        if any(keyword in section_lower for keyword in keywords):
            activities.append(activity.title())
    
    return activities if activities else ["No specific extracurricular requirements"]

def _extract_scholarship_amount(section: str) -> str:
    """Extract scholarship amount or coverage"""
    section_lower = section.lower()
    
    # Full coverage keywords
    if any(keyword in section_lower for keyword in ['full tuition', 'full scholarship', '100%']):
        return "Full tuition coverage"
    
    # Partial coverage
    partial_patterns = [
        r'(\d+)%\s*(?:of\s*)?tuition',
        r'up to\s*\$(\d+,?\d*)',
        r'\$(\d+,?\d*)\s*per\s*year'
    ]
    
    for pattern in partial_patterns:
        match = re.search(pattern, section_lower)
        if match:
            return f"Amount: {match.group(0)}"
    
    # Living allowance
    if any(keyword in section_lower for keyword in ['living allowance', 'stipend', 'monthly allowance']):
        return "Tuition + living allowance"
    
    return "Amount not specified"

def _extract_deadline(section: str) -> str:
    """Extract application deadline"""
    # Date patterns
    date_patterns = [
        r'deadline:\s*([^\n]+)',
        r'apply by:\s*([^\n]+)',
        r'due date:\s*([^\n]+)',
        r'(\w+\s+\d{1,2},?\s+\d{4})',  # Month Day, Year
        r'(\d{1,2}/\d{1,2}/\d{4})',      # MM/DD/YYYY
        r'(\d{1,2}-\d{1,2}-\d{4})'       # MM-DD-YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Deadline not specified"

def _extract_additional_requirements(section: str) -> List[str]:
    """Extract additional specific requirements"""
    requirements = []
    section_lower = section.lower()
    
    # Common additional requirements
    if 'essay' in section_lower:
        requirements.append("Essay required")
    
    if any(keyword in section_lower for keyword in ['interview', 'interview required']):
        requirements.append("Interview required")
    
    if any(keyword in section_lower for keyword in ['recommendation', 'reference letter']):
        requirements.append("Recommendation letters required")
    
    if any(keyword in section_lower for keyword in ['financial need', 'need-based']):
        requirements.append("Financial need demonstration")
    
    if any(keyword in section_lower for keyword in ['work experience', 'professional experience']):
        requirements.append("Work experience preferred")
    
    return requirements

def _remove_duplicate_scholarships(scholarships: List[ScholarshipInfo]) -> List[ScholarshipInfo]:
    """Remove duplicate scholarships based on name similarity"""
    unique_scholarships = []
    seen_names = set()
    
    for scholarship in scholarships:
        # Create a normalized name for comparison
        normalized_name = scholarship.name.lower().strip()
        normalized_name = re.sub(r'\s+', ' ', normalized_name)
        
        if normalized_name not in seen_names:
            seen_names.add(normalized_name)
            unique_scholarships.append(scholarship)
    
    return unique_scholarships

def _generate_analysis_summary(scholarships: List[ScholarshipInfo], target_university: str, target_field: str) -> str:
    """Generate summary of scholarship analysis"""
    if not scholarships:
        return f"No scholarships found for {target_field} at {target_university}. Consider broadening search criteria."
    
    summary_parts = []
    summary_parts.append(f"Found {len(scholarships)} scholarship opportunities for {target_field} studies.")
    
    # Analyze coverage types
    full_coverage = sum(1 for s in scholarships if 'full' in s.scholarship_amount.lower())
    if full_coverage > 0:
        summary_parts.append(f"{full_coverage} offer full tuition coverage.")
    
    # Analyze target demographics
    gender_specific = sum(1 for s in scholarships if s.target_gender is not None)
    if gender_specific > 0:
        summary_parts.append(f"{gender_specific} are gender-specific scholarships.")
    
    # Analyze requirements
    with_certificates = sum(1 for s in scholarships if 'required' in ' '.join(s.required_certificates).lower())
    if with_certificates > 0:
        summary_parts.append(f"{with_certificates} require specific certificates (IELTS/TOEFL/SAT/GRE).")
    
    return " ".join(summary_parts)