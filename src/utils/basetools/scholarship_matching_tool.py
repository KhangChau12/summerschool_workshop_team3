# utils/basetools/scholarship_matching_tool.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class MatchLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good" 
    FAIR = "fair"
    POOR = "poor"
    NO_MATCH = "no_match"

class MatchedScholarship(BaseModel):
    """Scholarship with match analysis"""
    scholarship_name: str = Field(..., description="Name of the scholarship")
    university: str = Field(..., description="University offering the scholarship")
    match_level: MatchLevel = Field(..., description="Level of match with student profile")
    match_score: float = Field(..., description="Numerical match score (0-100)")
    matching_criteria: List[str] = Field(..., description="Criteria that match")
    missing_requirements: List[str] = Field(..., description="Requirements the student doesn't meet")
    scholarship_amount: str = Field(..., description="Scholarship amount")
    improvement_suggestions: List[str] = Field(..., description="Suggestions to improve match")
    application_priority: str = Field(..., description="Priority level for application")

class ScholarshipMatchingInput(BaseModel):
    """Input for scholarship matching"""
    student_profile: Dict[str, Any] = Field(..., description="Classified student profile")
    available_scholarships: List[Dict[str, Any]] = Field(..., description="List of available scholarships")

class ScholarshipMatchingOutput(BaseModel):
    """Output with matched scholarships"""
    matched_scholarships: List[MatchedScholarship] = Field(..., description="List of matched scholarships")
    total_matches: int = Field(..., description="Total number of matches found")
    best_matches: List[MatchedScholarship] = Field(..., description="Top 3 best matches")
    matching_summary: str = Field(..., description="Summary of matching results")

def scholarship_matching_tool(input: ScholarshipMatchingInput) -> ScholarshipMatchingOutput:
    """
    Match available scholarships to student profile and rank them by compatibility.
    """
    student = input.student_profile
    scholarships = input.available_scholarships
    
    matched_scholarships = []
    
    for scholarship in scholarships:
        match_result = _analyze_scholarship_match(student, scholarship)
        if match_result:
            matched_scholarships.append(match_result)
    
    # Sort by match score (highest first)
    matched_scholarships.sort(key=lambda x: x.match_score, reverse=True)
    
    # Get best matches (top 3)
    best_matches = matched_scholarships[:3]
    
    # Generate summary
    summary = _generate_matching_summary(matched_scholarships, student)
    
    return ScholarshipMatchingOutput(
        matched_scholarships=matched_scholarships,
        total_matches=len(matched_scholarships),
        best_matches=best_matches,
        matching_summary=summary
    )

def _analyze_scholarship_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> Optional[MatchedScholarship]:
    """Analyze how well a scholarship matches a student profile"""
    
    match_score = 0.0
    matching_criteria = []
    missing_requirements = []
    improvement_suggestions = []
    
    # Demographic matching (20 points total)
    demo_score, demo_matches, demo_missing = _check_demographic_match(student, scholarship)
    match_score += demo_score
    matching_criteria.extend(demo_matches)
    missing_requirements.extend(demo_missing)
    
    # Academic matching (30 points total)
    academic_score, academic_matches, academic_missing, academic_suggestions = _check_academic_match(student, scholarship)
    match_score += academic_score
    matching_criteria.extend(academic_matches)
    missing_requirements.extend(academic_missing)
    improvement_suggestions.extend(academic_suggestions)
    
    # Certificate matching (25 points total)
    cert_score, cert_matches, cert_missing, cert_suggestions = _check_certificate_match(student, scholarship)
    match_score += cert_score
    matching_criteria.extend(cert_matches)
    missing_requirements.extend(cert_missing)
    improvement_suggestions.extend(cert_suggestions)
    
    # Extracurricular matching (15 points total)
    extra_score, extra_matches, extra_missing, extra_suggestions = _check_extracurricular_match(student, scholarship)
    match_score += extra_score
    matching_criteria.extend(extra_matches)
    missing_requirements.extend(extra_missing)
    improvement_suggestions.extend(extra_suggestions)
    
    # Field of study matching (10 points total)
    field_score, field_matches, field_missing = _check_field_match(student, scholarship)
    match_score += field_score
    matching_criteria.extend(field_matches)
    missing_requirements.extend(field_missing)
    
    # Determine match level
    match_level = _determine_match_level(match_score)
    
    # Only return matches that are at least FAIR
    if match_level == MatchLevel.NO_MATCH:
        return None
    
    # Determine application priority
    priority = _determine_application_priority(match_score, missing_requirements)
    
    return MatchedScholarship(
        scholarship_name=scholarship.get('name', 'Unknown Scholarship'),
        university=scholarship.get('university', 'Unknown University'),
        match_level=match_level,
        match_score=round(match_score, 1),
        matching_criteria=matching_criteria,
        missing_requirements=missing_requirements,
        scholarship_amount=scholarship.get('scholarship_amount', 'Amount not specified'),
        improvement_suggestions=improvement_suggestions,
        application_priority=priority
    )

