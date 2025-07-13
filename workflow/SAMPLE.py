# Study Abroad Counseling Multi-Agent Workflow
# workflow/sample.py

import os
import asyncio
from typing import Dict, Any, List
import json
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from llm.base import AgentClient
import chainlit as cl
from data.cache.memory_handler import MessageMemoryHandler

# Import system prompts
from data.prompts.demo import (
    COORDINATOR_AGENT_PROMPT,
    SCHOLARSHIP_RESEARCH_AGENT_PROMPT,
    STUDENT_CLASSIFICATION_AGENT_PROMPT,
    PROFILE_ANALYSIS_AGENT_PROMPT,
    SCHOLARSHIP_MATCHING_AGENT_PROMPT,
    FINANCIAL_RESEARCH_AGENT_PROMPT,
    COMPREHENSIVE_COUNSELING_AGENT_PROMPT
)

# Import tools
from utils.basetools.enhanced_web_search_tool import enhanced_web_search
from utils.basetools.student_classification_tool import student_classification_tool
from utils.basetools.scholarship_analysis_tool import scholarship_analysis_tool
from utils.basetools.scholarship_matching_tool import scholarship_matching_tool
from utils.basetools.financial_calculation_tool import financial_calculation_tool
from utils.basetools.send_email_tool import create_send_email_tool

