import asyncio
import uuid
from agent.graph import graph

async def main():
    # 1. Giả lập thông tin người dùng (Frontend gửi xuống)
    user_info_mock = {
        "full_name": "Lục Thới Trọng",
        "role": "ROLE_STUDENT",
        "user_id": "22110254",
    }

    # 2. Config thread_id (Session ID)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"--- Bắt đầu hội thoại (Thread ID: {thread_id}) ---")

    # 3. Vòng lặp chat
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # 4. Gửi input vào Graph
        # Lưu ý: Truyền user_info vào input state
        input_state = {
            "messages": [("user", user_input)],
            "user_info": user_info_mock
        }

        # Dùng astream để nhận phản hồi (hoặc ainvoke nếu không cần stream)
        async for event in graph.astream(input_state, config=config, stream_mode="values"):
            # Lấy tin nhắn cuối cùng để in ra
            message = event["messages"][-1]
            if message.type == "ai":
                print(f"Bot: {message.content}")
                # Nếu có tool call thì in ra cho dễ debug
                if message.tool_calls:
                    print(f"   [System] Đang gọi tool: {message.tool_calls[0]['name']}")

if __name__ == "__main__":
    asyncio.run(main())