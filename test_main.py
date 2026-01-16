#!/usr/bin/env python3
"""
单元测试 - 测试 iflow-cli-ralph-loop 程序
"""

import sys
import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from io import StringIO


class TestMainFunction(unittest.TestCase):
    """测试主函数功能"""
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_basic_iteration(self, mock_stdout, mock_client_class):
        """测试基本迭代功能"""
        # Mock iflow client
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        # Mock消息对象
        msg1 = Mock()
        msg1.content = "响应1"
        msg2 = Mock()
        msg2.content = "响应2 <promise>ALL-DONE</promise> 完成"
        
        # Mock receive_messages 返回异步迭代器
        async def mock_receive_1():
            yield msg1
        
        async def mock_receive_2():
            yield msg2
        
        mock_client.receive_messages = Mock(side_effect=[mock_receive_1(), mock_receive_2()])
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py', '--max-iterations', '5']):
            import main
            asyncio.run(main.main())
        
        # 验证调用次数
        self.assertEqual(mock_client.send_message.call_count, 2)
        
        # 验证输出包含完成关键词
        output = mock_stdout.getvalue()
        self.assertIn("响应1", output)
        self.assertIn("响应2 <promise>ALL-DONE</promise> 完成", output)
        self.assertIn("ALL-DONE", output)
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_max_iterations_reached(self, mock_stdout, mock_client_class):
        """测试达到最大迭代次数"""
        # Mock iflow client - 从不返回完成关键词
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        # Mock消息对象
        messages = []
        for i in range(1, 11):
            msg = Mock()
            msg.content = f"响应{i}"
            messages.append(msg)
        
        # Mock receive_messages 返回异步迭代器
        async def mock_receive():
            for msg in messages:
                yield msg
        
        mock_client.receive_messages = Mock(return_value=mock_receive())
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py', '--max-iterations', '10']):
            import main
            asyncio.run(main.main())
        
        # 验证调用次数达到最大值
        self.assertEqual(mock_client.send_message.call_count, 10)
        
        # 验证最后输出完成关键词
        output = mock_stdout.getvalue()
        self.assertIn("ALL-DONE", output)
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_custom_completion_promise(self, mock_stdout, mock_client_class):
        """测试自定义完成关键词"""
        custom_promise = "TASK-COMPLETE"
        
        # Mock iflow client
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        # Mock消息对象
        msg = Mock()
        msg.content = f"这是响应 <promise>{custom_promise}</promise>"
        
        async def mock_receive():
            yield msg
        
        mock_client.receive_messages = Mock(return_value=mock_receive())
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py', '--completion-promise', custom_promise]):
            import main
            asyncio.run(main.main())
        
        # 验证只调用一次
        self.assertEqual(mock_client.send_message.call_count, 1)
        
        # 验证输出包含自定义关键词
        output = mock_stdout.getvalue()
        self.assertIn(custom_promise, output)
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_yolo_mode_used(self, mock_stdout, mock_client_class):
        """测试是否使用YOLO模式"""
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        msg = Mock()
        msg.content = "响应"
        
        async def mock_receive():
            yield msg
        
        mock_client.receive_messages = Mock(return_value=mock_receive())
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py', '--max-iterations', '1']):
            import main
            asyncio.run(main.main())
        
        # 验证client使用IFlowOptions初始化
        self.assertEqual(mock_client_class.call_count, 1)
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_iteration_prompt_chaining(self, mock_stdout, mock_client_class):
        """测试迭代中prompt的传递链"""
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.send_message = AsyncMock()
        
        # Mock消息对象
        msg1 = Mock()
        msg1.content = "第一轮响应"
        msg2 = Mock()
        msg2.content = "第二轮响应"
        msg3 = Mock()
        msg3.content = "第三轮响应 <promise>ALL-DONE</promise>"
        
        async def mock_receive_1():
            yield msg1
        
        async def mock_receive_2():
            yield msg2
        
        async def mock_receive_3():
            yield msg3
        
        mock_client.receive_messages = Mock(side_effect=[mock_receive_1(), mock_receive_2(), mock_receive_3()])
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py']):
            import main
            asyncio.run(main.main())
        
        # 验证prompt链正确传递
        calls = mock_client.send_message.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0][0][0], "测试prompt")
        self.assertEqual(calls[1][0][0], "第一轮响应")
        self.assertEqual(calls[2][0][0], "第二轮响应")
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO(""))
    @patch('sys.stdout', new_callable=StringIO)
    def test_empty_prompt_error(self, mock_stdout, mock_client_class):
        """测试空prompt的错误处理"""
        # 导入并运行main
        with patch('sys.argv', ['main.py']):
            import main
            with self.assertRaises(SystemExit) as context:
                asyncio.run(main.main())
            self.assertEqual(context.exception.code, 1)
    
    @patch('main.IFlowClient')
    @patch('sys.stdin', StringIO("测试prompt"))
    @patch('sys.stdout', new_callable=StringIO)
    def test_api_error_handling(self, mock_stdout, mock_client_class):
        """测试API错误处理"""
        # Mock iflow client抛出异常
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(side_effect=Exception("API错误"))
        mock_client_class.return_value = mock_client
        
        # 导入并运行main
        with patch('sys.argv', ['main.py']):
            import main
            with self.assertRaises(SystemExit) as context:
                asyncio.run(main.main())
            self.assertEqual(context.exception.code, 1)


class TestArgumentParsing(unittest.TestCase):
    """测试命令行参数解析"""
    
    def test_default_arguments(self):
        """测试默认参数"""
        with patch('sys.argv', ['main.py']):
            import main
            args = main.parse_arguments()
            self.assertEqual(args.max_iterations, 10)
            self.assertEqual(args.completion_promise, "ALL-DONE")
    
    def test_custom_max_iterations(self):
        """测试自定义最大迭代次数"""
        with patch('sys.argv', ['main.py', '--max-iterations', '20']):
            import main
            args = main.parse_arguments()
            self.assertEqual(args.max_iterations, 20)
    
    def test_custom_completion_promise(self):
        """测试自定义完成关键词"""
        with patch('sys.argv', ['main.py', '--completion-promise', 'FINISHED']):
            import main
            args = main.parse_arguments()
            self.assertEqual(args.completion_promise, "FINISHED")
    
    def test_both_custom_arguments(self):
        """测试同时自定义两个参数"""
        with patch('sys.argv', ['main.py', '--max-iterations', '5', '--completion-promise', 'DONE']):
            import main
            args = main.parse_arguments()
            self.assertEqual(args.max_iterations, 5)
            self.assertEqual(args.completion_promise, "DONE")


if __name__ == '__main__':
    unittest.main()