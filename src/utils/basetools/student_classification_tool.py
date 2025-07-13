# utils/basetools/student_classification_tool.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class StudentProfile(BaseModel):
    """Student profile input for classification"""
    personal_info: str = Field(..., description="Personal information including location, age, gender, religion, etc.")
    academic_background: str = Field(..., description="Academic achievements, GPA, test scores, etc.")
    extracurricular: str = Field(..., description="Extracurricular activities, volunteer work, leadership roles")
    certificates: str = Field(..., description="International certificates, language proficiency, etc.")
    target_field: str = Field(..., description="Intended field of study")
    target_location: str = Field(..., description="Preferred study location/country")

class ClassifiedStudent(BaseModel):
    """Classified student profile output"""
    region: str = Field(..., description="Student's region/country")
    age_group: str = Field(..., description="Age group (e.g., 18-22, 23-25)")
    gender: Optional[str] = Field(None, description="Gender if specified")
    religion: Optional[str] = Field(None, description="Religion if specified")
    academic_level: str = Field(..., description="Current academic level")
    target_field: str = Field(..., description="Intended field of study")
    target_location: str = Field(..., description="Preferred study location")
    academic_strengths: List[str] = Field(..., description="List of academic strengths")
    certificates_list: List[str] = Field(..., description="List of certificates and scores")
    extracurricular_list: List[str] = Field(..., description="List of extracurricular activities")
    profile_score: int = Field(..., description="Overall profile strength score (1-10)")

class StudentClassificationInput(BaseModel):
    student_profile: StudentProfile = Field(..., description="Student profile to classify")

class StudentClassificationOutput(BaseModel):
    classified_student: ClassifiedStudent = Field(..., description="Classified student profile")
    classification_notes: str = Field(..., description="Additional notes about classification")

def student_classification_tool(input: StudentClassificationInput) -> StudentClassificationOutput:
    """
    Classify and structure student profile for scholarship matching.
    This tool analyzes student information and organizes it into standardized categories
    for easier comparison with scholarship requirements.
    """
    profile = input.student_profile
    
    # Extract demographic information
    region = _extract_region(profile.personal_info, profile.target_location)
    age_group = _extract_age_group(profile.personal_info)
    gender = _extract_gender(profile.personal_info)
    religion = _extract_religion(profile.personal_info)
    
    # Extract academic information
    academic_level = _extract_academic_level(profile.academic_background)
    academic_strengths = _extract_academic_strengths(profile.academic_background)
    
    # Extract certificates and activities
    certificates_list = _extract_certificates(profile.certificates)
    extracurricular_list = _extract_extracurricular(profile.extracurricular)
    
    # Calculate profile score
    profile_score = _calculate_profile_score(
        profile.academic_background,
        profile.certificates,
        profile.extracurricular
    )
    
    classified_student = ClassifiedStudent(
        region=region,
        age_group=age_group,
        gender=gender,
        religion=religion,
        academic_level=academic_level,
        target_field=profile.target_field,
        target_location=profile.target_location,
        academic_strengths=academic_strengths,
        certificates_list=certificates_list,
        extracurricular_list=extracurricular_list,
        profile_score=profile_score
    )
    
    # Generate classification notes
    notes = _generate_classification_notes(classified_student)
    
    return StudentClassificationOutput(
        classified_student=classified_student,
        classification_notes=notes
    )

def _extract_region(personal_info: str, target_location: str) -> str:
    """Extract student's current region"""
    personal_lower = personal_info.lower()
    
    # Common region keywords
    regions = {
        'vietnam': ['vietnam', 'vietnamese', 'viet nam', 'saigon', 'hanoi', 'hcmc'],
        'southeast_asia': ['thailand', 'singapore', 'malaysia', 'indonesia', 'philippines'],
        'east_asia': ['china', 'japan', 'korea', 'taiwan', 'hong kong'],
        'south_asia': ['india', 'pakistan', 'bangladesh', 'sri lanka'],
        'middle_east': ['saudi', 'uae', 'qatar', 'iran', 'turkey'],
        'europe': ['germany', 'france', 'uk', 'italy', 'spain', 'netherlands'],
        'north_america': ['usa', 'canada', 'america', 'united states'],
        'australia': ['australia', 'new zealand']
    }
    
    for region, keywords in regions.items():
        if any(keyword in personal_lower for keyword in keywords):
            return region
    
    return 'other'

def _extract_age_group(personal_info: str) -> str:
    """Extract age group from personal information"""
    import re
    
    # Look for age mentions
    age_patterns = [
        r'(\d{1,2})\s*years?\s*old',
        r'age\s*:?\s*(\d{1,2})',
        r'(\d{1,2})\s*tuổi'
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, personal_info.lower())
        if match:
            age = int(match.group(1))
            if age <= 18:
                return 'under_18'
            elif age <= 22:
                return '18-22'
            elif age <= 25:
                return '23-25'
            elif age <= 30:
                return '26-30'
            else:
                return 'over_30'
    
    # Default based on common student age
    return '18-22'

def _extract_gender(personal_info: str) -> Optional[str]:
    """Extract gender from personal information"""
    personal_lower = personal_info.lower()
    
    if any(keyword in personal_lower for keyword in ['male', 'nam', 'boy', 'man']):
        return 'male'
    elif any(keyword in personal_lower for keyword in ['female', 'nữ', 'girl', 'woman']):
        return 'female'
    
    return None

