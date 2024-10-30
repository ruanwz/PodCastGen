import os
import sys
from pocketgroq import GroqProvider, GroqAPIKeyMissingError, GroqAPIError
import asyncio
import subprocess
from edge_tts import Communicate
from config import (
    DEFAULT_MODEL,
    MAX_TOKENS,
    HOST_PROFILES,
    OUTLINE_PROMPT_TEMPLATE,
    EXPAND_PROMPT_TEMPLATE,
    DIALOGUE_PROMPT_TEMPLATE
)

class PodCastGen:
    def __init__(self, male_voice='zh-CN-YunxiNeural', female_voice='zh-CN-XiaoxiaoNeural'):
        """
        初始化 PodCastGen
        
        Args:
            male_voice (str): 男声角色，默认使用'zh-CN-YunxiNeural'
            female_voice (str): 女声角色，默认使用'zh-CN-XiaoxiaoNeural'
        """
        try:
            self.groq = GroqProvider()
            self.male_voice = male_voice
            self.female_voice = female_voice
        except GroqAPIKeyMissingError:
            print("Error: GROQ_API_KEY not found. Please set it in your environment variables.")
            sys.exit(1)
        except Exception as e:
            print(f"Error during initialization: {e}")
            sys.exit(1)

    @staticmethod
    def list_voices():
        """列出所有可用的语音"""
        try:
            result = subprocess.run(['edge-tts', '--list-voices'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error listing voices: {e}")
            return None

    @staticmethod
    def list_voices_by_language(language_code):
        """
        列出指定语言的所有语音
        
        Args:
            language_code (str): 语言代码，如 'zh-CN', 'en-US' 等
        """
        voices = PodCastGen.list_voices()
        if voices:
            filtered_voices = []
            for line in voices.split('\n'):
                if line.startswith('Name: ' + language_code):
                    filtered_voices.append(line)
                    # 获取下一行的性别信息
                    next_line = next((l for l in voices.split('\n') if 'Gender:' in l), None)
                    if next_line:
                        filtered_voices.append(next_line)
            return '\n'.join(filtered_voices)
        return None

    async def generate_audio_segment(self, text, voice, output_file):
        try:
            communicate = Communicate(text, voice)
            await communicate.save(output_file)
            return True
        except Exception as e:
            print(f"Error generating audio: {e}")
            return False

    async def generate_audio_from_script(self, script, output_dir):
        lines = script.split('\n')
        audio_segments = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        for i, line in enumerate(lines):
            if line.strip():
                try:
                    # 处理中文冒号和英文冒号
                    if '：' in line:
                        speaker, text = line.split('：', 1)
                    elif ':' in line:
                        speaker, text = line.split(':', 1)
                    else:
                        print(f"Skipping invalid line format: {line}")
                        continue
                    
                    speaker = speaker.strip().lower()
                    text = text.strip()
                    
                    # 选择声音
                    voice = self.male_voice if speaker == "mike" else self.female_voice
                    
                    # 修正临时文件路径
                    temp_file = os.path.join(output_dir, f"segment_{i}.mp3")
                    success = await self.generate_audio_segment(text, voice, temp_file)
                    
                    if success and os.path.exists(temp_file):  # 添加文件存在检查
                        audio_segments.append(temp_file)
                        print(f"Generated segment {i}: {temp_file}")
                    
                except Exception as e:
                    print(f"Error processing line: {line}")
                    print(f"Error details: {e}")
        
        # 合并所有音频片段
        if audio_segments:
            output_file = os.path.join(output_dir, "full_podcast.mp3")
            concat_file = os.path.join(output_dir, "concat.txt")
            
            # 使用绝对路径写入concat文件
            with open(concat_file, 'w') as f:
                for segment in audio_segments:
                    # 使用绝对路径
                    abs_path = os.path.abspath(segment)
                    f.write(f"file '{abs_path}'\n")
            
            try:
                cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', 
                      '-i', concat_file, '-c', 'copy', output_file]
                print(f"Running ffmpeg command: {' '.join(cmd)}")
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"FFmpeg output: {result.stdout}")
                
                # 清理临时文件
                os.remove(concat_file)
                for segment in audio_segments:
                    if os.path.exists(segment):
                        os.remove(segment)
                
                print(f"Full podcast audio saved to: {output_file}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error: {e.stderr}")
                raise
        else:
            print("No audio segments were generated successfully.")

    def generate_podcast_script(self, input_text):
        outline = self._generate_outline(input_text)
        if not outline:
            return None

        full_script = self._expand_outline(outline)
        if not full_script:
            return None

        dialogue_script = self._convert_to_dialogue(full_script)
        return dialogue_script

    def _generate_outline(self, input_text):
        prompt = OUTLINE_PROMPT_TEMPLATE.format(input_text=input_text)
        try:
            return self.groq.generate(prompt, model=DEFAULT_MODEL, max_tokens=MAX_TOKENS["outline"])
        except GroqAPIError as e:
            print(f"Error generating outline: {e}")
            return None

    def _expand_outline(self, outline):
        prompt = EXPAND_PROMPT_TEMPLATE.format(outline=outline, host_profiles=HOST_PROFILES)
        try:
            return self.groq.generate(prompt, model=DEFAULT_MODEL, max_tokens=MAX_TOKENS["full_script"])
        except GroqAPIError as e:
            print(f"Error expanding outline: {e}")
            return None

    def _convert_to_dialogue(self, full_script):
        prompt = DIALOGUE_PROMPT_TEMPLATE.format(full_script=full_script, host_profiles=HOST_PROFILES)
        try:
            return self.groq.generate(prompt, model=DEFAULT_MODEL, max_tokens=MAX_TOKENS["dialogue"])
        except GroqAPIError as e:
            print(f"Error converting to dialogue: {e}")
            return None

    def process_html_content(self, text: str) -> str:
        """
        使用 LLM 处理 HTML 内容
        """
        prompt = f"""
        请从以下网页内容中提取主要的文本信息，去除导航栏、页脚等无关内容：

        {text}

        只返回主要内容，使用简洁的格式。
        """
        
        try:
            result = self.groq.generate(prompt, model=DEFAULT_MODEL, max_tokens=MAX_TOKENS["outline"])
            return result
        except Exception as e:
            print(f"Error using LLM to process HTML content: {e}")
            # 如果 LLM 处理失败，返回基本清理的文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)

    def process_input_text(self, input_source: str) -> str:
        """
        处理输入源并返回文本内容
        """
        try:
            # 检查是否是 YouTube URL
            if "youtube.com" in input_source or "youtu.be" in input_source:
                return process_youtube_url(input_source)
            # 检查是否是 HTML URL
            elif input_source.startswith(("http://", "https://")):
                return self.process_html_url(input_source)
            # 处理本地文件
            else:
                return process_local_file(input_source)
                
        except Exception as e:
            print(f"Error processing input source: {e}")
            return ""

    def process_html_url(self, url: str) -> str:
        """
        从 HTML URL 获取内容并使用 LLM 提取文本
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # 获取 HTML 内容
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.decompose()
                
            # 获取文本内容
            text = soup.get_text()
            
            # 使用 LLM 处理内容
            return self.process_html_content(text)
                
        except Exception as e:
            print(f"Error processing HTML URL: {e}")
            return ""

def process_youtube_url(url: str) -> str:
    """
    从 YouTube URL 获取英文字幕内容
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
        
        # 从 URL 中提取视频 ID
        video_id = None
        if "youtu.be" in url:
            video_id = url.split("/")[-1].split("?")[0]  # 处理可能的查询参数
        elif "youtube.com" in url:
            # 处理不同格式的 YouTube URL
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "/embed/" in url:
                video_id = url.split("/embed/")[1].split("?")[0]
            elif "/v/" in url:
                video_id = url.split("/v/")[1].split("?")[0]
        
        if not video_id:
            print(f"Error: Could not extract video ID from URL: {url}")
            return ""
            
        print(f"Extracted video ID: {video_id}")
        
        # 获取字幕列表
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 尝试获取英文字幕
            try:
                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                text_transcript = transcript.fetch()
                # 将字幕合并成文本，添加适当的分隔
                transcript_text = []
                for entry in text_transcript:
                    text = entry['text'].strip()
                    if text:  # 只添加非空文本
                        transcript_text.append(text)
                
                return "\n".join(transcript_text)
                
            except NoTranscriptFound:
                print("No English transcript found. Trying auto-translated version...")
                # 尝试获取任何可用字幕并翻译成英文
                transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB', 'zh-CN', 'zh', 'ja', 'ko'])
                translated_transcript = transcript.translate('en')
                text_transcript = translated_transcript.fetch()
                transcript_text = []
                for entry in text_transcript:
                    text = entry['text'].strip()
                    if text:
                        transcript_text.append(text)
                
                return "\n".join(transcript_text)
                
        except Exception as e:
            print(f"Error accessing transcripts: {e}")
            return ""
            
    except Exception as e:
        print(f"Error processing YouTube URL: {e}")
        print(f"URL: {url}")
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈
        return ""

