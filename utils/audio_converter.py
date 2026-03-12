"""
音频格式转换工具
支持多种音频格式转换为标准WAV格式
"""

import io
import struct
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class AudioConverter:
    """
    音频格式转换器
    
    将各种音频格式转换为标准WAV格式（16kHz, 16bit, 单声道）
    """
    
    # 支持的音频格式魔数
    AUDIO_FORMATS = {
        b'RIFF': 'wav',      # WAV格式
        b'ID3\x04': 'mp3',   # MP3格式 (ID3v2.4)
        b'ID3\x03': 'mp3',   # MP3格式 (ID3v2.3)
        b'\xff\xfb': 'mp3',  # MP3格式 (无ID3)
        b'\xff\xf3': 'mp3',  # MP3格式
        b'\xff\xf2': 'mp3',  # MP3格式
        b'fLaC': 'flac',     # FLAC格式
        b'OggS': 'ogg',      # OGG格式
        b'M4A ': 'm4a',      # M4A格式
    }
    
    @classmethod
    def detect_format(cls, data: bytes) -> Optional[str]:
        """
        检测音频格式
        
        Args:
            data: 音频文件前几个字节
            
        Returns:
            格式名称或None
        """
        if len(data) < 4:
            return None
        
        # 检查前4字节
        magic = data[:4]
        if magic in cls.AUDIO_FORMATS:
            return cls.AUDIO_FORMATS[magic]
        
        # 检查MP3特殊格式
        if data[:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
            return 'mp3'
        
        # 检查M4A (ftyp在偏移4处)
        if len(data) >= 8 and data[4:8] == b'ftyp':
            return 'm4a'
        
        return None
    
    @classmethod
    def convert_to_wav(cls, input_data: bytes, target_sample_rate: int = 16000) -> Tuple[bytes, bool]:
        """
        将音频数据转换为WAV格式
        
        Args:
            input_data: 输入音频数据
            target_sample_rate: 目标采样率
            
        Returns:
            (wav_data, success): WAV格式数据和是否成功
        """
        # 检测格式
        input_format = cls.detect_format(input_data)
        
        if input_format == 'wav':
            # 已经是WAV，检查是否需要重采样
            return cls._process_wav(input_data, target_sample_rate)
        
        # 尝试使用ffmpeg转换
        return cls._convert_with_ffmpeg(input_data, input_format, target_sample_rate)
    
    @classmethod
    def _process_wav(cls, data: bytes, target_sample_rate: int) -> Tuple[bytes, bool]:
        """
        处理WAV文件，检查并重采样
        
        Args:
            data: WAV数据
            target_sample_rate: 目标采样率
            
        Returns:
            (wav_data, success)
        """
        try:
            # 解析WAV头部
            if len(data) < 44:
                return data, True  # 数据太短，直接返回
            
            # 读取采样率（偏移24，4字节）
            sample_rate = struct.unpack('<I', data[24:28])[0]
            
            # 如果采样率已经是目标值，直接返回
            if sample_rate == target_sample_rate:
                return data, True
            
            # 需要重采样，使用ffmpeg
            return cls._convert_with_ffmpeg(data, 'wav', target_sample_rate)
            
        except Exception as e:
            print(f"[AudioConverter] WAV processing error: {e}")
            return data, True  # 出错时返回原始数据
    
    @classmethod
    def _convert_with_ffmpeg(cls, data: bytes, input_format: Optional[str], 
                            target_sample_rate: int) -> Tuple[bytes, bool]:
        """
        使用ffmpeg转换音频格式
        
        Args:
            data: 输入音频数据
            input_format: 输入格式
            target_sample_rate: 目标采样率
            
        Returns:
            (wav_data, success)
        """
        try:
            import ffmpeg
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{input_format or "bin"}', 
                                             delete=False) as input_file:
                input_file.write(data)
                input_path = input_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                output_path = output_file.name
            
            try:
                # 使用ffmpeg转换
                (
                    ffmpeg
                    .input(input_path)
                    .output(output_path,
                           ar=target_sample_rate,  # 采样率
                           ac=1,                    # 单声道
                           acodec='pcm_s16le')      # 16bit PCM
                    .run(quiet=True, overwrite_output=True)
                )
                
                # 读取转换后的文件
                with open(output_path, 'rb') as f:
                    wav_data = f.read()
                
                return wav_data, True
                
            finally:
                # 清理临时文件
                import os
                try:
                    os.unlink(input_path)
                    os.unlink(output_path)
                except:
                    pass
                    
        except ImportError:
            print("[AudioConverter] ffmpeg-python not installed, skipping conversion")
            return data, False
        except Exception as e:
            print(f"[AudioConverter] FFmpeg conversion error: {e}")
            return data, False
    
    @classmethod
    def generate_silent_wav(cls, duration: float = 1.0, 
                           sample_rate: int = 16000) -> bytes:
        """
        生成静音WAV数据
        
        Args:
            duration: 时长（秒）
            sample_rate: 采样率
            
        Returns:
            WAV格式字节数据
        """
        num_samples = int(sample_rate * duration)
        
        # WAV头部
        header = b'RIFF'
        header += struct.pack('<I', 36 + num_samples * 2)  # 文件大小
        header += b'WAVE'
        header += b'fmt '
        header += struct.pack('<I', 16)  # fmt块大小
        header += struct.pack('<H', 1)   # 音频格式 (PCM)
        header += struct.pack('<H', 1)   # 声道数
        header += struct.pack('<I', sample_rate)  # 采样率
        header += struct.pack('<I', sample_rate * 2)  # 字节率
        header += struct.pack('<H', 2)   # 块对齐
        header += struct.pack('<H', 16)  # 采样位数
        header += b'data'
        header += struct.pack('<I', num_samples * 2)  # 数据大小
        
        # 静音数据
        data = b'\x00\x00' * num_samples
        
        return header + data


# 便捷函数
def convert_audio(input_data: bytes, target_sample_rate: int = 16000) -> bytes:
    """
    转换音频为WAV格式
    
    Args:
        input_data: 输入音频数据
        target_sample_rate: 目标采样率
        
    Returns:
        WAV格式数据（转换失败则返回静音）
    """
    wav_data, success = AudioConverter.convert_to_wav(input_data, target_sample_rate)
    
    if not success:
        # 转换失败，返回静音（避免服务中断）
        print("[AudioConverter] Conversion failed, returning silence")
        return AudioConverter.generate_silent_wav(duration=1.0)
    
    return wav_data
