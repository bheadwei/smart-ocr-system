"""
OpenAI Vision API service for OCR.
"""
import base64
import json
from typing import Dict, Any

from app.config import settings
from app.core.exceptions import OCRProcessingError


class OpenAIVisionService:
    """Service for OpenAI Vision API calls."""

    def __init__(self):
        """Initialize OpenAI client."""
        self._client = None

    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        return self._client

    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image using OpenAI Vision API.

        Args:
            image_data: Image bytes

        Returns:
            OCR result dict with extracted_text, structured_data, confidence
        """
        client = self._get_client()

        # Encode image to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")

        prompt = """請分析這張圖片中的文字內容。這是一份銀行代繳公用事業費用申請書。

請以 JSON 格式回傳結果，**必須**提取以下指定欄位：

{
  "extracted_text": "完整的辨識文字內容",
  "structured_data": {
    "type": "銀行代繳申請書",
    "fields": [
      {"key": "銀行名稱", "value": "銀行名稱", "confidence": 0.95},
      {"key": "戶名", "value": "申請人姓名", "confidence": 0.95},
      {"key": "身分證", "value": "身分證統一編號", "confidence": 0.95},
      {"key": "存款帳號", "value": "銀行存款帳號", "confidence": 0.95},
      {"key": "連絡電話", "value": "電話號碼(可能多筆)", "confidence": 0.95},
      {"key": "聯絡地址", "value": "完整地址", "confidence": 0.95},
      {"key": "電費", "value": "台電電費帳號/電號(共11碼)", "confidence": 0.95},
      {"key": "水費", "value": "水費帳號(台灣省共11碼/台北市共10碼)", "confidence": 0.95},
      {"key": "電信費", "value": "中華電信用戶號碼", "confidence": 0.95}
    ]
  },
  "confidence": 0.92
}

**重要提取規則：**
1. 銀行名稱：通常在表單最上方，如「華南商業銀行」、「台灣銀行」等
2. 戶名：申請人/立委託書人的姓名
3. 身分證：10碼英數字混合，格式如 A123456789
4. 存款帳號：銀行帳號數字，通常12-14位數
5. 連絡電話：可能有多組（市話、手機），用逗號分隔
6. 聯絡地址：完整的通訊地址
7. 電費：台電公司的電號，共11碼數字
8. 水費：台灣省11碼或台北市10碼
9. 電信費：中華電信用戶號碼

**注意事項：**
- 如果某欄位在圖片中不存在或無法辨識，value 填 "" (空字串)
- confidence 為整體辨識信心度 (0-1)
- 請仔細辨識手寫文字"""

        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=4096,
            )

            result_text = response.choices[0].message.content

            # Parse JSON response
            result = json.loads(result_text)

            return {
                "extracted_text": result.get("extracted_text", ""),
                "structured_data": result.get("structured_data", {}),
                "confidence": result.get("confidence", 0),
            }

        except json.JSONDecodeError as e:
            raise OCRProcessingError(f"無法解析 OpenAI 回應: {str(e)}")
        except Exception as e:
            raise OCRProcessingError(f"OpenAI API 錯誤: {str(e)}")
