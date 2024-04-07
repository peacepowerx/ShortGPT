from gmail import send_email_with_gmail
import logging
import threading
logger = logging.getLogger(__name__)

import os
import requests
from moviepy.editor import AudioFileClip, VideoFileClip, ImageClip, concatenate_videoclips, TextClip, ColorClip, CompositeVideoClip
from gtts import gTTS
from io import BytesIO
from PIL import Image
from pillow_heif import register_heif_opener
from textwrap import wrap
from gcp_local_script2video import VideoUploader
from shortGPT.config.api_db import ApiKeyManager
import uuid
api_key_manager = ApiKeyManager()
register_heif_opener()

def cleanup_temp_files(temp_files):
    for file_path in temp_files:
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting temporary file {file_path}: {e.strerror}")

def transcript_to_audio(transcript):
    openai_api_key = api_key_manager.get_api_key('OPENAI')
    if openai_api_key:
        try:
            response = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={"model": "tts-1", "input": transcript, "voice": "onyx"},
            )
            if response.status_code == 200:
                audio_data = response.content
                return audio_data  # 返回字节串
            else:
                print("OpenAI API request failed, switching to gTTS...")
                # 如果API请求失败，则转到gTTS
        except Exception as e:
            print(f"Error accessing OpenAI API: {e}, switching to gTTS...")
            # 处理异常，例如网络错误

    # gTTS备选方案
    tts = gTTS(text=transcript, lang='en')
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.getvalue()  # 返回字节串


def convert_heic_to_jpeg(heic_path):
    # 打开HEIC文件
    image = Image.open(heic_path)

    # 转换色彩模式，因为JPEG不支持Alpha通道
    if image.mode == "RGBA":
        image = image.convert("RGB")

    # 保存图片为JPEG


    # 转换文件名并保存为JPEG格式
    base_path, _ = os.path.splitext(heic_path)
    jpeg_path = base_path + '.jpg'
    image.save(jpeg_path, "JPEG")
    return jpeg_path

def get_file_type(filename):
    video_extensions = ['.mp4', '.mov', '.avi']
    image_extensions = ['.jpg', '.png', '.jpeg']  # Note: .heic is handled separately

    extension = os.path.splitext(filename)[1].lower()
    if extension in video_extensions:
        return 'video'
    elif extension in image_extensions or extension == '.heic':
        return 'image'
    else:
        return 'unknown'

def download_file(url, new_filename):
    # 使用提供的新文件名来保存下载的文件
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(new_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return new_filename

def get_file_type_from_url(url):
    # Make a HEAD request to get headers without downloading the whole file
    response = requests.head(url, allow_redirects=True)

    # Extract the Content-Type header
    content_type = response.headers.get('Content-Type')
    print(f"####content_type:{content_type}")
    # Map common MIME types to file extensions
    mime_types_to_extension = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'text/html': 'html',
        'application/pdf': 'pdf',
        'video/mp4': 'mp4',
        # Add more mappings as needed
    }

    # Get the file extension based on the Content-Type
    file_extension = mime_types_to_extension.get(content_type, 'png')

    return file_extension

def resize_with_padding(image_clip, target_size):
    # 计算新尺寸以保持宽高比
    ratio = min(target_size[0] / image_clip.size[0], target_size[1] / image_clip.size[1])
    new_size = (int(image_clip.size[0] * ratio), int(image_clip.size[1] * ratio))
    # 生成新的ImageClip对象，保持原有的宽高比
    image_clip_resized = image_clip.resize(newsize=new_size)
    # 使用CompositeVideoClip在必要时添加黑色背景填充
    padded_clip = CompositeVideoClip([image_clip_resized.set_position("center")], size=target_size)
    return padded_clip

def dynamic_text_wrap(text, font, max_width, fontsize, line_limit=3):
    """
    Dynamically wraps text to fit within a specified width and line limit.
    Returns the wrapped text and the best font size found.
    """
    # Start with a large font size and decrease until it fits within the line limit
    for fs in range(fontsize, 10, -1):  # Don't go below a font size of 10
        wrapped_text = wrap(text, width=int(max_width / (fs * 0.6)))  # 0.6 is an estimated width per character
        if len(wrapped_text) <= line_limit:
            return "\n".join(wrapped_text), fs  # Text fits, return wrapped text and font size
    return text, fontsize  # Fallback to original if no fit was found

