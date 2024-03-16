from google.cloud import storage
from shortGPT.config.languages import (EDGE_TTS_VOICENAME_MAPPING,
                                        ELEVEN_SUPPORTED_LANGUAGES,
                                        COQUI_SUPPORTED_LANGUAGES,
                                        LANGUAGE_ACRONYM_MAPPING,
                                        Language)
from shortGPT.engine.content_video_engine import ContentVideoEngine
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
from shortGPT.audio.coqui_voice_module import CoquiVoiceModule
class VideoUploader:
    @staticmethod
    def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
        """上传文件到GCS存储桶，并设置为公开访问（如果启用了UBLA）。"""
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)
        VideoUploader.make_blob_public(bucket_name, destination_blob_name)
        return blob.public_url

    @staticmethod
    def make_blob_public(bucket_name, blob_name):
        """设置指定对象为公开访问。此方法用于UBLA启用的存储桶。"""
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        policy = bucket.get_iam_policy(requested_policy_version=3)
        policy.bindings.append({
            'role': 'roles/storage.objectViewer',
            'members': {'allUsers'},
        })
        bucket.set_iam_policy(policy)

        print(f"Blob {blob_name} is now publicly accessible.")

def make_and_upload_video(script, voice_module, isVertical, progress_func):
    # 初始化视频生成引擎

    video_path = 'videos/2024-03-14_22-20-00 - Boost Your Health with Apples .mp4'

    # 上传视频到GCS并获取公共URL
    bucket_name = 'shortgpt'
    destination_blob_name = str(video_path)
    public_url = VideoUploader.upload_to_gcs(bucket_name, video_path, destination_blob_name)

    print(f"Video uploaded to GCS. Public URL: {public_url}")
    return public_url
# 定义一个简单的进度更新函数
def progress_update(progress, message):
    print(f"Progress: {progress*100}%, Message: {message}")

# 实例化语音模块和设置脚本
language = Language.ENGLISH
voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
isVertical = True

script = "Discover the majestic Tratzberg Castle, nestled in the heart of picturesque landscapes, offering a journey through history and breathtaking architecture. Come and be enchanted!Savor the ambiance: intimate gatherings, delectable cuisine, and joyful moments await your presence. Join the feast!"
isVertical = True # 或 False，取决于您的视频格式需求

# 调用make_and_upload_video函数
public_video_url = make_and_upload_video(script, voice_module, isVertical, progress_update)