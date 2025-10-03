import os
from dotenv import load_dotenv
from google import genai

from llm_abstraction import LLM
from base_agent import BaseAgent, JsonOutputParser
from tools import ToolManager, BaseTool, get_current_time, calculator, Final_Answer, run_sql_query
from agent_executor import AgentExecutor
from prompt_template import PromptTemplate


load_dotenv()

try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    print("Please make sure you have the GEMINI_API_KEY environment variable set.")
    exit()

if __name__ == "__main__":
    print("--- Initializing AI Agent Framework ---")

    # 1. Initialize the LLM Abstraction Layer
    llm = LLM(model_name="gemini-2.0-flash", client=client)

    # 2. Register Tools with the ToolManager
    tool_manager = ToolManager()
    calculator_tool = BaseTool(name="calculator", func=calculator)
    get_time_tool = BaseTool(name="get_time", func=get_current_time)
    final_answer = BaseTool(name="Final_Answer", func=Final_Answer)
    run_sql_query_tool = BaseTool(name="run_sql_query", func=run_sql_query)
    tool_manager.add_tool(run_sql_query_tool)
    tool_manager.add_tool(get_time_tool)
    tool_manager.add_tool(calculator_tool)
    tool_manager.add_tool(final_answer)

    # 3. Create the Prompt Template to inform the agent about its tools
    tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tool_manager.get_all_tools()])
    prompt_template = PromptTemplate(
        system_prompt=f"""
Bạn là một trợ lý phân tích dữ liệu chuyên nghiệp. Nhiệm vụ của bạn là giải quyết các vấn đề phức tạp bằng cách tạo ra một chuỗi các lệnh gọi công cụ.

Cấu trúc Dữ liệu
Tất cả dữ liệu từ các tệp CSV đã được hợp nhất vào một bảng duy nhất trong cơ sở dữ liệu SQLite.
Tên file: `sales_data.db`.
Tên table: `unified_sales_data`

Các cột trong bảng:
**`STT_Order`**: Số thứ tự giao dịch, đánh dấu thứ tự bản ghi.
**`Ngày_CT_Issue_date`**: Ngày phát hành chứng từ, định dạng `YYYY-MM-DD HH:MM:SS`.
**`Số_CT_Doc_Nbr`**: Mã chứng từ duy nhất, nhận diện giao dịch.
**`Hành_trình_Route`**: Lộ trình di chuyển hoặc thông tin giao dịch, có thể trống.
**`Nội_dung_Description`**: Mô tả chi tiết giao dịch (hành khách hoặc thanh toán).
**`Thông_tin_khác_Extra_Info`**: Thông tin bổ sung, thường là mã vé, có thể trống.

IMPORTANT, PAY MORE ATTENTION TO THIS
**`T`**: Loại giao dịch. **S** (bán vé) làm tăng công nợ. **D** (gửi tiền) làm giảm công nợ. **R** (hoàn tiền) và **V** (hủy giao dịch) cũng ảnh hưởng đến công nợ.

**`Curr`**: Loại tiền tệ, thường là `VND`.
**`Tỷ_giá_ROE`**: Tỷ giá hối đoái, thường là `1` cho `VND`.
**`Giá_vé_Ticket_Price`**: Giá vé cơ bản, `0` cho giao dịch không bán vé.
**`Thành_tiền_Total_Net`**: Giá trị thực tế sau phí và hoa hồng, ảnh hưởng công nợ.
**`Tiền_nợ`**: Số dư công nợ tích lũy sau mỗi giao dịch. Để tìm tổng công nợ cuối kỳ (ví dụ: cuối tháng), bạn cần lấy giá trị cuối cùng của cột này cho tháng đó.
**`Rmks`**: Ghi chú, chứa mã khách hàng hoặc thông tin liên quan, có thể trống.

Đây là ví dụ của bảng:
(3, '2025-01-02 00:00:00', 'VJAUM4QJY', 'HANVJSGNVJHAN', 'NGUYEN, NGOC MINH', 'UM4QJY / Y / Y', 'S', 'VND', 1, 4558000, 4568000, 99418392, 'KH05234')
(4, '2025-01-02 00:00:00', 'VJAYJZCP7', 'CXRVJHANVJCXR', 'HUYNH, THI NHI', 'YJZCP7 / Y / Y', 'S', 'VND', 1, 6674800, 6684800, 106103192, 'EMP1000041')
(5, '2025-01-03 00:00:00', 'UNT0103/00954', None, 'VCB - 020097041501030758462025udQz75966984972075846minh diep anh ck ()', ' ', 'D', 'VND', 1, 0, -60000000, 46103192, None)

Các ví dụ khác:
(5, '2025-02-04 00:00:00', '9264560319455', 'HOAN VE VOID-5I8JR7', 'NGUYEN/BAO KHANH MS', ' ', 'R', 'VND', 1, -300000, -300000, 1170612, None)
(82, '2025-07-23 00:00:00', '7382312984156', 'SGNVNHAN', 'TRAN/QUOC HUNG MR', 'F3NLUA / SVNF / S', 'R', 'VND', 1, -3495000, -3130000, 4239851, 'MDANH')



Năm nay là năm 2025.
Bạn có quyền truy cập vào các công cụ sau:
{tool_descriptions}

Hãy tự tin với câu trả lời của mình và luôn đưa ra kết quả cuối cùng mà bạn có
Bạn phải cung cấp một kế hoạch giải quyết hoàn toàn yêu cầu của người dùng.
""",
        user_input="{user_input}",
        history="{history}"
    )

    # 4. Create the Agent with the LLM
    agent = BaseAgent(llm=llm)

    # 5. Initialize the AgentExecutor with the Agent and ToolManager
    executor = AgentExecutor(agent=agent, tool_manager=tool_manager, prompt_template=prompt_template,max_iterations=1, dev_mode=True, json_output=True)

    print("\n--- Framework Initialized. Running Demo Task ---")

    # This prompt requires the agent to use two tools in a specific sequence.
    user_prompt = "Công nợ sau tháng 2 năm nay là bao nhiêu?"

    # 6. Run the AgentExecutor
    final_output, _ = executor.run(user_prompt)

    assert "31500082" in final_output, "wrong answer for eval 2"
    print("\n--- Evaluation Complete ---")
