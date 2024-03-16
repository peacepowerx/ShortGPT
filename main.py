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

app = Flask(__name__)

    # 定义一个简单的进度更新函数
def progress_update(progress, message):
    print(f"Progress: {progress*100}%, Message: {message}")

@app.route('/script2video', methods=['POST'])
def make_video_api():
    request_json = request.get_json(silent=True)
    script = request_json.get('script')
    isVertical = request_json.get('isVertical', True)  # 默认为True
    language = Language.ENGLISH
    voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
    # 调用您之前定义的make_and_upload_video函数
    public_video_url = make_and_upload_video(script, voice_module, isVertical, progress_update)

    return jsonify({'url': public_video_url})

if __name__ == '__main__':
    app.run()