def add_subtitles_with_background(clip, txt, txt_color='white', bg_color=(0, 0, 0), fontsize=50, bg_opacity=0.5, line_limit=3):
    """Adds a subtitle with dynamic font size adjustment to fit text within a line limit."""
    # Calculate the maximum width for text based on clip size
    max_width = clip.w * 0.8  # Use 80% of the clip width for text

    # Dynamically wrap text and adjust font size
    wrapped_text, adjusted_fontsize = dynamic_text_wrap(txt, "Arial-Bold", max_width, fontsize, line_limit)

    # Create a text clip with the wrapped text
    txt_clip = TextClip(wrapped_text, fontsize=adjusted_fontsize, color=txt_color, font="Arial-Bold",
                        size=(max_width, None), method="caption")
    txt_clip = txt_clip.set_duration(clip.duration)

    # Position the text clip at the bottom of the video
    txt_clip = txt_clip.set_position(('center', 'bottom'))

    # Create a semi-transparent background for the text clip
    txt_bg = ColorClip(size=(clip.w, txt_clip.h + 10), color=bg_color, duration=clip.duration)
    txt_bg = txt_bg.set_opacity(bg_opacity)

    # Position the background at the bottom of the video
    txt_bg = txt_bg.set_position(('center', 'bottom'))

    # Composite the text and the background on top of the video
    composite = CompositeVideoClip([clip, txt_bg, txt_clip.set_position(('center', 'bottom'))])

    return composite

def process_scene(scene, scene_index, target_format, temp_files):
    audio_data = transcript_to_audio(scene['voice_over'])
    audio_filename = f'scene_{scene_index}_audio.mp3'
    #clean
    temp_files.append(audio_filename)
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(audio_data)

    audio_clip = AudioFileClip(audio_filename)
    audio_duration = audio_clip.duration

    target_size_short = (1080, 1920)
    target_size_long = (1920, 1080)
    target_size = target_size_short if target_format == "short" else target_size_long

    filenames = scene['filename'] if isinstance(scene['filename'], list) else [scene['filename']]
    subclips = []

    audio_clip_parts = [audio_clip.subclip(i * audio_duration / len(filenames), (i + 1) * audio_duration / len(filenames)) for i in range(len(filenames))]

    text_over_clip = None
    if 'text_over' in scene:
        text_over_clip = TextClip(scene['text_over'], fontsize=70, color='white', method='caption', align='center', font='Arial-Bold')
        # Set the position to the bottom of the clip
        text_over_clip = text_over_clip.set_pos(('center', 'bottom'))

    for idx, url in enumerate(filenames):
        #file_extension = get_file_type(url)
        file_extension = "png"
        new_filename = f'scene_{scene_index}_file_{idx}.{file_extension}'
        print(f"NEW filename URL: {new_filename}")
        filename = download_file(url, new_filename)
        #clean
        temp_files.append(filename) 

        if filename.lower().endswith('.heic'):
            filename = convert_heic_to_jpeg(filename)

        file_type = get_file_type(filename)

        if file_type == 'video':
            video_clip = VideoFileClip(filename)
            clip_duration = min(audio_clip_parts[idx].duration, video_clip.duration)
            clip = video_clip.subclip(0, clip_duration).resize(newsize=target_size)
            clip = clip.set_audio(audio_clip_parts[idx])

            if text_over_clip:
                clip = add_subtitles_with_background(clip, scene['text_over'])

            subclips.append(clip)

        elif file_type == 'image':
            image_clip = ImageClip(filename).set_duration(audio_clip_parts[idx].duration)
            image_clip = resize_with_padding(image_clip, target_size)
            image_clip = image_clip.set_audio(audio_clip_parts[idx])

            if text_over_clip:
                image_clip = add_subtitles_with_background(image_clip, scene['text_over'])

            subclips.append(image_clip)
          

    if subclips:
        scene_clip = concatenate_videoclips(subclips, method="compose")
        scene_video_filename = f'scene_{scene_index}_video.mp4'
        scene_clip.write_videofile(scene_video_filename, codec="libx264", audio_codec="aac", fps=24)
        return scene_video_filename




