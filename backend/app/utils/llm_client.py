"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config


class LLMClient:
    """LLM客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        # Accumulated token usage across all calls on this instance
        self._tokens: Dict[str, int] = {"in": 0, "out": 0, "total": 0}

        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            
        Returns:
            模型响应文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        if response.usage:
            self._tokens['in'] += response.usage.prompt_tokens
            self._tokens['out'] += response.usage.completion_tokens
            self._tokens['total'] += response.usage.total_tokens
        return content
    
    def chat_with_image(
        self,
        image_base64: str,
        mime_type: str,
        prompt: str,
        max_tokens: int = 2048
    ) -> str:
        """
        Send a chat request with an inline base64-encoded image.

        Uses LLM_VISION_MODEL_NAME which should point to a vision-capable model
        (e.g. qwen-vl-plus on DashScope, gpt-4o on OpenAI).
        """
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                },
                {"type": "text", "text": prompt}
            ]
        }]
        response = self.client.chat.completions.create(
            model=Config.LLM_VISION_MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens
        )
        if response.usage:
            self._tokens['in'] += response.usage.prompt_tokens
            self._tokens['out'] += response.usage.completion_tokens
            self._tokens['total'] += response.usage.total_tokens
        return response.choices[0].message.content or ""

    def get_usage(self) -> Dict[str, int]:
        """Return accumulated token usage since creation or last reset_usage() call."""
        return dict(self._tokens)

    def reset_usage(self) -> None:
        """Reset accumulated token counts to zero."""
        self._tokens = {"in": 0, "out": 0, "total": 0}

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")

