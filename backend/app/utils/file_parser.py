"""
文件解析工具
支持PDF、Markdown、TXT文件的文本提取
"""

import os
from pathlib import Path
from typing import List, Optional


def _read_text_with_fallback(file_path: str) -> str:
    """
    读取文本文件，UTF-8失败时自动探测编码。
    
    采用多级回退策略：
    1. 首先尝试 UTF-8 解码
    2. 使用 charset_normalizer 检测编码
    3. 回退到 chardet 检测编码
    4. 最终使用 UTF-8 + errors='replace' 兜底
    
    Args:
        file_path: 文件路径
        
    Returns:
        解码后的文本内容
    """
    data = Path(file_path).read_bytes()
    
    # 首先尝试 UTF-8
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # 尝试使用 charset_normalizer 检测编码
    encoding = None
    try:
        from charset_normalizer import from_bytes
        best = from_bytes(data).best()
        if best and best.encoding:
            encoding = best.encoding
    except Exception:
        pass
    
    # 回退到 chardet
    if not encoding:
        try:
            import chardet
            result = chardet.detect(data)
            encoding = result.get('encoding') if result else None
        except Exception:
            pass
    
    # 最终兜底：使用 UTF-8 + replace
    if not encoding:
        encoding = 'utf-8'
    
    return data.decode(encoding, errors='replace')


class FileParser:
    """文件解析器"""

    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt', '.png', '.jpg', '.jpeg', '.webp'}
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
    
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """
        从文件中提取文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {suffix}")
        
        if suffix == '.pdf':
            return cls._extract_from_pdf(file_path)
        elif suffix in {'.md', '.markdown'}:
            return cls._extract_from_md(file_path)
        elif suffix == '.txt':
            return cls._extract_from_txt(file_path)
        elif suffix in cls.IMAGE_EXTENSIONS:
            return cls._extract_from_image(file_path)

        raise ValueError(f"无法处理的文件格式: {suffix}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """
        Extracts text and embedded images from a PDF.

        For each page:
        - Text is extracted via page.get_text().
        - Embedded image objects (charts, diagrams, figures) are extracted via
          page.get_images() and described by the vision LLM.

        Images smaller than 100x100 px are skipped (icons / decorations).
        Duplicate xrefs across pages are skipped to avoid re-processing the same image.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("需要安装PyMuPDF: pip install PyMuPDF")

        import base64
        from .llm_client import LLMClient

        parts = []
        seen_xrefs: set = set()
        llm_client = None  # lazy-init only when an image is found

        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                # --- text ---
                text = page.get_text()
                if text.strip():
                    parts.append(text)

                # --- embedded images ---
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    if xref in seen_xrefs:
                        continue
                    seen_xrefs.add(xref)

                    try:
                        img_dict = doc.extract_image(xref)
                        width, height = img_dict.get("width", 0), img_dict.get("height", 0)
                        # skip tiny decorative images
                        if width < 100 or height < 100:
                            continue

                        img_bytes = img_dict["image"]
                        ext = img_dict.get("ext", "png")
                        mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

                        if llm_client is None:
                            llm_client = LLMClient()

                        prompt = (
                            "Analyze this image extracted from a PDF document. "
                            "Describe all visible content including: text, numbers, labels, "
                            "chart/graph data and trends, table contents, diagrams, and key insights. "
                            "Be specific and detailed."
                        )
                        description = llm_client.chat_with_image(img_base64, mime_type, prompt)
                        parts.append(f"[Image on page {page_num}]: {description}")
                    except Exception:
                        # silently skip unreadable images
                        continue

        return "\n\n".join(parts)
    
    @staticmethod
    def _extract_from_md(file_path: str) -> str:
        """从Markdown提取文本，支持自动编码检测"""
        return _read_text_with_fallback(file_path)
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """从TXT提取文本，支持自动编码检测"""
        return _read_text_with_fallback(file_path)

    @staticmethod
    def _extract_from_image(file_path: str) -> str:
        """
        从图片提取内容描述，通过 vision LLM 分析图像。
        支持 PNG、JPG、JPEG、WEBP。
        """
        import base64
        import mimetypes
        from .llm_client import LLMClient

        mime_type = mimetypes.guess_type(file_path)[0] or "image/png"
        with open(file_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")

        client = LLMClient()
        prompt = (
            "Analyze this image thoroughly. Describe all visible content including: "
            "any text, numbers, labels, chart/graph data and trends, table contents, "
            "diagrams, figures, and key insights. Be specific and detailed so the "
            "description can be used to build a knowledge graph."
        )
        return client.chat_with_image(image_base64, mime_type, prompt)
    
    @classmethod
    def extract_from_multiple(cls, file_paths: List[str]) -> str:
        """
        从多个文件提取文本并合并
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            合并后的文本
        """
        all_texts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                text = cls.extract_text(file_path)
                filename = Path(file_path).name
                all_texts.append(f"=== 文档 {i}: {filename} ===\n{text}")
            except Exception as e:
                all_texts.append(f"=== 文档 {i}: {file_path} (提取失败: {str(e)}) ===")
        
        return "\n\n".join(all_texts)


def split_text_into_chunks(
    text: str, 
    chunk_size: int = 500, 
    overlap: int = 50
) -> List[str]:
    """
    将文本分割成小块
    
    Args:
        text: 原始文本
        chunk_size: 每块的字符数
        overlap: 重叠字符数
        
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            # 查找最近的句子结束符
            for sep in ['。', '！', '？', '.\n', '!\n', '?\n', '\n\n', '. ', '! ', '? ']:
                last_sep = text[start:end].rfind(sep)
                if last_sep != -1 and last_sep > chunk_size * 0.3:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 下一个块从重叠位置开始
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