def _check_demographic_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> tuple:
    """Check demographic compatibility"""
    score = 0.0
    matches = []
    missing = []
    
    # Region match (8 points)
    student_region = student.get('region', '').lower()
    target_region = scholarship.get('target_region', '').lower()
    
    if target_region in ['all', 'international', 'global']:
        score += 8
        matches.append("Region: International scholarship")
    elif student_region in target_region or target_region in student_region:
        score += 8
        matches.append(f"Region: Matches {target_region}")
    elif 'developing' in target_region and student_region in ['vietnam', 'asia', 'southeast_asia']:
        score += 6
        matches.append("Region: Developing countries eligible")
    else:
        missing.append(f"Region mismatch: scholarship targets {target_region}")
    
    # Age group match (4 points)
    student_age = student.get('age_group', '')
    target_age = scholarship.get('target_age_group', '')
    
    if target_age in ['all', ''] or student_age == target_age:
        score += 4
        matches.append(f"Age group: Matches {student_age}")
    else:
        missing.append(f"Age group mismatch: scholarship targets {target_age}")
    
    # Gender match (4 points)
    student_gender = student.get('gender')
    target_gender = scholarship.get('target_gender')
    
    if target_gender is None:
        score += 4
        matches.append("Gender: Gender-neutral scholarship")
    elif student_gender == target_gender:
        score += 4
        matches.append(f"Gender: Matches {target_gender}")
    elif student_gender is None:
        score += 2
        matches.append("Gender: Not specified, may be eligible")
    else:
        missing.append(f"Gender mismatch: scholarship targets {target_gender}")
    
    # Religion match (4 points)
    student_religion = student.get('religion')
    target_religion = scholarship.get('target_religion')
    
    if target_religion is None:
        score += 4
        matches.append("Religion: Religion-neutral scholarship")
    elif student_religion == target_religion:
        score += 4
        matches.append(f"Religion: Matches {target_religion}")
    elif student_religion is None:
        score += 2
        matches.append("Religion: Not specified, may be eligible")
    else:
        missing.append(f"Religion mismatch: scholarship targets {target_religion}")
    
    return score, matches, missing

def _check_academic_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> tuple:
    """Check academic requirements compatibility"""
    score = 0.0
    matches = []
    missing = []
    suggestions = []
    
    # Profile score assessment (15 points)
    profile_score = student.get('profile_score', 5)
    academic_reqs = scholarship.get('academic_requirements', [])
    
    if profile_score >= 8:
        score += 15
        matches.append("Academic performance: Strong profile")
    elif profile_score >= 6:
        score += 12
        matches.append("Academic performance: Good profile")
    elif profile_score >= 4:
        score += 8
        matches.append("Academic performance: Adequate profile")
        if any('honor' in req.lower() for req in academic_reqs):
            suggestions.append("Work on achieving academic honors to strengthen profile")
    else:
        score += 4
        missing.append("Academic performance: Below average profile")
        suggestions.append("Focus on improving GPA and academic achievements")
    
    # Specific GPA requirements (15 points)
    gpa_requirements = [req for req in academic_reqs if 'gpa' in req.lower()]
    
    if gpa_requirements:
        # Extract required GPA
        import re
        for req in gpa_requirements:
            gpa_match = re.search(r'(\d+\.?\d*)', req)
            if gpa_match:
                required_gpa = float(gpa_match.group(1))
                
                # Estimate student GPA from profile score
                estimated_gpa = _estimate_gpa_from_profile(profile_score)
                
                if estimated_gpa >= required_gpa:
                    score += 15
                    matches.append(f"GPA requirement: Meets minimum {required_gpa}")
                elif estimated_gpa >= required_gpa - 0.2:
                    score += 10
                    matches.append(f"GPA requirement: Close to minimum {required_gpa}")
                    suggestions.append(f"Work on raising GPA to meet {required_gpa} requirement")
                else:
                    missing.append(f"GPA requirement: Need minimum {required_gpa}")
                    suggestions.append(f"Significant GPA improvement needed to reach {required_gpa}")
                break
    else:
        score += 10  # No specific GPA requirement
        matches.append("GPA requirement: No specific GPA requirement")
    
    return score, matches, missing, suggestions

