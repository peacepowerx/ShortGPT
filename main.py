from flask import Flask, request, jsonify
from google.cloud import storage
from gcp_local_script2video import make_and_upload_video
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
logger = logging.getLogger(__name__)

app = Flask(__name__)
api_key_manager = ApiKeyManager()
    # 定义一个简单的进度更新函数
def progress_update(progress, message):
    print(f"Progress: {progress*100}%, Message: {message}")

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
    if not all([openai_key, pexels_key, eleven_key, script]):
        return jsonify({"error": "Missing required parameters"}), 400
    if (api_key_manager.get_api_key('OPENAI') != openai_key):
        api_key_manager.set_api_key("OPENAI", openai_key)
    if (api_key_manager.get_api_key('PEXELS') != pexels_key):
        api_key_manager.set_api_key("PEXELS", pexels_key)
    if (api_key_manager.get_api_key('ELEVEN LABS') != eleven_key):
        api_key_manager.set_api_key("ELEVEN LABS", eleven_key)

    language = Language.ENGLISH
    voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
    # 调用您之前定义的make_and_upload_video函数
    public_video_url = make_and_upload_video(script, voice_module, isVertical, progress_update)

    return jsonify({'url': public_video_url})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
