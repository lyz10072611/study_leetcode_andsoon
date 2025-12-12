"""
高级工具示例

这个模块展示了FastMCP的高级功能，包括异步处理、图片处理、
文件操作、网络请求等。这些工具展示了FastMCP的企业级特性。
"""

from fastmcp import FastMCP, Context
from typing import List, Dict, Optional, Any, Union
import asyncio
import aiohttp
import aiofiles
from PIL import Image
import io
import base64
import json
import hashlib
import time
from datetime import datetime, timedelta
import tempfile
import os
import uuid


class AdvancedTools:
    """高级工具类，包含异步处理、图片处理、网络请求等功能"""
    
    def __init__(self, mcp: FastMCP):
        """
        初始化高级工具
        
        Args:
            mcp: FastMCP服务器实例
        """
        self.mcp = mcp
        self._register_tools()
        # 用于存储临时文件信息
        self.temp_files: Dict[str, Dict[str, Any]] = {}
    
    def _register_tools(self):
        """注册所有高级工具"""
        # 异步处理工具
        self.mcp.tool()(self.async_data_processor)
        self.mcp.tool()(self.concurrent_web_scraper)
        self.mcp.tool()(self.async_file_processor)
        self.mcp.tool()(self.simulate_long_running_task)
        
        # 图片处理工具
        self.mcp.tool()(self.resize_image)
        self.mcp.tool()(self.convert_image_format)
        self.mcp.tool()(self.apply_image_filter)
        self.mcp.tool()(self.extract_image_metadata)
        self.mcp.tool()(self.create_thumbnail)
        self.mcp.tool()(self.merge_images)
        self.mcp.tool()(self.add_watermark)
        
        # 文件操作工具
        self.mcp.tool()(self.read_file_async)
        self.mcp.tool()(self.write_file_async)
        self.mcp.tool()(self.list_directory)
        self.mcp.tool()(self.create_archive)
        self.mcp.tool()(self.extract_archive)
        self.mcp.tool()(self.calculate_file_hash)
        
        # 网络请求工具
        self.mcp.tool()(self.fetch_web_data)
        self.mcp.tool()(self.check_website_status)
        self.mcp.tool()(self.get_weather_data)
        self.mcp.tool()(self.translate_text)
        self.mcp.tool()(self.get_exchange_rates)
        
        # 数据处理工具
        self.mcp.tool()(self.json_validator)
        self.mcp.tool()(self.csv_to_json)
        self.mcp.tool()(self.json_to_csv)
        self.mcp.tool()(self.data_transformation)
        self.mcp.tool()(self.generate_report)
        
        # 缓存和会话工具
        self.mcp.tool()(self.set_cache_value)
        self.mcp.tool()(self.get_cache_value)
        self.mcp.tool()(self.clear_cache)
        self.mcp.tool()(self.get_session_info)
    
    # ===== 异步处理工具 =====
    
    async def async_data_processor(self, data: List[Any], operation: str, 
                                 context: Context) -> Dict[str, Any]:
        """
        异步数据处理工具，展示异步处理的能力
        
        Args:
            data: 要处理的数据列表
            operation: 操作类型，可选"sort", "filter", "transform", "aggregate"
            context: FastMCP上下文对象
            
        Returns:
            处理结果
            
        Example:
            >>> await async_data_processor([3, 1, 4, 1, 5], "sort")
            {
                "original_data": [3, 1, 4, 1, 5],
                "processed_data": [1, 1, 3, 4, 5],
                "operation": "sort",
                "processing_time": 0.05
            }
        """
        start_time = time.time()
        context.log.info(f"开始异步数据处理，操作: {operation}, 数据量: {len(data)}")
        
        # 模拟异步处理
        await asyncio.sleep(0.1)
        
        # 发送进度更新
        await context.progress(30, "数据预处理完成")
        await asyncio.sleep(0.05)
        
        result = None
        
        if operation == "sort":
            result = sorted(data)
        elif operation == "filter":
            # 过滤掉None值和空值
            result = [item for item in data if item is not None and str(item).strip()]
        elif operation == "transform":
            # 转换为大写（如果是字符串）
            result = [str(item).upper() if isinstance(item, str) else item for item in data]
        elif operation == "aggregate":
            # 聚合统计
            numeric_data = [item for item in data if isinstance(item, (int, float))]
            if numeric_data:
                result = {
                    "count": len(numeric_data),
                    "sum": sum(numeric_data),
                    "average": sum(numeric_data) / len(numeric_data),
                    "min": min(numeric_data),
                    "max": max(numeric_data)
                }
            else:
                result = {"error": "没有数值数据可供聚合"}
        else:
            result = {"error": f"不支持的操作: {operation}"}
        
        await context.progress(100, "数据处理完成")
        
        processing_time = time.time() - start_time
        
        return {
            "original_data": data,
            "processed_data": result,
            "operation": operation,
            "processing_time": round(processing_time, 3)
        }
    
    async def concurrent_web_scraper(self, urls: List[str], timeout: int = 30,
                                   context: Context) -> Dict[str, Any]:
        """
        并发网络爬虫，展示并发处理能力
        
        Args:
            urls: 要爬取的URL列表
            timeout: 超时时间（秒），默认为30
            context: FastMCP上下文对象
            
        Returns:
            爬取结果
        """
        context.log.info(f"开始并发爬取 {len(urls)} 个URL")
        
        async def fetch_url(session: aiohttp.ClientSession, url: str, index: int):
            """获取单个URL的内容"""
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    content = await response.text()
                    return {
                        "url": url,
                        "status": response.status,
                        "content_length": len(content),
                        "title": self._extract_title(content),
                        "success": True
                    }
            except Exception as e:
                return {
                    "url": url,
                    "status": 0,
                    "error": str(e),
                    "success": False
                }
        
        async with aiohttp.ClientSession() as session:
            # 并发执行所有请求
            tasks = [fetch_url(session, url, i) for i, url in enumerate(urls)]
            results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r["success"])
        
        context.log.info(f"爬取完成，成功: {successful}/{len(urls)}")
        
        return {
            "total_urls": len(urls),
            "successful": successful,
            "failed": len(urls) - successful,
            "results": results
        }
    
    def _extract_title(self, html_content: str) -> str:
        """从HTML内容中提取标题"""
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        return title_match.group(1).strip() if title_match else "No title found"
    
    async def async_file_processor(self, file_path: str, operations: List[str],
                                 context: Context) -> Dict[str, Any]:
        """
        异步文件处理器
        
        Args:
            file_path: 文件路径
            operations: 操作列表，可选"read", "word_count", "line_count", "find_emails", "find_urls"
            context: FastMCP上下文对象
            
        Returns:
            处理结果
        """
        context.log.info(f"开始异步处理文件: {file_path}")
        
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}
        
        results = {}
        
        try:
            if "read" in operations:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()
                    results["content"] = content[:1000]  # 限制返回内容长度
                    await context.progress(20, "文件读取完成")
            
            if "word_count" in operations:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()
                    word_count = len(content.split())
                    results["word_count"] = word_count
            
            if "line_count" in operations:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    lines = 0
                    async for line in file:
                        lines += 1
                    results["line_count"] = lines
            
            if "find_emails" in operations:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()
                    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
                    results["emails_found"] = list(set(emails))  # 去重
            
            if "find_urls" in operations:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()
                    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
                    results["urls_found"] = list(set(urls))  # 去重
            
            await context.progress(100, "文件处理完成")
            
            # 获取文件基本信息
            file_stats = os.stat(file_path)
            results["file_info"] = {
                "size_bytes": file_stats.st_size,
                "size_kb": round(file_stats.st_size / 1024, 2),
                "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "file_path": file_path
            }
            
        except Exception as e:
            return {"error": f"文件处理失败: {str(e)}"}
        
        return results
    
    async def simulate_long_running_task(self, duration: int, steps: int = 10,
                                       context: Context) -> Dict[str, Any]:
        """
        模拟长时间运行的任务，展示进度报告功能
        
        Args:
            duration: 任务持续时间（秒）
            steps: 进度更新步数，默认为10
            context: FastMCP上下文对象
            
        Returns:
            任务执行结果
        """
        context.log.info(f"开始长时间任务，预计耗时: {duration}秒")
        
        start_time = time.time()
        step_duration = duration / steps
        
        for i in range(steps):
            await asyncio.sleep(step_duration)
            progress = ((i + 1) / steps) * 100
            
            # 发送进度更新
            await context.progress(
                progress, 
                f"任务进行中... {i + 1}/{steps} 步骤完成"
            )
            
            # 发送自定义事件
            await context.send_event(
                "task_progress",
                {
                    "step": i + 1,
                    "total_steps": steps,
                    "progress_percentage": progress,
                    "estimated_remaining": duration - (i + 1) * step_duration
                }
            )
        
        total_time = time.time() - start_time
        
        return {
            "status": "completed",
            "total_duration": round(total_time, 2),
            "steps_completed": steps,
            "message": "长时间任务执行完成"
        }
    
    # ===== 图片处理工具 =====
    
    def resize_image(self, image_data: str, width: int, height: int, 
                    maintain_aspect_ratio: bool = True) -> Dict[str, Any]:
        """
        调整图片大小
        
        Args:
            image_data: Base64编码的图片数据
            width: 目标宽度
            height: 目标高度
            maintain_aspect_ratio: 是否保持宽高比，默认为True
            
        Returns:
            处理后的图片信息
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            original_width, original_height = image.size
            
            if maintain_aspect_ratio:
                # 计算保持宽高比的尺寸
                ratio = min(width / original_width, height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                new_width = width
                new_height = height
            
            # 调整大小
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 转换回base64
            output_buffer = io.BytesIO()
            resized_image.save(output_buffer, format=image.format or 'PNG')
            output_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "original_size": (original_width, original_height),
                "new_size": (new_width, new_height),
                "image_data": output_data,
                "format": image.format or 'PNG',
                "size_bytes": len(output_buffer.getvalue())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"图片处理失败: {str(e)}"
            }
    
    def convert_image_format(self, image_data: str, target_format: str,
                           quality: int = 85) -> Dict[str, Any]:
        """
        转换图片格式
        
        Args:
            image_data: Base64编码的图片数据
            target_format: 目标格式，如'JPEG', 'PNG', 'WEBP'
            quality: JPEG质量，默认为85
            
        Returns:
            转换后的图片信息
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 转换格式
            output_buffer = io.BytesIO()
            
            if target_format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # JPEG不支持透明度，转换为RGB
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                rgb_image.save(output_buffer, format='JPEG', quality=quality)
            else:
                save_kwargs = {}
                if target_format.upper() in ['JPEG', 'WEBP']:
                    save_kwargs['quality'] = quality
                
                image.save(output_buffer, format=target_format.upper(), **save_kwargs)
            
            output_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "original_format": image.format or 'Unknown',
                "new_format": target_format.upper(),
                "image_data": output_data,
                "size_bytes": len(output_buffer.getvalue()),
                "size_reduction": round((1 - len(output_buffer.getvalue()) / len(image_bytes)) * 100, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"格式转换失败: {str(e)}"
            }
    
    def apply_image_filter(self, image_data: str, filter_type: str,
                         **kwargs) -> Dict[str, Any]:
        """
        应用图片滤镜
        
        Args:
            image_data: Base64编码的图片数据
            filter_type: 滤镜类型，可选"blur", "sharpen", "grayscale", "sepia", "brightness"
            **kwargs: 滤镜参数
            
        Returns:
            处理后的图片信息
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            if filter_type == "blur":
                radius = kwargs.get('radius', 2)
                from PIL import ImageFilter
                filtered_image = image.filter(ImageFilter.GaussianBlur(radius=radius))
                
            elif filter_type == "sharpen":
                from PIL import ImageFilter
                filtered_image = image.filter(ImageFilter.SHARPEN)
                
            elif filter_type == "grayscale":
                filtered_image = image.convert('L')
                
            elif filter_type == "sepia":
                # 棕褐色调效果
                width, height = image.size
                pixels = image.load()
                
                for py in range(height):
                    for px in range(width):
                        r, g, b = image.getpixel((px, py))
                        
                        tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                        tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                        tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                        
                        if tr > 255:
                            tr = 255
                        if tg > 255:
                            tg = 255
                        if tb > 255:
                            tb = 255
                        
                        pixels[px, py] = (tr, tg, tb)
                
                filtered_image = image
                
            elif filter_type == "brightness":
                factor = kwargs.get('factor', 1.2)
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Brightness(image)
                filtered_image = enhancer.enhance(factor)
                
            else:
                return {
                    "success": False,
                    "error": f"不支持的滤镜类型: {filter_type}"
                }
            
            # 转换回base64
            output_buffer = io.BytesIO()
            filtered_image.save(output_buffer, format=image.format or 'PNG')
            output_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "filter_applied": filter_type,
                "image_data": output_data,
                "format": image.format or 'PNG',
                "size_bytes": len(output_buffer.getvalue())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"滤镜应用失败: {str(e)}"
            }
    
    def extract_image_metadata(self, image_data: str) -> Dict[str, Any]:
        """
        提取图片元数据
        
        Args:
            image_data: Base64编码的图片数据
            
        Returns:
            图片元数据
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            metadata = {
                "format": image.format or 'Unknown',
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "size_bytes": len(image_bytes)
            }
            
            # 提取EXIF数据（如果有）
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = {}
                exif = image._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = Image.ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                    metadata["exif"] = exif_data
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"元数据提取失败: {str(e)}"
            }
    
    def create_thumbnail(self, image_data: str, max_size: int = 150) -> Dict[str, Any]:
        """
        创建缩略图
        
        Args:
            image_data: Base64编码的图片数据
            max_size: 最大尺寸，默认为150像素
            
        Returns:
            缩略图信息
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 创建缩略图
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # 转换回base64
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='PNG')
            thumbnail_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "thumbnail_data": thumbnail_data,
                "thumbnail_size": image.size,
                "original_size": (Image.open(io.BytesIO(image_bytes)).width, 
                                Image.open(io.BytesIO(image_bytes)).height)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"缩略图创建失败: {str(e)}"
            }
    
    def merge_images(self, image_data_list: List[str], layout: str = "horizontal",
                    spacing: int = 10) -> Dict[str, Any]:
        """
        合并多张图片
        
        Args:
            image_data_list: Base64编码的图片数据列表
            layout: 布局方式，可选"horizontal"、"vertical"、"grid"
            spacing: 图片间距，默认为10像素
            
        Returns:
            合并后的图片信息
        """
        try:
            if len(image_data_list) < 2:
                return {
                    "success": False,
                    "error": "至少需要两张图片进行合并"
                }
            
            # 解码所有图片
            images = []
            for image_data in image_data_list:
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                images.append(image)
            
            if layout == "horizontal":
                # 水平布局
                total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
                max_height = max(img.height for img in images)
                
                merged_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))
                
                x_offset = 0
                for image in images:
                    merged_image.paste(image, (x_offset, 0))
                    x_offset += image.width + spacing
                    
            elif layout == "vertical":
                # 垂直布局
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
                
                merged_image = Image.new('RGB', (max_width, total_height), (255, 255, 255))
                
                y_offset = 0
                for image in images:
                    merged_image.paste(image, (0, y_offset))
                    y_offset += image.height + spacing
                    
            elif layout == "grid":
                # 网格布局（简化版：正方形网格）
                import math
                grid_size = math.ceil(math.sqrt(len(images)))
                
                # 计算网格尺寸
                max_width = max(img.width for img in images)
                max_height = max(img.height for img in images)
                
                grid_width = max_width * grid_size + spacing * (grid_size - 1)
                grid_height = max_height * grid_size + spacing * (grid_size - 1)
                
                merged_image = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
                
                for i, image in enumerate(images):
                    row = i // grid_size
                    col = i % grid_size
                    
                    x = col * (max_width + spacing)
                    y = row * (max_height + spacing)
                    
                    # 居中对齐
                    x_offset = (max_width - image.width) // 2
                    y_offset = (max_height - image.height) // 2
                    
                    merged_image.paste(image, (x + x_offset, y + y_offset))
            
            else:
                return {
                    "success": False,
                    "error": f"不支持的布局方式: {layout}"
                }
            
            # 转换回base64
            output_buffer = io.BytesIO()
            merged_image.save(output_buffer, format='PNG')
            merged_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "merged_image_data": merged_data,
                "layout": layout,
                "image_count": len(images),
                "final_size": merged_image.size,
                "size_bytes": len(output_buffer.getvalue())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"图片合并失败: {str(e)}"
            }
    
    def add_watermark(self, image_data: str, watermark_text: str,
                     position: str = "bottom-right", opacity: float = 0.5,
                     font_size: int = 36) -> Dict[str, Any]:
        """
        添加水印
        
        Args:
            image_data: Base64编码的图片数据
            watermark_text: 水印文本
            position: 水印位置，可选"top-left", "top-right", "bottom-left", "bottom-right", "center"
            opacity: 透明度，0-1之间，默认为0.5
            font_size: 字体大小，默认为36
            
        Returns:
            添加水印后的图片信息
        """
        try:
            # 解码图片数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # 创建水印图层
            watermark = Image.new('RGBA', image.size, (0, 0, 0, 0))
            
            # 尝试使用更好的字体，如果不可用则使用默认字体
            try:
                from PIL import ImageFont
                # 尝试使用系统字体
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            except:
                font = None
            
            # 创建绘图对象
            from PIL import ImageDraw
            draw = ImageDraw.Draw(watermark)
            
            # 计算文本尺寸
            if font:
                text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            else:
                text_width = len(watermark_text) * font_size * 0.6
                text_height = font_size
            
            # 计算位置
            img_width, img_height = image.size
            
            if position == "top-left":
                x, y = 10, 10
            elif position == "top-right":
                x, y = img_width - text_width - 10, 10
            elif position == "bottom-left":
                x, y = 10, img_height - text_height - 10
            elif position == "bottom-right":
                x, y = img_width - text_width - 10, img_height - text_height - 10
            elif position == "center":
                x, y = (img_width - text_width) // 2, (img_height - text_height) // 2
            else:
                x, y = img_width - text_width - 10, img_height - text_height - 10
            
            # 添加半透明背景
            padding = 5
            bg_bbox = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
            draw.rectangle(bg_bbox, fill=(0, 0, 0, int(128 * opacity)))
            
            # 添加文本
            text_color = (255, 255, 255, int(255 * opacity))
            if font:
                draw.text((x, y), watermark_text, font=font, fill=text_color)
            else:
                draw.text((x, y), watermark_text, fill=text_color)
            
            # 合并图片和水印
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            result = Image.alpha_composite(image, watermark)
            
            # 转换回base64
            output_buffer = io.BytesIO()
            result.save(output_buffer, format='PNG')
            result_data = base64.b64encode(output_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "watermarked_image_data": result_data,
                "watermark_text": watermark_text,
                "position": position,
                "opacity": opacity,
                "size_bytes": len(output_buffer.getvalue())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"水印添加失败: {str(e)}"
            }
    
    # ===== 文件操作工具 =====
    
    async def read_file_async(self, file_path: str, encoding: str = 'utf-8',
                            max_size: int = 1024 * 1024) -> Dict[str, Any]:  # 1MB限制
        """
        异步读取文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认为utf-8
            max_size: 最大读取大小（字节），默认为1MB
            
        Returns:
            文件内容
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            file_size = os.path.getsize(file_path)
            
            if file_size > max_size:
                return {
                    "error": f"文件过大: {file_size} 字节 (最大限制: {max_size} 字节)",
                    "file_size": file_size
                }
            
            async with aiofiles.open(file_path, 'r', encoding=encoding) as file:
                content = await file.read()
            
            return {
                "success": True,
                "content": content,
                "file_path": file_path,
                "size_bytes": file_size,
                "encoding": encoding
            }
            
        except Exception as e:
            return {
                "error": f"文件读取失败: {str(e)}"
            }
    
    async def write_file_async(self, file_path: str, content: str,
                             encoding: str = 'utf-8', create_dirs: bool = True) -> Dict[str, Any]:
        """
        异步写入文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码，默认为utf-8
            create_dirs: 是否创建目录，默认为True
            
        Returns:
            写入结果
        """
        try:
            # 创建目录（如果需要）
            if create_dirs:
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding) as file:
                await file.write(content)
            
            file_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "size_bytes": file_size,
                "encoding": encoding,
                "message": "文件写入成功"
            }
            
        except Exception as e:
            return {
                "error": f"文件写入失败: {str(e)}"
            }
    
    def list_directory(self, directory_path: str, recursive: bool = False,
                      file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        列出目录内容
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归列出子目录，默认为False
            file_extensions: 文件扩展名过滤器，如['.txt', '.py']
            
        Returns:
            目录内容列表
        """
        try:
            if not os.path.exists(directory_path):
                return {"error": f"目录不存在: {directory_path}"}
            
            if not os.path.isdir(directory_path):
                return {"error": f"路径不是目录: {directory_path}"}
            
            items = []
            
            if recursive:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # 检查文件扩展名
                        if file_extensions:
                            if not any(file.endswith(ext) for ext in file_extensions):
                                continue
                        
                        file_stats = os.stat(file_path)
                        items.append({
                            "name": file,
                            "path": file_path,
                            "type": "file",
                            "size_bytes": file_stats.st_size,
                            "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                            "relative_path": os.path.relpath(file_path, directory_path)
                        })
            else:
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)
                    item_stats = os.stat(item_path)
                    
                    # 检查文件扩展名（如果是文件）
                    if os.path.isfile(item_path) and file_extensions:
                        if not any(item.endswith(ext) for ext in file_extensions):
                            continue
                    
                    items.append({
                        "name": item,
                        "path": item_path,
                        "type": "directory" if os.path.isdir(item_path) else "file",
                        "size_bytes": item_stats.st_size if os.path.isfile(item_path) else 0,
                        "modified_time": datetime.fromtimestamp(item_stats.st_mtime).isoformat()
                    })
            
            return {
                "success": True,
                "directory": directory_path,
                "items": items,
                "total_items": len(items),
                "recursive": recursive,
                "filters": {
                    "file_extensions": file_extensions
                }
            }
            
        except Exception as e:
            return {
                "error": f"目录列表失败: {str(e)}"
            }
    
    def create_archive(self, source_paths: List[str], archive_name: str,
                      archive_format: str = "zip") -> Dict[str, Any]:
        """
        创建压缩文件
        
        Args:
            source_paths: 要压缩的文件或目录路径列表
            archive_name: 压缩文件名（不含扩展名）
            archive_format: 压缩格式，可选"zip", "tar", "gztar", "bztar"
            
        Returns:
            压缩结果
        """
        try:
            import shutil
            
            # 检查所有源路径是否存在
            for path in source_paths:
                if not os.path.exists(path):
                    return {"error": f"路径不存在: {path}"}
            
            # 创建压缩文件
            archive_path = shutil.make_archive(archive_name, archive_format, root_dir=None, base_dir=None)
            
            # 获取压缩文件信息
            archive_stats = os.stat(archive_path)
            
            return {
                "success": True,
                "archive_path": archive_path,
                "format": archive_format,
                "size_bytes": archive_stats.st_size,
                "source_paths": source_paths,
                "message": f"压缩文件创建成功: {archive_path}"
            }
            
        except Exception as e:
            return {
                "error": f"压缩文件创建失败: {str(e)}"
            }
    
    def calculate_file_hash(self, file_path: str, algorithm: str = "sha256") -> Dict[str, Any]:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法，可选"md5", "sha1", "sha256", "sha512"
            
        Returns:
            哈希值信息
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            # 选择哈希算法
            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "sha512":
                hash_obj = hashlib.sha512()
            else:
                return {"error": f"不支持的哈希算法: {algorithm}"}
            
            # 计算哈希值
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_obj.update(chunk)
            
            hash_value = hash_obj.hexdigest()
            
            return {
                "success": True,
                "file_path": file_path,
                "algorithm": algorithm,
                "hash": hash_value,
                "file_size": os.path.getsize(file_path)
            }
            
        except Exception as e:
            return {
                "error": f"哈希计算失败: {str(e)}"
            }
    
    # ===== 网络请求工具 =====
    
    async def fetch_web_data(self, url: str, method: str = "GET",
                           headers: Optional[Dict[str, str]] = None,
                           timeout: int = 30, context: Context) -> Dict[str, Any]:
        """
        获取网页数据
        
        Args:
            url: 目标URL
            method: 请求方法，默认为GET
            headers: 请求头字典
            timeout: 超时时间（秒），默认为30
            context: FastMCP上下文对象
            
        Returns:
            网页数据
        """
        context.log.info(f"获取网页数据: {url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, 
                                         timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    content = await response.text()
                    
                    return {
                        "success": True,
                        "url": url,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "content_length": len(content),
                        "content_preview": content[:1000],  # 限制返回内容长度
                        "encoding": response.get_encoding()
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"网页获取失败: {str(e)}"
            }
    
    async def check_website_status(self, urls: List[str], timeout: int = 10,
                                 context: Context) -> Dict[str, Any]:
        """
        检查网站状态
        
        Args:
            urls: 要检查的URL列表
            timeout: 超时时间（秒），默认为10
            context: FastMCP上下文对象
            
        Returns:
            网站状态检查结果
        """
        context.log.info(f"开始检查 {len(urls)} 个网站状态")
        
        async def check_single_url(session: aiohttp.ClientSession, url: str):
            """检查单个URL"""
            try:
                start_time = time.time()
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    response_time = time.time() - start_time
                    
                    return {
                        "url": url,
                        "status": response.status,
                        "response_time": round(response_time, 3),
                        "success": 200 <= response.status < 300,
                        "headers": dict(response.headers)
                    }
            except Exception as e:
                return {
                    "url": url,
                    "status": 0,
                    "error": str(e),
                    "success": False
                }
        
        async with aiohttp.ClientSession() as session:
            tasks = [check_single_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "total_urls": len(urls),
            "successful": successful,
            "failed": len(urls) - successful,
            "results": results
        }
    
    async def get_weather_data(self, city: str, units: str = "metric",
                             api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        获取天气数据（使用OpenWeatherMap API）
        
        Args:
            city: 城市名称
            units: 单位制，可选"metric", "imperial", "kelvin"
            api_key: API密钥（可选，如果不提供则使用模拟数据）
            
        Returns:
            天气数据
        """
        if api_key:
            # 使用真实API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units={units}&appid={api_key}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "success": True,
                                "city": city,
                                "temperature": data["main"]["temp"],
                                "feels_like": data["main"]["feels_like"],
                                "humidity": data["main"]["humidity"],
                                "pressure": data["main"]["pressure"],
                                "weather": data["weather"][0]["description"],
                                "wind_speed": data["wind"]["speed"],
                                "units": units
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"API返回错误状态: {response.status}"
                            }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"天气数据获取失败: {str(e)}"
                }
        else:
            # 返回模拟数据
            import random
            
            base_temp = {"metric": 20, "imperial": 68, "kelvin": 293}[units]
            
            return {
                "success": True,
                "city": city,
                "temperature": base_temp + random.randint(-5, 5),
                "feels_like": base_temp + random.randint(-3, 3),
                "humidity": random.randint(40, 80),
                "pressure": random.randint(1000, 1030),
                "weather": random.choice(["晴朗", "多云", "小雨", "阴天"]),
                "wind_speed": random.randint(0, 20),
                "units": units,
                "note": "这是模拟数据，请提供API密钥获取真实数据"
            }
    
    async def translate_text(self, text: str, target_language: str = "en",
                           source_language: str = "auto") -> Dict[str, Any]:
        """
        翻译文本（模拟翻译功能）
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言代码，默认为"en"（英语）
            source_language: 源语言代码，默认为"auto"（自动检测）
            
        Returns:
            翻译结果
        """
        # 这是一个模拟翻译功能
        # 在实际应用中，你可以集成Google Translate API、Microsoft Translator等
        
        # 简单的翻译映射（仅用于演示）
        translation_map = {
            "hello": {"es": "hola", "fr": "bonjour", "de": "hallo", "zh": "你好"},
            "world": {"es": "mundo", "fr": "monde", "de": "welt", "zh": "世界"},
            "good": {"es": "bueno", "fr": "bon", "de": "gut", "zh": "好"},
            "thank you": {"es": "gracias", "fr": "merci", "de": "danke", "zh": "谢谢"}
        }
        
        text_lower = text.lower().strip()
        
        if text_lower in translation_map and target_language in translation_map[text_lower]:
            translated_text = translation_map[text_lower][target_language]
        else:
            # 模拟翻译（实际应用中应该调用真实的翻译API）
            translated_text = f"[{target_language.upper()}] {text}"
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "note": "这是模拟翻译，实际应用中请集成真实的翻译API"
        }
    
    async def get_exchange_rates(self, base_currency: str = "USD",
                               target_currencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取汇率信息（模拟数据）
        
        Args:
            base_currency: 基础货币代码，默认为"USD"
            target_currencies: 目标货币代码列表，如["EUR", "GBP", "JPY"]
            
        Returns:
            汇率信息
        """
        if target_currencies is None:
            target_currencies = ["EUR", "GBP", "JPY", "CNY", "CAD"]
        
        # 模拟汇率数据（实际应用中应该调用真实的汇率API）
        import random
        
        base_rates = {
            "USD": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "CNY": 6.4, "CAD": 1.25},
            "EUR": {"USD": 1.18, "GBP": 0.86, "JPY": 129.0, "CNY": 7.5, "CAD": 1.47},
            "GBP": {"USD": 1.37, "EUR": 1.16, "JPY": 150.0, "CNY": 8.7, "CAD": 1.71}
        }
        
        if base_currency in base_rates:
            rates = base_rates[base_currency]
        else:
            # 对其他货币使用USD作为基准的模拟汇率
            rates = {curr: random.uniform(0.5, 2.0) for curr in target_currencies}
        
        # 添加一些随机变化
        final_rates = {}
        for currency in target_currencies:
            if currency in rates:
                rate = rates[currency] * random.uniform(0.98, 1.02)
                final_rates[currency] = round(rate, 4)
            else:
                final_rates[currency] = round(random.uniform(0.5, 2.0), 4)
        
        return {
            "success": True,
            "base_currency": base_currency,
            "rates": final_rates,
            "timestamp": datetime.now().isoformat(),
            "note": "这是模拟汇率数据，实际应用中请使用真实的汇率API"
        }
    
    # ===== 数据处理工具 =====
    
    def json_validator(self, json_string: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        JSON数据验证器
        
        Args:
            json_string: JSON字符串
            schema: JSON Schema（可选）
            
        Returns:
            验证结果
        """
        try:
            # 解析JSON
            data = json.loads(json_string)
            
            result = {
                "valid": True,
                "data": data,
                "error": None
            }
            
            # 如果有schema，进行schema验证
            if schema:
                try:
                    # 简化的schema验证（实际应用中应该使用jsonschema库）
                    self._validate_against_schema(data, schema)
                    result["schema_valid"] = True
                except Exception as e:
                    result["schema_valid"] = False
                    result["schema_error"] = str(e)
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"JSON解析错误: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"验证失败: {str(e)}"
            }
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]):
        """简化的schema验证"""
        # 这里应该实现完整的JSON Schema验证逻辑
        # 为了简化，这里只检查基本类型
        
        if "type" in schema:
            expected_type = schema["type"]
            
            if expected_type == "object" and not isinstance(data, dict):
                raise ValueError(f"期望对象类型，得到: {type(data).__name__}")
            elif expected_type == "array" and not isinstance(data, list):
                raise ValueError(f"期望数组类型，得到: {type(data).__name__}")
            elif expected_type == "string" and not isinstance(data, str):
                raise ValueError(f"期望字符串类型，得到: {type(data).__name__}")
            elif expected_type == "number" and not isinstance(data, (int, float)):
                raise ValueError(f"期望数值类型，得到: {type(data).__name__}")
            elif expected_type == "boolean" and not isinstance(data, bool):
                raise ValueError(f"期望布尔类型，得到: {type(data).__name__}")
    
    def csv_to_json(self, csv_content: str, delimiter: str = ",") -> Dict[str, Any]:
        """
        CSV转JSON
        
        Args:
            csv_content: CSV内容
            delimiter: 分隔符，默认为逗号
            
        Returns:
            JSON数据
        """
        try:
            import csv
            
            # 解析CSV
            csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
            data = list(csv_reader)
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "columns": list(data[0].keys()) if data else []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"CSV转换失败: {str(e)}"
            }
    
    def json_to_csv(self, json_data: List[Dict[str, Any]], delimiter: str = ",") -> Dict[str, Any]:
        """
        JSON转CSV
        
        Args:
            json_data: JSON数据列表
            delimiter: 分隔符，默认为逗号
            
        Returns:
            CSV内容
        """
        try:
            if not json_data:
                return {"error": "JSON数据不能为空"}
            
            import csv
            
            # 获取所有列名
            columns = set()
            for row in json_data:
                columns.update(row.keys())
            columns = sorted(list(columns))
            
            # 生成CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=columns, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(json_data)
            
            csv_content = output.getvalue()
            
            return {
                "success": True,
                "csv_content": csv_content,
                "row_count": len(json_data),
                "column_count": len(columns),
                "columns": columns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"JSON转换失败: {str(e)}"
            }
    
    def data_transformation(self, data: List[Dict[str, Any]], 
                          transformations: Dict[str, Any]) -> Dict[str, Any]:
        """
        数据转换工具
        
        Args:
            data: 输入数据
            transformations: 转换规则
            
        Returns:
            转换后的数据
        """
        try:
            transformed_data = []
            
            for item in data:
                new_item = {}
                
                # 字段映射
                if "field_mapping" in transformations:
                    for old_field, new_field in transformations["field_mapping"].items():
                        if old_field in item:
                            new_item[new_field] = item[old_field]
                
                # 添加新字段
                if "add_fields" in transformations:
                    for field, value in transformations["add_fields"].items():
                        new_item[field] = value
                
                # 删除字段
                if "remove_fields" in transformations:
                    for field in transformations["remove_fields"]:
                        new_item.pop(field, None)
                
                # 保留原始字段（如果没有映射）
                for field, value in item.items():
                    if field not in transformations.get("field_mapping", {}):
                        new_item[field] = value
                
                transformed_data.append(new_item)
            
            return {
                "success": True,
                "original_data": data,
                "transformed_data": transformed_data,
                "transformation_count": len(transformed_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"数据转换失败: {str(e)}"
            }
    
    def generate_report(self, data: List[Dict[str, Any]], 
                       report_type: str = "summary") -> Dict[str, Any]:
        """
        生成数据报告
        
        Args:
            data: 输入数据
            report_type: 报告类型，可选"summary", "statistics", "detailed"
            
        Returns:
            生成的报告
        """
        try:
            if not data:
                return {"error": "数据不能为空"}
            
            report = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "data_count": len(data)
            }
            
            if report_type == "summary":
                # 基础摘要
                report["summary"] = {
                    "total_records": len(data),
                    "fields": list(data[0].keys()) if data else [],
                    "sample_records": data[:3]  # 前3条记录作为样本
                }
            
            elif report_type == "statistics":
                # 统计信息
                stats = {}
                
                for record in data:
                    for field, value in record.items():
                        if field not in stats:
                            stats[field] = {
                                "total": 0,
                                "numeric_count": 0,
                                "string_count": 0,
                                "null_count": 0,
                                "unique_values": set()
                            }
                        
                        stats[field]["total"] += 1
                        stats[field]["unique_values"].add(str(value))
                        
                        if value is None:
                            stats[field]["null_count"] += 1
                        elif isinstance(value, (int, float)):
                            stats[field]["numeric_count"] += 1
                        elif isinstance(value, str):
                            stats[field]["string_count"] += 1
                
                # 转换set为list以便JSON序列化
                for field in stats:
                    stats[field]["unique_values"] = list(stats[field]["unique_values"])
                    stats[field]["unique_count"] = len(stats[field]["unique_values"])
                
                report["statistics"] = stats
            
            elif report_type == "detailed":
                # 详细报告
                report["detailed"] = {
                    "total_records": len(data),
                    "field_analysis": {},
                    "data_quality": {}
                }
                
                # 字段分析
                for record in data:
                    for field, value in record.items():
                        if field not in report["detailed"]["field_analysis"]:
                            report["detailed"]["field_analysis"][field] = {
                                "type": type(value).__name__,
                                "present_count": 0,
                                "missing_count": 0,
                                "unique_values": set()
                            }
                        
                        if value is not None and str(value).strip() != "":
                            report["detailed"]["field_analysis"][field]["present_count"] += 1
                            report["detailed"]["field_analysis"][field]["unique_values"].add(str(value))
                        else:
                            report["detailed"]["field_analysis"][field]["missing_count"] += 1
                
                # 转换set为list
                for field in report["detailed"]["field_analysis"]:
                    report["detailed"]["field_analysis"][field]["unique_values"] = list(
                        report["detailed"]["field_analysis"][field]["unique_values"]
                    )
                
                # 数据质量评估
                total_fields = sum(len(record) for record in data)
                missing_fields = sum(
                    1 for record in data 
                    for field, value in record.items() 
                    if value is None or str(value).strip() == ""
                )
                
                report["detailed"]["data_quality"] = {
                    "completeness": round((1 - missing_fields / total_fields) * 100, 2),
                    "total_fields": total_fields,
                    "missing_fields": missing_fields
                }
            
            return {
                "success": True,
                "report": report
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"报告生成失败: {str(e)}"
            }