def _check_certificate_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> tuple:
    """Check certificate requirements compatibility"""
    score = 0.0
    matches = []
    missing = []
    suggestions = []
    
    student_certs = student.get('certificates_list', [])
    required_certs = scholarship.get('required_certificates', [])
    
    if not required_certs or any('no specific' in cert.lower() for cert in required_certs):
        score += 15
        matches.append("Certificates: No specific requirements")
        return score, matches, missing, suggestions
    
    # Check each required certificate
    for req_cert in required_certs:
        req_cert_lower = req_cert.lower()
        
        if 'ielts' in req_cert_lower:
            ielts_score, ielts_matches, ielts_missing, ielts_suggestions = _check_specific_certificate(
                student_certs, req_cert, 'ielts', _extract_ielts_score
            )
            score += ielts_score
            matches.extend(ielts_matches)
            missing.extend(ielts_missing)
            suggestions.extend(ielts_suggestions)
        
        elif 'toefl' in req_cert_lower:
            toefl_score, toefl_matches, toefl_missing, toefl_suggestions = _check_specific_certificate(
                student_certs, req_cert, 'toefl', _extract_toefl_score
            )
            score += toefl_score
            matches.extend(toefl_matches)
            missing.extend(toefl_missing)
            suggestions.extend(toefl_suggestions)
        
        elif 'sat' in req_cert_lower:
            sat_score, sat_matches, sat_missing, sat_suggestions = _check_specific_certificate(
                student_certs, req_cert, 'sat', _extract_sat_score
            )
            score += sat_score
            matches.extend(sat_matches)
            missing.extend(sat_missing)
            suggestions.extend(sat_suggestions)
        
        elif 'gre' in req_cert_lower:
            gre_score, gre_matches, gre_missing, gre_suggestions = _check_specific_certificate(
                student_certs, req_cert, 'gre', _extract_gre_score
            )
            score += gre_score
            matches.extend(gre_matches)
            missing.extend(gre_missing)
            suggestions.extend(gre_suggestions)
    
    # If no certificates matched and student has no certificates
    if score == 0 and any('no international' in cert.lower() for cert in student_certs):
        missing.append("Missing required international certificates")
        suggestions.append("Obtain required certificates (IELTS/TOEFL/SAT/GRE) for this scholarship")
    
    return score, matches, missing, suggestions

def _check_specific_certificate(student_certs: List[str], required: str, cert_type: str, score_extractor) -> tuple:
    """Check specific certificate type"""
    score = 0.0
    matches = []
    missing = []
    suggestions = []
    
    # Extract required score
    import re
    required_score_match = re.search(r'(\d+\.?\d*)', required)
    required_score = float(required_score_match.group(1)) if required_score_match else None
    
    # Check if student has this certificate
    student_cert = None
    for cert in student_certs:
        if cert_type.lower() in cert.lower():
            student_cert = cert
            break
    
    if student_cert:
        student_score = score_extractor(student_cert)
        
        if student_score and required_score:
            if student_score >= required_score:
                score = 8.0
                matches.append(f"{cert_type.upper()}: {student_score} meets requirement {required_score}")
            elif student_score >= required_score * 0.9:  # Within 90%
                score = 6.0
                matches.append(f"{cert_type.upper()}: {student_score} close to requirement {required_score}")
                suggestions.append(f"Retake {cert_type.upper()} to reach {required_score} requirement")
            else:
                score = 3.0
                missing.append(f"{cert_type.upper()}: {student_score} below requirement {required_score}")
                suggestions.append(f"Significant {cert_type.upper()} improvement needed")
        elif student_score:
            score = 5.0
            matches.append(f"{cert_type.upper()}: Have certificate with score {student_score}")
        else:
            score = 3.0
            matches.append(f"{cert_type.upper()}: Have certificate but score not specified")
    else:
        missing.append(f"{cert_type.upper()}: Certificate required but not obtained")
        suggestions.append(f"Obtain {cert_type.upper()} certificate with minimum score {required_score}")
    
    return score, matches, missing, suggestions

def _check_extracurricular_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> tuple:
    """Check extracurricular requirements compatibility"""
    score = 0.0
    matches = []
    missing = []
    suggestions = []
    
    student_activities = student.get('extracurricular_list', [])
    required_activities = scholarship.get('required_extracurricular', [])
    
    if any('no specific' in activity.lower() for activity in required_activities):
        score += 10
        matches.append("Extracurricular: No specific requirements")
        return score, matches, missing, suggestions
    
    # Check overlap
    student_activities_lower = [activity.lower() for activity in student_activities]
    required_activities_lower = [activity.lower() for activity in required_activities]
    
    overlap_count = 0
    for req_activity in required_activities_lower:
        for student_activity in student_activities_lower:
            if req_activity in student_activity or student_activity in req_activity:
                overlap_count += 1
                matches.append(f"Extracurricular: {req_activity.title()} activity present")
                break
    
    if len(required_activities) > 0:
        overlap_ratio = overlap_count / len(required_activities)
        score = overlap_ratio * 15
        
        if overlap_ratio < 0.5:
            missing_activities = [activity for activity in required_activities 
                                if not any(activity.lower() in sa.lower() for sa in student_activities_lower)]
            missing.extend([f"Missing activity: {activity}" for activity in missing_activities])
            suggestions.extend([f"Consider engaging in {activity.lower()} activities" for activity in missing_activities])
    
    return score, matches, missing, suggestions

