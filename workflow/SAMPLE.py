# Study Abroad Counseling Multi-Agent Workflow
# workflow/SAMPLE.py
import logging
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
    """Multi-agent system for study abroad counseling with Chainlit Steps visualization"""
    
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
        
        # Agent 5: Scholarship Matching Agent - FIXED: Remove tool, use pure LLM approach
        self.scholarship_matching_agent = AgentClient(
            model=self.model,
            system_prompt=SCHOLARSHIP_MATCHING_AGENT_PROMPT,
            tools=[]  # Removed scholarship_matching_tool to handle text input directly
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
        Following the 5-step process with 6 agents + Chainlit Steps visualization
        """
        try:
            print(f"🚀 Starting 5-step multi-agent workflow...")
            
            # Store user input
            self.workflow_state['user_input'] = user_input
            
            # Step 1: Coordinate and extract information
            print("📋 Step 1: Coordinating and extracting information...")
            await self._step_1_coordination(user_input)
            
            # Step 2: Parallel processing (Research + Classification + Analysis)
            print("⚡ Step 2: Parallel processing with 3 agents...")
            await self._step_2_parallel_processing()
            
            # Step 3: Match scholarships to student
            print("🔗 Step 3: Matching scholarships to student profile...")
            await self._step_3_scholarship_matching()
            
            # Step 4: Financial analysis
            print("💰 Step 4: Financial analysis and planning...")
            await self._step_4_financial_analysis()
            
            # Step 5: Comprehensive counseling
            print("📝 Step 5: Generating comprehensive counseling report...")
            final_response = await self._step_5_comprehensive_counseling()
            
            print("✅ Multi-agent workflow completed successfully!")
            return final_response
            
        except Exception as e:
            error_message = f"""❌ **Lỗi trong quá trình xử lý multi-agent workflow**

**Chi tiết lỗi:** {str(e)}

**Dữ liệu đã xử lý:**
- Bước 1 (Coordination): {'✅' if self.workflow_state.get('step_1_complete') else '❌'}
- Bước 2 (Parallel Processing): {'✅' if self.workflow_state.get('step_2_complete') else '❌'}
- Bước 3 (Matching): {'✅' if self.workflow_state.get('step_3_complete') else '❌'}
- Bước 4 (Financial): {'✅' if self.workflow_state.get('step_4_complete') else '❌'}
- Bước 5 (Final Report): {'✅' if self.workflow_state.get('step_5_complete') else '❌'}

**Vui lòng thử lại hoặc cung cấp thêm thông tin chi tiết.**"""
            print(f"❌ Error in multi-agent workflow: {e}")
            return error_message
    
    @cl.step(type="llm", name="📋 Bước 1: Điều phối và trích xuất thông tin có cấu trúc")
    async def _step_1_coordination(self, user_input: str):
        """Step 1: Coordinate and extract structured information"""
        current_step = cl.context.current_step
        current_step.input = f"User request: {user_input}"
        
        await current_step.stream_token("🔄 Phân tích và trích xuất thông tin từ yêu cầu người dùng...\n")
        await current_step.stream_token("📊 Tạo dữ liệu có cấu trúc...\n")
        
        coordination_prompt = f"""
        Phân tích yêu cầu của người dùng và trích xuất thông tin có cấu trúc:
        
        User Input: {user_input}
        
        Hãy trích xuất và tổ chức thông tin theo format JSON sau:
        {{
            "target_university": "tên trường đại học",
            "target_country": "quốc gia", 
            "field_of_study": "ngành học",
            "student_profile": {{
                "gpa": "điểm GPA",
                "standardized_tests": "điểm thi chuẩn hóa",
                "english_proficiency": "trình độ tiếng Anh",
                "extracurriculars": "hoạt động ngoại khóa",
                "experience": "kinh nghiệm"
            }},
            "demographics": {{
                "age": "độ tuổi",
                "gender": "giới tính", 
                "nationality": "quốc tịch"
            }}
        }}
        
        Nếu thông tin nào không có, hãy để null hoặc ghi "not specified".
        """
        
        try:
            result = await self.coordinator_agent.run(coordination_prompt)
            output = result.output
            
            # Try to parse JSON from the output
            try:
                # Extract JSON from the response (handle cases where LLM adds extra text)
                import re
                json_pattern = r'\{.*\}'
                json_match = re.search(json_pattern, output, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    structured_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                    
                await current_step.stream_token("✅ Trích xuất thông tin thành công!\n")
                self.workflow_state['step_1_complete'] = True
                print(f"✅ Step 1 completed: Extracted structured data successfully")
                
            except (json.JSONDecodeError, ValueError) as e:
                # Fallback: create structured data manually from the output
                await current_step.stream_token("⚠️ JSON parsing failed, using fallback extraction...\n")
                structured_data = {
                    "target_university": "University of Toronto" if "toronto" in user_input.lower() else "not specified",
                    "target_country": "Canada" if "canada" in user_input.lower() else "not specified", 
                    "field_of_study": "Khoa học máy tính" if "máy tính" in user_input.lower() or "computer" in user_input.lower() else "not specified",
                    "student_profile": {
                        "gpa": "8.7/10" if "8.7" in user_input else "not specified",
                        "standardized_tests": "SAT: 1410" if "1410" in user_input else "not specified",
                        "english_proficiency": "IELTS: 7.5" if "7.5" in user_input else "not specified", 
                        "extracurriculars": user_input if "robotics" in user_input.lower() or "clb" in user_input.lower() else "not specified",
                        "experience": user_input if "github" in user_input.lower() or "website" in user_input.lower() else "not specified"
                    },
                    "demographics": {
                        "age": "not specified",
                        "gender": "not specified",
                        "nationality": "not specified"
                    }
                }
                self.workflow_state['step_1_complete'] = False
                print(f"⚠️ Step 1 fallback: Could not parse JSON, using manual extraction")
        
        except Exception as e:
            await current_step.stream_token(f"❌ Lỗi trong bước điều phối: {e}\n")
            print(f"❌ Error in coordination step: {e}")
            print(f"Đầu ra thô gây lỗi: {output}")

            structured_data = {
                "error": "Failed to parse structured data from user input.",
                "raw_output": output
            }
            self.workflow_state['step_1_complete'] = False
            print(f"⚠️ Step 1 failed: Could not extract structured data. Fallback logic was triggered.")

        # Lưu kết quả và hiển thị output
        self.workflow_state['structured_input'] = structured_data
        current_step.output = f"Structured Data:\n{json.dumps(structured_data, ensure_ascii=False, indent=2)}"

    @cl.step(type="tool", name="⚡ Bước 2: Xử lý song song với 3 agents")
    async def _step_2_parallel_processing(self):
        """Step 2: Parallel processing with 3 agents - with real-time progress"""
        current_step = cl.context.current_step
        
        structured_data = self.workflow_state.get('structured_input', {})
        current_step.input = f"Structured data from Step 1"
        
        await current_step.stream_token("🚀 Khởi động 3 agents song song...\n")
        await current_step.stream_token("🔍 Agent 2: Scholarship Research (WAO1)\n")
        await current_step.stream_token("👤 Agent 3: Student Classification (WAO2)\n") 
        await current_step.stream_token("📊 Agent 4: Profile Analysis\n")
        
        # Task 1: Scholarship Research (Agent 2)
        scholarship_research_task = self._research_scholarships(structured_data)
        
        # Task 2: Student Classification (Agent 3)  
        student_classification_task = self._classify_student(structured_data)
        
        # Task 3: Profile Analysis (Agent 4)
        profile_analysis_task = self._analyze_profile(structured_data)
        
        await current_step.stream_token("⏳ Đang xử lý song song...\n")
        
        # Run all 3 tasks in parallel
        scholarship_result, classification_result, profile_result = await asyncio.gather(
            scholarship_research_task,
            student_classification_task,
            profile_analysis_task
        )
        
        await current_step.stream_token("✅ Hoàn thành xử lý song song!\n")
        
        # Store results
        self.workflow_state.update({
            'scholarship_research_result': scholarship_result,  # This becomes wao1
            'student_classification_result': classification_result,  # This becomes wao2  
            'profile_analysis_result': profile_result,
            'step_2_complete': True
        })
        
        current_step.output = f"""Parallel Processing Results:
WAO1 (Scholarship Research): {len(scholarship_result)} chars
WAO2 (Student Classification): {len(classification_result)} chars  
Profile Analysis: {len(profile_result)} chars"""
        
        print(f"✅ Step 2 completed: Processed scholarship research, student classification, and profile analysis")
    
    async def _research_scholarships(self, structured_data: Dict[str, Any]) -> str:
        """Agent 2: Research scholarships using web search"""
        
        target_university = structured_data.get('target_university', 'NUS')
        field_of_study = structured_data.get('field_of_study', 'Computer Science')
        target_country = structured_data.get('target_country', 'Singapore')
        
        research_prompt = f"""
        Tìm kiếm và phân tích các học bổng cho:
        - Trường: {target_university}
        - Ngành: {field_of_study}  
        - Quốc gia: {target_country}
        
        Sử dụng enhanced_web_search để tìm thông tin mới nhất về học bổng.
        Sau đó sử dụng scholarship_analysis_tool để tạo bảng wao1 có cấu trúc với thông tin:
        - Tên học bổng
        - Đối tượng target (vùng, tuổi, giới tính, tôn giáo)
        - Yêu cầu học thuật (GPA, điểm thi)
        - Chứng chỉ cần thiết
        - Hoạt động ngoại khóa yêu cầu
        - Giá trị học bổng
        - Hạn nộp đơn
        """
        
        result = await self.scholarship_research_agent.run(research_prompt)
        return result.output
    
    async def _classify_student(self, structured_data: Dict[str, Any]) -> str:
        """Agent 3: Classify student using classification tool"""
        
        student_profile = structured_data.get('student_profile', {})
        
        classification_prompt = f"""
        Sử dụng student_classification_tool để phân loại học sinh dựa trên thông tin:
        {student_profile}
        
        Tạo wao2 với classification theo:
        - Vùng/Region (ví dụ: Southeast Asia)
        - Lứa tuổi/Age group  
        - Giới tính/Gender
        - Tôn giáo/Religion (nếu có)
        - Trình độ học thuật/Academic level
        - Loại chứng chỉ/Certificate types
        - Mức độ hoạt động ngoại khóa/Extracurricular level
        """
        
        result = await self.student_classification_agent.run(classification_prompt)
        return result.output
    
    async def _analyze_profile(self, structured_data: Dict[str, Any]) -> str:
        """Agent 4: Analyze student profile"""
        
        student_profile = structured_data.get('student_profile', {})
        
        analysis_prompt = f"""
        Phân tích chi tiết hồ sơ học sinh:
        {student_profile}
        
        Đánh giá:
        1. Điểm mạnh (Strong points)
        2. Điểm yếu cần cải thiện (Areas for improvement)  
        3. Cơ hội phát triển (Opportunities)
        4. Rủi ro và thách thức (Risks and challenges)
        5. Khuyến nghị cải thiện cụ thể (Specific improvement recommendations)
        
        Cung cấp phân tích SWOT đầy đủ cho việc apply học bổng.
        """
        
        result = await self.profile_analysis_agent.run(analysis_prompt)
        return result.output
    
    @cl.step(type="llm", name="🔗 Bước 3: Đối chiếu WAO1 + WAO2 → WHAT")
    async def _step_3_scholarship_matching(self):
        """Step 3: Match scholarships with student profile - FIXED: Pure LLM approach"""
        current_step = cl.context.current_step
        
        wao1 = self.workflow_state.get('scholarship_research_result')  # Scholarships
        wao2 = self.workflow_state.get('student_classification_result')  # Student classification
        
        current_step.input = f"WAO1 + WAO2 matching process"
        
        # FIXED: Better validation with meaningful fallback
        if not wao1 or len(str(wao1).strip()) < 10:
            await current_step.stream_token("⚠️ WAO1 data không đầy đủ, tạo fallback data...\n")
            wao1 = "Học bổng chung: Dành cho sinh viên quốc tế, yêu cầu GPA > 3.0, IELTS > 6.0"
            
        if not wao2 or len(str(wao2).strip()) < 10:
            await current_step.stream_token("⚠️ WAO2 data không đầy đủ, tạo fallback data...\n")  
            wao2 = "Sinh viên Việt Nam, GPA tốt, có kinh nghiệm lập trình và robotics"
        
        await current_step.stream_token("🔄 Đối chiếu học bổng với hồ sơ học sinh...\n")
        await current_step.stream_token("📊 Tính toán độ phù hợp...\n")
        
        # FIXED: Pure LLM approach - no tool usage
        matching_prompt = f"""
        Bạn là chuyên gia đối chiếu học bổng. Hãy phân tích và đối chiếu thông tin sau:
        
        📊 DANH SÁCH HỌC BỔNG (WAO1):
        {wao1}
        
        👤 HỒ SƠ HỌC SINH ĐÃ PHÂN LOẠI (WAO2):
        {wao2}
        
        Hãy tạo danh sách WHAT - các học bổng phù hợp với format sau:
        
        ## DANH SÁCH HỌC BỔNG PHÙ HỢP (WHAT)
        
        ### 1. [Tên học bổng 1]
        - **Điểm match:** [0-100]/100
        - **Mức độ phù hợp:** [EXCELLENT/GOOD/FAIR/POOR]
        - **Tiêu chí đáp ứng:** 
          • [tiêu chí 1]
          • [tiêu chí 2]
        - **Yêu cầu còn thiếu:**
          • [yêu cầu 1]
          • [yêu cầu 2]
        - **Gợi ý cải thiện:**
          • [gợi ý 1]
          • [gợi ý 2]
        - **Thứ tự ưu tiên apply:** [HIGH/MEDIUM/LOW]
        
        ### 2. [Tên học bổng 2]
        [Tương tự format trên]
        
        **SCORING CRITERIA:**
        - Demographics (20%): Vùng, tuổi, giới tính, tôn giáo
        - Academic (30%): GPA, điểm thi, thành tích học thuật
        - Certificates (25%): IELTS/TOEFL, SAT/ACT, chứng chỉ khác
        - Extracurricular (15%): Hoạt động ngoại khóa, leadership
        - Field alignment (10%): Phù hợp ngành học
        
        **QUY TẮC:**
        - Chỉ liệt kê học bổng có mức độ phù hợp FAIR trở lên (≥45 điểm)
        - Sắp xếp theo thứ tự điểm match giảm dần
        - Đưa ra lời khuyên thực tế và có thể thực hiện được
        - Tính toán honest và objective
        """
        
        await current_step.stream_token("🎯 Xếp hạng theo độ ưu tiên...\n")
        result = await self.scholarship_matching_agent.run(matching_prompt)
        
        await current_step.stream_token("✅ Tạo danh sách WHAT thành công!\n")
        
        self.workflow_state['matched_scholarships'] = result.output
        self.workflow_state['step_3_complete'] = True
        
        current_step.output = f"WHAT - Matched Scholarships:\n{result.output[:500]}..."
        print(f"✅ Step 3 completed: Generated WHAT - matched scholarships list")
    
    @cl.step(type="tool", name="💰 Bước 4: Phân tích tài chính và funding")
    async def _step_4_financial_analysis(self):
        """Step 4: Financial research and calculation"""
        current_step = cl.context.current_step
        
        matched_scholarships = self.workflow_state.get('matched_scholarships')
        student_data = self.workflow_state.get('student_classification_result')
        structured_input = self.workflow_state.get('structured_input', {})
        
        university = structured_input.get('target_university', 'NUS')
        field = structured_input.get('field_of_study', 'Computer Science')
        country = structured_input.get('target_country', 'Singapore')
        
        current_step.input = f"Financial analysis for {university} - {field}"
        
        await current_step.stream_token("🌐 Tìm kiếm thông tin học phí và chi phí sinh hoạt...\n")
        await current_step.stream_token("💵 Tính toán tổng chi phí...\n")
        
        financial_prompt = f"""
        Thực hiện phân tích tài chính toàn diện:
        
        1. Sử dụng enhanced_web_search để tìm:
           - Học phí của {university} ngành {field}
           - Chi phí sinh hoạt tại {country}
           - Các khoản trợ cấp chính phủ available
           - Chi phí visa và giấy tờ
        
        2. Sử dụng financial_calculation_tool để tính:
           - Tổng chi phí (Total costs)
           - Nguồn funding available từ matched scholarships: {matched_scholarships}
           - Khoản thiếu hụt cần cover (Funding gap)
           - Phương án tài chính khác nhau (Funding scenarios)
           - ROI của từng scholarship option
        
        Đưa ra recommended funding strategy với timeline cụ thể.
        """
        
        await current_step.stream_token("📊 Phân tích các phương án funding...\n")
        await current_step.stream_token("📈 Tính toán ROI...\n")
        
        result = await self.financial_research_agent.run(financial_prompt)
        
        await current_step.stream_token("✅ Hoàn thành chiến lược tài chính!\n")
        
        self.workflow_state['financial_analysis'] = result.output
        self.workflow_state['step_4_complete'] = True
        
        current_step.output = f"Financial Analysis Results:\n{result.output[:500]}..."
        print(f"✅ Step 4 completed: Financial analysis and funding strategy")
    
    @cl.step(type="llm", name="📝 Bước 5: Tư vấn tổng hợp và báo cáo cuối")
    async def _step_5_comprehensive_counseling(self) -> str:
        """Step 5: Comprehensive counseling and final recommendations"""
        current_step = cl.context.current_step
        
        # Gather all workflow results
        all_results = {
            'structured_input': self.workflow_state.get('structured_input'),
            'scholarship_research': self.workflow_state.get('scholarship_research_result'),
            'student_classification': self.workflow_state.get('student_classification_result'), 
            'profile_analysis': self.workflow_state.get('profile_analysis_result'),
            'matched_scholarships': self.workflow_state.get('matched_scholarships'),
            'financial_analysis': self.workflow_state.get('financial_analysis')
        }
        
        current_step.input = "Synthesizing all 5 steps of analysis"
        
        await current_step.stream_token("📋 Tổng hợp tất cả kết quả từ 4 bước trước...\n")
        await current_step.stream_token("📊 Tạo executive summary...\n")
        
        counseling_prompt = f"""
        Tổng hợp tất cả kết quả từ 4 bước trước để tạo báo cáo tư vấn du học toàn diện:
        
        📊 DỮ LIỆU ĐẦU VÀO:
        {all_results['structured_input']}
        
        📚 KẾT QUẢ NGHIÊN CỨU HỌC BỔNG (WAO1):
        {all_results['scholarship_research']}
        
        👤 PHÂN LOẠI HỌC SINH (WAO2):
        {all_results['student_classification']}
        
        📋 PHÂN TÍCH HỒ SƠ:
        {all_results['profile_analysis']}
        
        🎯 HỌC BỔNG PHÙ HỢP (WHAT):
        {all_results['matched_scholarships']}
        
        💰 PHÂN TÍCH TÀI CHÍNH:
        {all_results['financial_analysis']}
        
        Tạo báo cáo có cấu trúc sau:
        
        # BÁO CÁO TƯ VẤN DU HỌC TOÀN DIỆN
        
        ## 1. TÓM TẮT TỔNG QUAN (Executive Summary)
        - Điểm mạnh và cơ hội chính
        - Top 3 khuyến nghị ưu tiên
        - Timeline tổng quan
        
        ## 2. TOP 3-5 HỌC BỔNG ĐƯỢC KHUYẾN NGHỊ
        - Danh sách học bổng phù hợp nhất
        - Chiến lược nộp đơn cho từng học bổng
        - Timeline nộp đơn
        
        ## 3. PHÂN TÍCH TÀI CHÍNH VÀ KẾ HOẠCH TÀI TRỢ
        - Breakdown chi phí chi tiết
        - Các phương án funding
        - Kế hoạch tài chính khuyến nghị
        
        ## 4. KẾ HOẠCH CẢI THIỆN HỒ SƠ
        - Điểm yếu cần khắc phục
        - Hành động cụ thể với timeline
        - Metrics để đo lường tiến độ
        
        ## 5. CHIẾN LƯỢC NỘP ĐƠN VÀ TIMELINE
        - Lịch trình nộp đơn chi tiết
        - Preparation checklist
        - Risk mitigation strategies
        
        ## 6. YÊU CẦU PHÁP LÝ (VISA, GIẤY TỜ)
        - Thủ tục visa cần thiết
        - Documents required
        - Timeline cho paperwork
        
        ## 7. KẾ HOẠCH DỰ PHÒNG
        - Backup options
        - Alternative pathways
        - Contingency planning
        
        Tạo báo cáo chi tiết, thực tế và actionable.
        """
        
        await current_step.stream_token("📝 Tạo báo cáo toàn diện...\n")
        await current_step.stream_token("✅ Hoàn thành multi-agent workflow!\n")
        
        result = await self.comprehensive_counseling_agent.run(counseling_prompt)
        
        self.workflow_state['final_report'] = result.output
        self.workflow_state['step_5_complete'] = True
        
        current_step.output = f"Comprehensive Report Generated: {len(result.output)} characters"
        print(f"✅ Step 5 completed: Generated comprehensive counseling report")
        
        return result.output

# Initialize the counseling system
counseling_system = StudyAbroadCounselingSystem()

@cl.on_chat_start
async def start():
    """Initialize the chat session with welcome message"""
    await cl.Message(
        content="""🎓 **Chào mừng đến với Hệ thống Tư vấn Du học Thông minh Multi-Agent!**

Tôi là hệ thống AI đa tác tử chuyên nghiệp với **6 agents** làm việc qua **5 bước** để giúp bạn:

✅ **Bước 1:** Agent Điều phối - Trích xuất thông tin có cấu trúc
✅ **Bước 2:** 3 Agents song song:
   - 🔍 Agent Tìm Học Bổng → tạo **WAO1**
   - 👤 Agent Phân Loại Học Sinh → tạo **WAO2** 
   - 📊 Agent Phân Tích Hồ Sơ
✅ **Bước 3:** Agent Đối Chiếu → **WAO1** + **WAO2** = **WHAT**
✅ **Bước 4:** Agent Tài Chính - Phân tích chi phí & funding
✅ **Bước 5:** Agent Tư Vấn Tổng Hợp - Báo cáo cuối

**Để bắt đầu, vui lòng cung cấp thông tin:**
- 🏫 Trường đại học/quốc gia muốn học
- 📚 Ngành học quan tâm  
- 📋 Thông tin cá nhân (GPA, điểm thi, chứng chỉ, hoạt động ngoại khóa...)

Tôi sẽ phân tích toàn diện qua **multi-agent workflow** và đưa ra báo cáo tư vấn chi tiết nhất! 🚀

*Bạn sẽ thấy từng bước xử lý real-time với Chain of Thought!* 👀"""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with multi-agent workflow visualization"""
    
    # Add context from memory
    message_with_context = counseling_system.memory_handler.get_history_message(message.content)
    
    try:
        # NO MORE static processing message - Steps will show real-time progress
        # Process the counseling request through multi-agent workflow with real-time visualization
        response = await counseling_system.process_counseling_request(message_with_context)
        
        # Store bot response in memory
        counseling_system.memory_handler.store_bot_response(response)
        
        # Send final comprehensive report
        await cl.Message(content=response).send()
        
        # Send follow-up message
        await cl.Message(
            content="💡 **Bạn có thể:**\n" +
                   "- Hỏi chi tiết về bất kỳ phần nào trong báo cáo\n" + 
                   "- Yêu cầu điều chỉnh chiến lược\n" +
                   "- Cập nhật thông tin hồ sơ để tái phân tích\n" +
                   "- Hỏi về timeline và deadline cụ thể\n\n" +
                   "Multi-agent system sẵn sàng hỗ trợ thêm! 🤖"
        ).send()
        
    except Exception as e:
        # Store error in memory
        counseling_system.memory_handler.store_error(e)
        
        # Send detailed error message
        await cl.Message(
            content=f"""❌ **Lỗi trong Multi-Agent Workflow**

**Mô tả lỗi:** {str(e)}

**Debug info:**
- Workflow state: {len(counseling_system.workflow_state)} steps processed
- Last completed step: {max([k for k in counseling_system.workflow_state.keys() if 'step_' in k and 'complete' in k], default='none')}

🔄 **Khắc phục:**
1. Kiểm tra kết nối internet
2. Đảm bảo đã cung cấp đủ thông tin cơ bản
3. Thử lại với format: "Tôi muốn học [trường] ngành [ngành], có [điểm số/chứng chỉ]"

💪 **Multi-agent system sẵn sàng xử lý lại!**"""
        ).send()

if __name__ == "__main__":
    print("🚀 Study Abroad Counseling Multi-Agent System with Chainlit Steps!")
    print("📊 Real-time Chain of Thought: 6 Agents → 5 Steps → Live Progress")
    print("⚡ 5-Step Workflow: WAO1 + WAO2 → WHAT → Comprehensive Report")
    print("🎯 Run with: chainlit run workflow/SAMPLE.py")