def storyboard2video(storyboard, target_format="short"):
    # Assume register_heif_opener() and other necessary initializations are done here if needed
    temp_files = []
    # Process each scene in the storyboard
    scene_video_filenames = [process_scene(scene, index, target_format, temp_files) for index, scene in enumerate(storyboard)]
    
    # Load all processed scene video files
    scene_clips = [VideoFileClip(filename) for filename in scene_video_filenames]
    
    # Concatenate scene video files into a full video
    final_clip = concatenate_videoclips(scene_clips, method="compose")
    unique_id = uuid.uuid4()
    final_video_filename = f"final_video_{unique_id}.mp4"
    final_clip.write_videofile(final_video_filename, codec="libx264", audio_codec="aac", fps=24)
    
    # Clean up: close all video clips
    for filename in scene_video_filenames:
        temp_files.append(filename)
    for clip in scene_clips:
        clip.close()
    cleanup_temp_files(temp_files)
    # Return the path to the final video
    return final_video_filename


def storyboard2video_gcp(storyboard):
    video_path = storyboard2video(storyboard)
    # 上传视频到GCS并获取公共URL
    bucket_name = 'shortgpt'
    destination_blob_name = str(video_path)
    public_url = VideoUploader.upload_to_gcs(bucket_name, video_path, destination_blob_name)

    print(f"Video uploaded to GCS. Public URL: {public_url}")
    return public_url
    
def storyboard2video_gcp_email(email, storyboard):
    public_video_url = storyboard2video_gcp(storyboard)
    send_email_with_gmail(email, public_video_url)
    logger.info(f"email sent to : {str(email)}")



# scenes =[
#     {
#         "voice_over": "A white bunny named Fluffy, with sparkling eyes, standing nervously at the start line of a race track, heart pounding.",
#         "text_over": "The race begins: Will Fluffy's determination overcome her nerves?",
#         "filename": ["https://p16-flow-sign-va.ciciai.com/ocean-cloud-tos-us/30b2017f600e4477a2fb3f5aba644955.png~tplv-6bxrjdptv7-image.png?rk3s=18ea6f23&x-expires=1742681782&x-signature=S%2F4w6tzIlMm2lm3YNmI0Eu5TTyU%3D"],
#         "duration": 15
#     },
#     {
#         "voice_over": "Fluffy, the bunny, is now racing on the track, feet thumping rhythmically.",
#         "text_over": "Determination in every stride, Fluffy thumps down the track.",
#         "filename": ["https://p16-flow-sign-va.ciciai.com/ocean-cloud-tos-us/e5719a7893a646e9a3a84b962f9f4d41.png~tplv-6bxrjdptv7-image.png?rk3s=18ea6f23&x-expires=1742681779&x-signature=i6D7%2BOk%2BKl%2BV0FjhnkMym%2Fvxwao%3D"],
#         "duration": 20
#     },
#     {
#         "voice_over": "Fluffy crosses the finish line, her chest heaving. She hasn't won the race but has managed to break her own record.",
#         "text_over": "Victory in spirit, Fluffy breaks her record!",
#         "filename": ["https://p16-flow-sign-va.ciciai.com/ocean-cloud-tos-us/58211fb9502c4c40abec9c14829f55d1.png~tplv-6bxrjdptv7-image.png?rk3s=18ea6f23&x-expires=1742681778&x-signature=GJLgV%2BSgg8YYhWZQ0ja8u%2BJf3cs%3D"],
#         "duration": 15
#     },
#     {
#         "voice_over": "Cat with gleaming green eyes and Tiger with chestnut stripes cheer for Fluffy. They fill the air with joy as they celebrate Fluffy's achievements.",
#         "text_over": "Paws up in the air: Cat and Tiger celebrate Fluffy's triumph!",
#         "filename": ["https://p16-flow-sign-va.ciciai.com/ocean-cloud-tos-us/7b37d69223f8433ba3d7e2fa5eb0be93.png~tplv-6bxrjdptv7-image.png?rk3s=18ea6f23&x-expires=1742681780&x-signature=j7Py0rUhkyEIJa61dlVUPS3blzM%3D"],
#         "duration": 10
#     }
# ]

# storyboard2video_gcp(storyboard=scenes)