def _check_field_match(student: Dict[str, Any], scholarship: Dict[str, Any]) -> tuple:
    """Check field of study compatibility"""
    score = 0.0
    matches = []
    missing = []
    
    student_field = student.get('target_field', '').lower()
    scholarship_field = scholarship.get('field_of_study', '').lower()
    
    if scholarship_field in ['all', '']:
        score += 10
        matches.append("Field of study: Open to all fields")
    elif student_field == scholarship_field:
        score += 10
        matches.append(f"Field of study: Perfect match ({student_field})")
    elif student_field in scholarship_field or scholarship_field in student_field:
        score += 8
        matches.append(f"Field of study: Related field match")
    else:
        missing.append(f"Field mismatch: scholarship for {scholarship_field}, student wants {student_field}")
    
    return score, matches, missing

def _estimate_gpa_from_profile(profile_score: int) -> float:
    """Estimate GPA from profile score"""
    if profile_score >= 9:
        return 3.8
    elif profile_score >= 8:
        return 3.6
    elif profile_score >= 7:
        return 3.4
    elif profile_score >= 6:
        return 3.2
    elif profile_score >= 5:
        return 3.0
    else:
        return 2.8

def _extract_ielts_score(cert_text: str) -> Optional[float]:
    """Extract IELTS score from certificate text"""
    import re
    match = re.search(r'ielts:\s*(\d+\.?\d*)', cert_text.lower())
    return float(match.group(1)) if match else None

def _extract_toefl_score(cert_text: str) -> Optional[int]:
    """Extract TOEFL score from certificate text"""
    import re
    match = re.search(r'toefl:\s*(\d+)', cert_text.lower())
    return int(match.group(1)) if match else None

def _extract_sat_score(cert_text: str) -> Optional[int]:
    """Extract SAT score from certificate text"""
    import re
    match = re.search(r'sat:\s*(\d+)', cert_text.lower())
    return int(match.group(1)) if match else None

def _extract_gre_score(cert_text: str) -> Optional[int]:
    """Extract GRE score from certificate text"""
    import re
    match = re.search(r'gre:\s*(\d+)', cert_text.lower())
    return int(match.group(1)) if match else None

def _determine_match_level(score: float) -> MatchLevel:
    """Determine match level based on score"""
    if score >= 80:
        return MatchLevel.EXCELLENT
    elif score >= 65:
        return MatchLevel.GOOD
    elif score >= 45:
        return MatchLevel.FAIR
    elif score >= 25:
        return MatchLevel.POOR
    else:
        return MatchLevel.NO_MATCH

def _determine_application_priority(score: float, missing_requirements: List[str]) -> str:
    """Determine application priority"""
    if score >= 80 and len(missing_requirements) <= 1:
        return "HIGH - Strong match, apply immediately"
    elif score >= 65 and len(missing_requirements) <= 2:
        return "MEDIUM - Good match, prepare application"
    elif score >= 45:
        return "LOW - Fair match, consider as backup"
    else:
        return "VERY LOW - Poor match, focus on improvement first"

def _generate_matching_summary(matched_scholarships: List[MatchedScholarship], student: Dict[str, Any]) -> str:
    """Generate summary of matching results"""
    if not matched_scholarships:
        return "No suitable scholarships found. Consider broadening search criteria or improving profile."
    
    total = len(matched_scholarships)
    excellent = sum(1 for s in matched_scholarships if s.match_level == MatchLevel.EXCELLENT)
    good = sum(1 for s in matched_scholarships if s.match_level == MatchLevel.GOOD)
    fair = sum(1 for s in matched_scholarships if s.match_level == MatchLevel.FAIR)
    
    summary_parts = []
    summary_parts.append(f"Found {total} scholarship matches for your profile.")
    
    if excellent > 0:
        summary_parts.append(f"{excellent} excellent matches - these should be your top priority.")
    if good > 0:
        summary_parts.append(f"{good} good matches - strong candidates for application.")
    if fair > 0:
        summary_parts.append(f"{fair} fair matches - consider as backup options.")
    
    # Overall recommendations
    avg_score = sum(s.match_score for s in matched_scholarships) / len(matched_scholarships)
    if avg_score >= 70:
        summary_parts.append("Your profile is competitive for most scholarships.")
    elif avg_score >= 50:
        summary_parts.append("Your profile shows good potential with some areas for improvement.")
    else:
        summary_parts.append("Focus on strengthening your profile before applying.")
    
    return " ".join(summary_parts)