def process_local_file(file_path: str) -> str:
    """
    处理本地文件
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return ""
        
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path)
        if ext.lower() != '.txt':
            print(f"Error: Unsupported file format {ext}. Please use .txt files.")
            return ""
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            print("Error: Input file is empty")
            return ""
            
        return content
        
    except Exception as e:
        print(f"Error processing input file: {e}")
        return ""

async def async_main():
    import argparse
    parser = argparse.ArgumentParser(description='PodCastGen - AI Podcast Generator')
    
    # 创建互斥参数组
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list-voices', action='store_true', help='List all available voices')
    group.add_argument('--list-language', help='List voices for specific language (e.g., zh-CN)')
    
    # 输入源和输出目录
    parser.add_argument('input_source', nargs='?', 
                        help='Input source (file path, YouTube URL, or HTML URL)')
    parser.add_argument('output_directory', nargs='?', help='Output directory path')
    parser.add_argument('--use-script', action='store_true', help='Use existing script')
    parser.add_argument('--male-voice', help='Male voice to use (default: zh-CN-YunxiNeural)')
    parser.add_argument('--female-voice', help='Female voice to use (default: zh-CN-XiaoxiaoNeural)')
    
    args = parser.parse_args()

    # 如果只是列出语音选项，执行后退出
    if args.list_voices:
        voices = PodCastGen.list_voices()
        if voices:
            print(voices)
        return

    if args.list_language:
        voices = PodCastGen.list_voices_by_language(args.list_language)
        if voices:
            print(voices)
        return

    # 检查是否提供了必要的参数
    if not args.input_source or not args.output_directory:
        parser.error("input_source and output_directory are required when not using --list-voices or --list-language")

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    # 使用命令行参数中指定的语音，如果没有指定则使用默认值
    casters = PodCastGen(
        male_voice=args.male_voice or 'zh-CN-YunxiNeural',
        female_voice=args.female_voice or 'zh-CN-XiaoxiaoNeural'
    )

    if args.use_script:
        print("Using pre-written script...")
        script = casters.process_input_text(args.input_source)
        if not script:
            print("Failed to read the script file.")
            return
    else:
        print("Generating new podcast script...")
        input_text = casters.process_input_text(args.input_source)
        if not input_text:
            print("Failed to process input text.")
            return
        script = casters.generate_podcast_script(input_text)
        if not script:
            print("Failed to generate podcast script.")
            return

    print("Generated/Loaded podcast script:")
    print(script)
    print("\nGenerating audio...")
    await casters.generate_audio_from_script(script, args.output_directory)

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()