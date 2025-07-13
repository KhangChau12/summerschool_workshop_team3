# utils/basetools/__init__.py

# Existing tools
from .calculator_tool import (
    CalculatorTool,
    CalculationInput,
    CalculationOutput,
    BasicOperationInput,
    TrigonometricInput,
    LogarithmInput,
    MemoryOperation,
    OperationType,
    calculate,
    basic_math,
    trigonometry,
    logarithm,
    calculator_memory
)

from .classfication_tool import (
    SearchInput as ClassificationInput,
    SearchOutput as ClassificationOutput
)

from .faq_tool import (
    SearchInput as FAQInput,
    SearchOutput as FAQOutput,
    faq_tool,
    create_faq_tool
)

from .file_reading_tool import (
    FileContentOutput,
    read_file_tool,
    create_read_file_tool
)

from .http_tool import (
    BodyType,
    ResponseType,
    HTTPMethod,
    HttpRequest,
    HttpResponse,
    http_tool
)

from .merge_files_tool import (
    MergeInput,
    MergeOutput,
    merge_files_tool
)

from .search_in_file_tool import (
    SearchInput as SearchInFileInput,
    SearchOutput as SearchInFileOutput,
    normalize,
    create_search_in_file_tool
)

from .search_web_tool import (
    SearchInput as WebSearchInput,
    SearchOutput as WebSearchOutput,
    search_web
)

from .send_email_tool import (
    EmailToolInput,
    EmailToolOutput,
    send_email_tool,
    create_send_email_tool
)

# New Study Abroad Counseling Tools
from .enhanced_web_search_tool import (
    SearchInput as EnhancedSearchInput,
    SearchResult,
    SearchOutput as EnhancedSearchOutput,
    enhanced_web_search
)

from .student_classification_tool import (
    StudentProfile,
    ClassifiedStudent,
    StudentClassificationInput,
    StudentClassificationOutput,
    student_classification_tool
)

from .scholarship_analysis_tool import (
    ScholarshipInfo,
    ScholarshipAnalysisInput,
    ScholarshipAnalysisOutput,
    scholarship_analysis_tool
)

from .scholarship_matching_tool import (
    MatchLevel,
    MatchedScholarship,
    ScholarshipMatchingInput,
    ScholarshipMatchingOutput,
    scholarship_matching_tool
)

from .financial_calculation_tool import (
    FinancialBreakdown,
    FinancialCalculationInput,
    FinancialCalculationOutput,
    financial_calculation_tool
)

# Export all for easy import with *
__all__ = [
    # Existing Calculator Tool
    'CalculatorTool',
    'CalculationInput',
    'CalculationOutput', 
    'BasicOperationInput',
    'TrigonometricInput',
    'LogarithmInput',
    'MemoryOperation',
    'OperationType',
    'calculate',
    'basic_math',
    'trigonometry',
    'logarithm',
    'calculator_memory',
    
    # Classification Tool
    'ClassificationInput',
    'ClassificationOutput',
    
    # FAQ Tool
    'FAQInput',
    'FAQOutput',
    'faq_tool',
    'create_faq_tool',
    
    # File Reading Tool
    'FileContentOutput',
    'read_file_tool',
    'create_read_file_tool',
    
    # HTTP Tool
    'BodyType',
    'ResponseType',
    'HTTPMethod',
    'HttpRequest',
    'HttpResponse',
    'http_tool',
    
    # Merge Files Tool
    'MergeInput',
    'MergeOutput',
    'merge_files_tool',
    
    # Search in File Tool
    'SearchInFileInput',
    'SearchInFileOutput',
    'normalize',
    'create_search_in_file_tool',
    
    # Search Web Tool
    'WebSearchInput',
    'WebSearchOutput',
    'search_web',
    
    # Send Email Tool
    'EmailToolInput',
    'EmailToolOutput',
    'send_email_tool',
    'create_send_email_tool',
    
    # New Enhanced Web Search Tool
    'EnhancedSearchInput',
    'SearchResult',
    'EnhancedSearchOutput',
    'enhanced_web_search',
    
    # Student Classification Tool
    'StudentProfile',
    'ClassifiedStudent',
    'StudentClassificationInput',
    'StudentClassificationOutput',
    'student_classification_tool',
    
    # Scholarship Analysis Tool
    'ScholarshipInfo',
    'ScholarshipAnalysisInput',
    'ScholarshipAnalysisOutput',
    'scholarship_analysis_tool',
    
    # Scholarship Matching Tool
    'MatchLevel',
    'MatchedScholarship',
    'ScholarshipMatchingInput',
    'ScholarshipMatchingOutput',
    'scholarship_matching_tool',
    
    # Financial Calculation Tool
    'FinancialBreakdown',
    'FinancialCalculationInput',
    'FinancialCalculationOutput',
    'financial_calculation_tool'
]