class StudyAbroadCounselingSystem:
    """Multi-agent system for study abroad counseling"""
    
    def __init__(self):
        # Initialize AI components
        self.provider = GoogleGLAProvider(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = GeminiModel('gemini-2.0-flash', provider=self.provider)
        
        # Initialize tools
        self.web_search_tool = enhanced_web_search
        self.student_classification_tool = student_classification_tool
        self.scholarship_analysis_tool = scholarship_analysis_tool
        self.scholarship_matching_tool = scholarship_matching_tool
        self.financial_calculation_tool = financial_calculation_tool
        self.email_tool = create_send_email_tool(
            to_emails=["admin@studyabroad.com"],
            sender_email="system@studyabroad.com", 
            sender_password="system_password"
        )
        
        # Initialize agents
        self._initialize_agents()
        
        # Initialize memory handler
        self.memory_handler = MessageMemoryHandler(max_messages=20)
        
        # Workflow state
        self.workflow_state = {}
    
    def _initialize_agents(self):
        """Initialize all agents with their specific prompts and tools"""
        
        # Agent 1: Coordinator Agent
        self.coordinator_agent = AgentClient(
            model=self.model,
            system_prompt=COORDINATOR_AGENT_PROMPT,
            tools=[]
        ).create_agent()
        
        # Agent 2: Scholarship Research Agent
        self.scholarship_research_agent = AgentClient(
            model=self.model,
            system_prompt=SCHOLARSHIP_RESEARCH_AGENT_PROMPT,
            tools=[self.web_search_tool, self.scholarship_analysis_tool]
        ).create_agent()
        
        # Agent 3: Student Classification Agent
        self.student_classification_agent = AgentClient(
            model=self.model,
            system_prompt=STUDENT_CLASSIFICATION_AGENT_PROMPT,
            tools=[self.student_classification_tool]
        ).create_agent()
        
        # Agent 4: Profile Analysis Agent
        self.profile_analysis_agent = AgentClient(
            model=self.model,
            system_prompt=PROFILE_ANALYSIS_AGENT_PROMPT,
            tools=[]
        ).create_agent()
        
        # Agent 5: Scholarship Matching Agent
        self.scholarship_matching_agent = AgentClient(
            model=self.model,
            system_prompt=SCHOLARSHIP_MATCHING_AGENT_PROMPT,
            tools=[self.scholarship_matching_tool]
        ).create_agent()
        
        # Agent 6: Financial Research Agent
        self.financial_research_agent = AgentClient(
            model=self.model,
            system_prompt=FINANCIAL_RESEARCH_AGENT_PROMPT,
            tools=[self.web_search_tool, self.financial_calculation_tool]
        ).create_agent()
        
        # Agent 7: Comprehensive Counseling Agent
        self.comprehensive_counseling_agent = AgentClient(
            model=self.model,
            system_prompt=COMPREHENSIVE_COUNSELING_AGENT_PROMPT,
            tools=[self.email_tool]
        ).create_agent()
    
    async def process_counseling_request(self, user_input: str) -> str:
        """
        Main workflow to process study abroad counseling request
        Following the 5-step process with 6 agents
        """
        try:
            # Store user input
            self.workflow_state['user_input'] = user_input
            
            # Step 1: Coordinate and extract information
            await self._step_1_coordination(user_input)
            
            # Step 2: Parallel processing (Research + Classification + Analysis)
            await self._step_2_parallel_processing()
            
            # Step 3: Match scholarships to student
            await self._step_3_scholarship_matching()
            
            # Step 4: Financial analysis
            await self._step_4_financial_analysis()
            
            # Step 5: Comprehensive counseling
            final_response = await self._step_5_comprehensive_counseling()
            
            return final_response
            
        except Exception as e:
            error_message = f"Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"
            print(f"Workflow error: {e}")
            return error_message
    
    async def _step_1_coordination(self, user_input: str):
        """Step 1: Coordinator Agent - Extract and structure user information"""
        
        coordination_prompt = f"""
        Người dùng đã cung cấp thông tin sau về nhu cầu du học:
        
        "{user_input}"
        
        Hãy phân tích và trích xuất thông tin có cấu trúc bao gồm:
        1. Trường đại học/tổ chức mục tiêu
        2. Quốc gia/khu vực muốn học
        3. Ngành học/chuyên ngành
        4. Thông tin hồ sơ cá nhân của học sinh
        
        Trả về kết quả dưới dạng JSON có cấu trúc rõ ràng.
        """
        
        response = await self.coordinator_agent.run(coordination_prompt)
        
        # Parse and store structured information
        try:
            # Extract structured data from response
            structured_data = self._extract_structured_data_from_response(str(response.output))
            self.workflow_state['structured_input'] = structured_data
            self.workflow_state['step_1_complete'] = True
            
        except Exception as e:
            print(f"Error in step 1: {e}")
            # Fallback to basic extraction
            self.workflow_state['structured_input'] = {
                'target_university': 'Unknown',
                'target_location': 'Unknown',
                'target_field': 'Unknown',
                'student_profile': user_input
            }
    
    async def _step_2_parallel_processing(self):
        """Step 2: Parallel processing with multiple agents"""
        
        structured_input = self.workflow_state.get('structured_input', {})
        
        # Create parallel tasks
        tasks = [
            self._task_2a_scholarship_research(structured_input),
            self._task_2b_student_classification(structured_input),
            self._task_2c_profile_analysis(structured_input)
        ]
        
        # Execute tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        self.workflow_state['scholarship_research_result'] = results[0] if not isinstance(results[0], Exception) else None
        self.workflow_state['student_classification_result'] = results[1] if not isinstance(results[1], Exception) else None
        self.workflow_state['profile_analysis_result'] = results[2] if not isinstance(results[2], Exception) else None
        self.workflow_state['step_2_complete'] = True
    
    async def _task_2a_scholarship_research(self, structured_input: Dict[str, Any]):
        """Task 2A: Research scholarships using web search"""
        
        target_university = structured_input.get('target_university', 'Unknown')
        target_field = structured_input.get('target_field', 'Unknown')
        target_location = structured_input.get('target_location', 'Unknown')
        
        research_prompt = f"""
        Tìm kiếm thông tin học bổng cho:
        - Trường đại học: {target_university}
        - Ngành học: {target_field}
        - Quốc gia: {target_location}
        
        Sử dụng web search tool để tìm các học bổng phù hợp và phân tích thông tin chi tiết.
        Tạo bảng hệ thống thông tin WAO1 với đầy đủ thông tin về học bổng.
        """
        
        response = await self.scholarship_research_agent.run(research_prompt)
        return response.output
    
    async def _task_2b_student_classification(self, structured_input: Dict[str, Any]):
        """Task 2B: Classify student profile"""
        
        student_profile = structured_input.get('student_profile', '')
        
        classification_prompt = f"""
        Phân loại hồ sơ học sinh sau:
        
        {student_profile}
        
        Sử dụng student classification tool để phân tích và tạo hồ sơ có cấu trúc WAO2.
        """
        
        response = await self.student_classification_agent.run(classification_prompt)
        return response.output
    
    async def _task_2c_profile_analysis(self, structured_input: Dict[str, Any]):
        """Task 2C: Detailed profile analysis"""
        
        student_profile = structured_input.get('student_profile', '')
        
        analysis_prompt = f"""
        Phân tích chi tiết hồ sơ học sinh:
        
        {student_profile}
        
        Đánh giá các thành tích học tập, chứng chỉ quốc tế, hoạt động ngoại khóa và tạo portfolio thành tích.
        """
        
        response = await self.profile_analysis_agent.run(analysis_prompt)
        return response.output
    
    async def _step_3_scholarship_matching(self):
        """Step 3: Match scholarships to student profile"""
        
        scholarship_data = self.workflow_state.get('scholarship_research_result')
        student_data = self.workflow_state.get('student_classification_result')
        
        if not scholarship_data or not student_data:
            print("Missing data for scholarship matching")
            return
        
        matching_prompt = f"""
        Đối chiếu hồ sơ học sinh với các học bổng có sẵn:
        
        Dữ liệu học sinh (WAO2):
        {student_data}
        
        Dữ liệu học bổng (WAO1):
        {scholarship_data}
        
        Sử dụng scholarship matching tool để tính toán điểm phù hợp và tạo danh sách học bổng phù hợp (WHAT).
        """
        
        response = await self.scholarship_matching_agent.run(matching_prompt)
        self.workflow_state['matched_scholarships'] = response.output
        self.workflow_state['step_3_complete'] = True
    
    async def _step_4_financial_analysis(self):
        """Step 4: Financial research and calculation"""
        
        matched_scholarships = self.workflow_state.get('matched_scholarships')
        student_data = self.workflow_state.get('student_classification_result')
        
        if not matched_scholarships:
            print("No matched scholarships for financial analysis")
            return
        
        financial_prompt = f"""
        Tính toán chi tiết tài chính cho các học bổng phù hợp:
        
        Học bổng phù hợp:
        {matched_scholarships}
        
        Thông tin học sinh:
        {student_data}
        
        Sử dụng web search để tìm thông tin học phí, trợ cấp chính phủ, và chi phí sinh hoạt.
        Sau đó sử dụng financial calculation tool để tính toán chi phí ròng.
        """
        
        response = await self.financial_research_agent.run(financial_prompt)
        self.workflow_state['financial_analysis'] = response.output
        self.workflow_state['step_4_complete'] = True
    
    async def _step_5_comprehensive_counseling(self) -> str:
        """Step 5: Comprehensive counseling and final recommendations"""
        
        # Gather all previous results
        all_data = {
            'structured_input': self.workflow_state.get('structured_input'),
            'scholarship_research': self.workflow_state.get('scholarship_research_result'),
            'student_classification': self.workflow_state.get('student_classification_result'),
            'profile_analysis': self.workflow_state.get('profile_analysis_result'),
            'matched_scholarships': self.workflow_state.get('matched_scholarships'),
            'financial_analysis': self.workflow_state.get('financial_analysis')
        }
        
        counseling_prompt = f"""
        Tổng hợp tất cả thông tin để tạo báo cáo tư vấn du học toàn diện:
        
        Dữ liệu đầu vào: {all_data['structured_input']}
        Kết quả nghiên cứu học bổng: {all_data['scholarship_research']}
        Phân loại học sinh: {all_data['student_classification']}
        Phân tích hồ sơ: {all_data['profile_analysis']}
        Học bổng phù hợp: {all_data['matched_scholarships']}
        Phân tích tài chính: {all_data['financial_analysis']}
        
        Tạo báo cáo tư vấn đầy đủ với cấu trúc:
        1. Tóm tắt tổng quan
        2. Top 3-5 học bổng được khuyến nghị
        3. Phân tích tài chính và kế hoạch tài trợ
        4. Kế hoạch cải thiện hồ sơ
        5. Chiến lược nộp đơn và timeline
        6. Yêu cầu pháp lý (visa, giấy tờ)
        7. Kế hoạch dự phòng
        
        Sử dụng send_email_tool để gửi nhắc nhở về các mốc thời gian quan trọng nếu cần.
        """
        
        response = await self.comprehensive_counseling_agent.run(counseling_prompt)
        self.workflow_state['final_counseling_report'] = response.output
        self.workflow_state['step_5_complete'] = True
        
        return str(response.output)
    
    def _extract_structured_data_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract structured data from coordinator agent response"""
        
        # Try to extract JSON if present
        import re
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        json_matches = re.findall(json_pattern, response_text)
        
        if json_matches:
            try:
                return json.loads(json_matches[0])
            except json.JSONDecodeError:
                pass
        
        # Fallback to keyword extraction
        lines = response_text.split('\n')
        extracted_data = {
            'target_university': 'Unknown',
            'target_location': 'Unknown', 
            'target_field': 'Unknown',
            'student_profile': response_text
        }
        
        # Simple keyword extraction
        for line in lines:
            line_lower = line.lower()
            if 'trường' in line_lower or 'university' in line_lower:
                extracted_data['target_university'] = line.strip()
            elif 'quốc gia' in line_lower or 'country' in line_lower:
                extracted_data['target_location'] = line.strip()
            elif 'ngành' in line_lower or 'field' in line_lower:
                extracted_data['target_field'] = line.strip()
        
        return extracted_data

# Initialize the counseling system
counseling_system = StudyAbroadCounselingSystem()

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    await cl.Message(
        content="""🎓 **Chào mừng đến với Hệ thống Tư vấn Du học Thông minh!**

Tôi là hệ thống AI đa tác tử chuyên nghiệp giúp bạn:
✅ Tìm kiếm học bổng phù hợp
✅ Phân tích hồ sơ cá nhân  
✅ Tính toán chi phí du học
✅ Lập kế hoạch tài chính
✅ Tư vấn chiến lược nộp đơn

**Để bắt đầu, vui lòng cung cấp thông tin sau:**
- Trường đại học/quốc gia bạn muốn học
- Ngành học quan tâm
- Thông tin về bản thân (học lực, chứng chỉ, hoạt động ngoại khóa...)

Tôi sẽ phân tích toàn diện và đưa ra lời tư vấn chi tiết nhất! 🚀"""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    
    # Add context from memory
    message_with_context = counseling_system.memory_handler.get_history_message(message.content)
    
    try:
        # Show processing message
        processing_msg = await cl.Message(content="🔍 Đang phân tích yêu cầu của bạn qua 5 bước xử lý với 6 agent chuyên nghiệp...").send()
        
        # Process the counseling request
        response = await counseling_system.process_counseling_request(message_with_context)
        
        # Update processing message
        processing_msg.content = "✅ Hoàn thành phân tích!"
        await processing_msg.update()
        
        # Store bot response in memory
        counseling_system.memory_handler.store_bot_response(response)
        
        # Send final response
        await cl.Message(content=response).send()
        
    except Exception as e:
        # Store error in memory
        counseling_system.memory_handler.store_error(e)
        
        # Send error message
        await cl.Message(
            content=f"""❌ **Đã xảy ra lỗi trong quá trình xử lý**

Lỗi: {str(e)}

🔄 **Vui lòng thử lại hoặc:**
- Cung cấp thêm thông tin chi tiết
- Kiểm tra kết nối internet
- Liên hệ hỗ trợ nếu lỗi tiếp tục xảy ra

Tôi sẵn sàng hỗ trợ bạn! 💪"""
        ).send()

if __name__ == "__main__":
    print("Study Abroad Counseling System initialized successfully!")
    print("Run with: chainlit run workflow/sample.py")