def _extract_religion(personal_info: str) -> Optional[str]:
    """Extract religion from personal information"""
    personal_lower = personal_info.lower()
    
    religions = {
        'christian': ['christian', 'catholic', 'protestant'],
        'muslim': ['muslim', 'islam', 'islamic'],
        'buddhist': ['buddhist', 'buddhism'],
        'hindu': ['hindu', 'hinduism'],
        'jewish': ['jewish', 'judaism']
    }
    
    for religion, keywords in religions.items():
        if any(keyword in personal_lower for keyword in keywords):
            return religion
    
    return None

def _extract_academic_level(academic_background: str) -> str:
    """Extract current academic level"""
    academic_lower = academic_background.lower()
    
    if any(keyword in academic_lower for keyword in ['high school', 'secondary', 'thpt', 'grade 12']):
        return 'high_school'
    elif any(keyword in academic_lower for keyword in ['bachelor', 'undergraduate', 'đại học']):
        return 'undergraduate'
    elif any(keyword in academic_lower for keyword in ['master', 'graduate', 'thạc sĩ']):
        return 'graduate'
    elif any(keyword in academic_lower for keyword in ['phd', 'doctorate', 'tiến sĩ']):
        return 'doctorate'
    
    return 'undergraduate'  # Default

def _extract_academic_strengths(academic_background: str) -> List[str]:
    """Extract academic strengths and achievements"""
    strengths = []
    academic_lower = academic_background.lower()
    
    # GPA mentions
    import re
    gpa_pattern = r'gpa\s*:?\s*(\d+\.?\d*)'
    gpa_match = re.search(gpa_pattern, academic_lower)
    if gpa_match:
        gpa = float(gpa_match.group(1))
        if gpa >= 3.5:
            strengths.append(f"High GPA: {gpa}")
        else:
            strengths.append(f"GPA: {gpa}")
    
    # Common academic achievements
    achievement_keywords = {
        'honors': ['honor', 'distinction', 'dean\'s list', 'magna cum laude'],
        'awards': ['award', 'prize', 'medal', 'competition'],
        'research': ['research', 'publication', 'thesis'],
        'leadership': ['president', 'leader', 'captain', 'head']
    }
    
    for category, keywords in achievement_keywords.items():
        if any(keyword in academic_lower for keyword in keywords):
            strengths.append(category.title())
    
    return strengths if strengths else ['Standard Academic Performance']

def _extract_certificates(certificates: str) -> List[str]:
    """Extract and list certificates with scores if available"""
    cert_list = []
    certs_lower = certificates.lower()
    
    # Common certificates with score extraction
    cert_patterns = {
        'ielts': r'ielts\s*:?\s*(\d+\.?\d*)',
        'toefl': r'toefl\s*:?\s*(\d+)',
        'sat': r'sat\s*:?\s*(\d+)',
        'gre': r'gre\s*:?\s*(\d+)',
        'gmat': r'gmat\s*:?\s*(\d+)'
    }
    
    import re
    for cert_name, pattern in cert_patterns.items():
        match = re.search(pattern, certs_lower)
        if match:
            score = match.group(1)
            cert_list.append(f"{cert_name.upper()}: {score}")
        elif cert_name in certs_lower:
            cert_list.append(cert_name.upper())
    
    return cert_list if cert_list else ['No international certificates mentioned']

def _extract_extracurricular(extracurricular: str) -> List[str]:
    """Extract extracurricular activities"""
    activities = []
    extra_lower = extracurricular.lower()
    
    activity_keywords = {
        'volunteer': ['volunteer', 'community service', 'charity'],
        'sports': ['sport', 'football', 'basketball', 'swimming'],
        'arts': ['music', 'art', 'drama', 'dance'],
        'leadership': ['club', 'society', 'president', 'organizer'],
        'academic_clubs': ['debate', 'science club', 'math olympiad']
    }
    
    for category, keywords in activity_keywords.items():
        if any(keyword in extra_lower for keyword in keywords):
            activities.append(category.replace('_', ' ').title())
    
    return activities if activities else ['Limited extracurricular activities mentioned']

def _calculate_profile_score(academic: str, certificates: str, extracurricular: str) -> int:
    """Calculate overall profile strength score"""
    score = 5  # Base score
    
    # Academic component (0-3 points)
    academic_lower = academic.lower()
    if 'gpa' in academic_lower:
        import re
        gpa_match = re.search(r'gpa\s*:?\s*(\d+\.?\d*)', academic_lower)
        if gpa_match:
            gpa = float(gpa_match.group(1))
            if gpa >= 3.8:
                score += 3
            elif gpa >= 3.5:
                score += 2
            elif gpa >= 3.0:
                score += 1
    
    # Certificates component (0-2 points)
    certs_lower = certificates.lower()
    if any(cert in certs_lower for cert in ['ielts', 'toefl', 'sat', 'gre']):
        score += 2
    elif 'certificate' in certs_lower:
        score += 1
    
    # Extracurricular component (0-1 point)
    if len(extracurricular.strip()) > 50:  # Substantial extracurricular description
        score += 1
    
    return min(score, 10)  # Cap at 10

def _generate_classification_notes(student: ClassifiedStudent) -> str:
    """Generate additional notes about the classification"""
    notes = []
    
    if student.profile_score >= 8:
        notes.append("Strong candidate profile with high academic achievements.")
    elif student.profile_score >= 6:
        notes.append("Good candidate profile with solid background.")
    else:
        notes.append("Developing candidate profile - focus on strengthening weak areas.")
    
    if not student.gender:
        notes.append("Gender not specified - will match with gender-neutral scholarships.")
    
    if not student.religion:
        notes.append("Religion not specified - will match with non-religious scholarships.")
    
    if len(student.certificates_list) == 1 and 'No international' in student.certificates_list[0]:
        notes.append("Consider obtaining international certificates to improve scholarship eligibility.")
    
    return " ".join(notes)