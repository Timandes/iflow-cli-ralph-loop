#!/usr/bin/env python3
"""
iFlow CLI Ralph Loop - 迭代式提示词处理工具

从标准输入获取prompt，持续获取iflow cli响应直到完结或检测到关键词，
反复迭代直到达到最大迭代次数或检测到完成关键词。
"""

import sys
import asyncio
import argparse
from iflow_sdk import IFlowClient, IFlowOptions


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="iFlow CLI Ralph Loop - 迭代式提示词处理工具"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="最大迭代次数（默认：10）"
    )
    parser.add_argument(
        "--completion-promise",
        type=str,
        default="ALL-DONE",
        help="完成关键词（默认：ALL-DONE）"
    )
    return parser.parse_args()


async def main():
    """主函数"""
    args = parse_arguments()
    
    # 从标准输入读取完整的prompt
    print("请输入prompt（按Ctrl+D结束输入）：", file=sys.stderr)
    prompt = sys.stdin.read()
    
    if not prompt.strip():
        print("错误：prompt不能为空", file=sys.stderr)
        sys.exit(1)
    
    # 初始化iflow客户端，使用YOLO模式
    options = IFlowOptions()
    
    max_iterations = args.max_iterations
    completion_promise = args.completion_promise
    
    print(f"开始迭代处理，最大迭代次数：{max_iterations}", file=sys.stderr)
    print(f"完成关键词：{completion_promise}", file=sys.stderr)
    print("-" * 50, file=sys.stderr)
    
    # 迭代处理
    for iteration in range(1, max_iterations + 1):
        print(f"\n[迭代 {iteration}/{max_iterations}]", file=sys.stderr)
        print(f"发送prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)
        
        # 每轮迭代创建新的客户端并连接
        client = IFlowClient(options=options)
        
        # 连接到iflow
        try:
            await client.connect()
        except Exception as e:
            print(f"错误：连接iflow失败: {e}", file=sys.stderr)
            sys.exit(1)
        
        # 发送消息
        try:
            await client.send_message(prompt)
        except Exception as e:
            print(f"错误：发送消息失败: {e}", file=sys.stderr)
            await client.disconnect()
            sys.exit(1)
        
        # 接收响应
        response_text = ""
        try:
            async for message in client.receive_messages():
                # 检查是否是TaskFinishMessage（任务完成）
                from iflow_sdk.types import TaskFinishMessage
                if isinstance(message, TaskFinishMessage):
                    # 收到TaskFinishMessage，只停止本轮迭代
                    print(f"\n检测到TaskFinishMessage: {message.stop_reason}", file=sys.stderr)
                    break
                
                # 提取消息文本
                msg_text = ""
                if hasattr(message, 'content'):
                    msg_text = str(message.content)
                elif hasattr(message, 'text'):
                    msg_text = str(message.text)
                elif hasattr(message, 'chunk') and hasattr(message.chunk, 'text'):
                    msg_text = str(message.chunk.text)
                elif hasattr(message, 'markdown'):
                    msg_text = str(message.markdown)
                else:
                    msg_text = str(message)
                
                response_text += msg_text
                
                # 输出消息内容
                print(msg_text)
                
                # 检查是否包含完成关键词（自动添加<promise>标签）
                promise_tag = f"<promise>{completion_promise}</promise>"
                if promise_tag in response_text:
                    print(f"\n检测到完成关键词：{completion_promise}", file=sys.stderr)
                    print(completion_promise)
                    await client.disconnect()
                    return
        except Exception as e:
            print(f"错误：接收消息失败: {e}", file=sys.stderr)
            await client.disconnect()
            sys.exit(1)
        
        # 断开连接
        await client.disconnect()
        
        # 将响应作为下一轮的prompt继续迭代
        prompt = response_text
    
    # 达到最大迭代次数
    print(f"\n达到最大迭代次数：{max_iterations}", file=sys.stderr)
    print(completion_promise)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())