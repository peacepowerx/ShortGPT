from flask import Flask, request, jsonify
from google.cloud import storage
from gcp_local_script2video import make_and_upload_video, make_and_upload_video_email
from shortGPT.config.languages import (EDGE_TTS_VOICENAME_MAPPING,
                                        ELEVEN_SUPPORTED_LANGUAGES,
                                        COQUI_SUPPORTED_LANGUAGES,
                                        LANGUAGE_ACRONYM_MAPPING,
                                        Language)
from shortGPT.engine.content_video_engine import ContentVideoEngine
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
import os
from shortGPT.config.api_db import ApiKeyManager
import logging
import threading
from utl_video_editing import storyboard2video_gcp, storyboard2video_gcp_email
from input_checker import is_valid_email, is_url_accessible
logger = logging.getLogger(__name__)

app = Flask(__name__)
api_key_manager = ApiKeyManager()
    # 定义一个简单的进度更新函数
def progress_update(progress, message):
    print(f"Progress: {progress*100}%, Message: {message}")

def correct_urls_in_storyboard(storyboard):
    """
    遍历storyboard中的每个场景，纠正filename列表中所有URL的格式错误。
    Args:
        storyboard (list of dict): 包含场景信息，每个场景包括至少一个filename URL。

    Returns:
        None: 直接修改传入的storyboard列表中的元素。
    """
    for scene in storyboard:
        if 'filename' in scene:
            original_filenames = scene['filename']
            corrected_filenames = []
            for url in original_filenames:
                corrected_url = url.replace("\\u0026", "&")
                if url != corrected_url:
                    logger.info(f"Corrected URL from {url} to {corrected_url}")
                corrected_filenames.append(corrected_url)
            scene['filename'] = corrected_filenames    

# TODO: 参考openai和gemni的格式，用content，parts来规范输入
@app.route('/script2video', methods=['POST'])
def make_video_api():
    request_json = request.get_json(silent=True, force=True)
    logger.info(f"Request args: {str(request_json)}")
    print(f"Request args: {str(request_json)}")
    openai_key = request_json.get('openai_key')
    pexels_key = request_json.get('pexels_key')
    eleven_key = request_json.get('eleven_key')
    script = request_json.get('script',"Welcome video")
    isVertical = request_json.get('isVertical', True)  # 默认为True
    logger.warn(f"$$$$script$$$$: {str(script)}")
    if not all([openai_key, pexels_key, eleven_key, script]):
        return jsonify({"error": "Missing required parameters"}), 400
    if (api_key_manager.get_api_key('OPENAI') != openai_key):
        api_key_manager.set_api_key("OPENAI", openai_key)
    if (api_key_manager.get_api_key('PEXELS') != pexels_key):
        api_key_manager.set_api_key("PEXELS", pexels_key)
    if (api_key_manager.get_api_key('ELEVEN LABS') != eleven_key):
        api_key_manager.set_api_key("ELEVEN LABS", eleven_key)
    if not all([openai_key, pexels_key, eleven_key, script]):
        return jsonify({"error": "Missing required parameters"}), 400    
    language = Language.ENGLISH
    voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
    # 调用您之前定义的make_and_upload_video函数
    public_video_url = make_and_upload_video(script, voice_module, isVertical, progress_update)

    return jsonify({'url': public_video_url})

@app.route('/emailvideo', methods=['POST'])
def email_video():
    request_json = request.get_json(silent=True, force=True)
    logger.info(f"Request args: {str(request_json)}")
    print(f"Request args: {str(request_json)}")
    #email
    email = request_json.get('email')
    openai_key = request_json.get('openai_key')
    pexels_key = request_json.get('pexels_key')
    eleven_key = request_json.get('eleven_key')
    script = request_json.get('script',"Welcome video")
    isVertical = request_json.get('isVertical', True)  # 默认为True
    logger.warn(f"$$$$script$$$$: {str(script)}")
    if not all([email, openai_key, pexels_key, eleven_key, script]):
        return jsonify({"error": "Missing required parameters"}), 400
    if is_valid_email(email)!= True:
        return jsonify({"error": "Please Provide a valid email"}), 400
    if (api_key_manager.get_api_key('OPENAI') != openai_key):
        api_key_manager.set_api_key("OPENAI", openai_key)
    if (api_key_manager.get_api_key('PEXELS') != pexels_key):
        api_key_manager.set_api_key("PEXELS", pexels_key)
    if (api_key_manager.get_api_key('ELEVEN LABS') != eleven_key):
        api_key_manager.set_api_key("ELEVEN LABS", eleven_key)

    language = Language.ENGLISH
    voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])    
# Start video processing in a new thread
    thread = threading.Thread(target=make_and_upload_video_email, args=(email,script, voice_module, isVertical, progress_update))
    thread.start()
    
    # Immediately return a response
    return jsonify({"message": f"Your video based on the script is being processed. You will receive an email at {email} once it is ready."})


@app.route('/storyboard2video', methods=['POST'])
def storyboard2video_api():
    request_json = request.get_json(silent=True, force=True)
    logger.info(f"Request args: {str(request_json)}")
    print(f"Request args: {str(request_json)}")
    storyboard = request_json.get('storyboard')
    openai_key = request_json.get('openai_key')
    if not all([storyboard]):
        return jsonify({"error": "Missing required parameters"}), 400
    if (api_key_manager.get_api_key('OPENAI') != openai_key):
        api_key_manager.set_api_key("OPENAI", openai_key)
    public_video_url = storyboard2video_gcp(storyboard)    
    return jsonify({"url": public_video_url})

@app.route('/storyboard2video_email', methods=['POST'])
def storyboard2video_email_api():
    request_json = request.get_json(silent=True, force=True)
    logger.info(f"Request args: {str(request_json)}")
    print(f"Request args: {str(request_json)}")
    email = request_json.get('email')
    storyboard = request_json.get('storyboard')
    # temp fix
    correct_urls_in_storyboard(storyboard)
    openai_key = request_json.get('openai_key')
    if (api_key_manager.get_api_key('OPENAI') != openai_key):
        api_key_manager.set_api_key("OPENAI", openai_key)
    if not all([email, storyboard]):
        return jsonify({"error": "Missing required parameters"}), 400
    if is_valid_email(email)!= True:
        return jsonify({"error": "Please Provide a valid email"}), 400
    # Extract all filenames from the storyboard and check accessibility
    filenames = [scene['filename'] for scene in storyboard]
    # List to hold inaccessible URLs
    inaccessible_urls = []

    # Iterate over filenames, accommodating both strings and lists
    for filename in filenames:
        if isinstance(filename, list):
            # Handle the case where filename is a list of URLs
            inaccessible_urls.extend([url for url in filename if not is_url_accessible(url)])
        elif isinstance(filename, str):
            # Handle the case where filename is a single URL string
            if not is_url_accessible(filename):
                inaccessible_urls.append(filename)

    if inaccessible_urls:
        # Return an error message if any URL is not accessible
        return jsonify({"error": f"Some resources cannot be accessed: {inaccessible_urls}"}), 400


    thread = threading.Thread(target=storyboard2video_gcp_email, args=(email,storyboard))
    thread.start()
    
    # Immediately return a response
    return jsonify({"message": f"Your video based on the storyboard is being processed. You will receive an email at {email} once it is ready."})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
