from shortGPT.config.languages import (EDGE_TTS_VOICENAME_MAPPING,
                                        ELEVEN_SUPPORTED_LANGUAGES,
                                        COQUI_SUPPORTED_LANGUAGES,
                                        LANGUAGE_ACRONYM_MAPPING,
                                        Language)
from shortGPT.engine.content_video_engine import ContentVideoEngine
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
from shortGPT.audio.coqui_voice_module import CoquiVoiceModule



# 准备 make_video 方法需要的参数
language = Language.ENGLISH
voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
#script = "Discover the enchantment of our castle, where history comes alive with every step. Begin your journey with a stunning view of its imposing facade, setting the stage for an adventure through time. Inside, grand halls and intricate details await, revealing secrets of the past and architectural wonders. Be mesmerized by ancient artifacts, breathtaking views from the tower, and the serene beauty of lush gardens. As the sun sets, casting a golden glow, [Castle Name] invites you to make your story part of its legend. Join us, and let the magic of history inspire your next adventure."
#script = "Meet our intrepid explorer, Techno cat, a serious cat at the helm of a digital voyage, paws clumsily navigating the chaos of codes and diagrams. Amidst the whirlwind of cuteness, challenges arise—screens filled with errors test our hero's resolve. But in the heart of adversity, our protagonist faces the ultimate test: the call of nature versus the call of duty. With a comical sigh of frustration, it chooses the former, surrendering to a peaceful nap on the keyboard, leaving a tapestry of random characters as the only evidence of its valiant effort. In this epic tale of paws versus pixels, our furry friend teaches us a valuable lesson: Sometimes, the bravest thing to do is to take a pause... and nap."

script = "Discover the majestic Tratzberg Castle, nestled in the heart of picturesque landscapes, offering a journey through history and breathtaking architecture. Come and be enchanted!Savor the ambiance: intimate gatherings, delectable cuisine, and joyful moments await your presence. Join the feast!"
isVertical = True # 或 False，取决于您的视频格式需求

def make_video(script, voice_module, isVertical, progress):
        videoEngine = ContentVideoEngine(voiceModule=voice_module, script=script, isVerticalFormat=isVertical)
        num_steps = videoEngine.get_total_steps()
        progress_counter = 0

        def logger(prog_str):
            progress(progress_counter / (num_steps), f"Creating video - {progress_counter} - {prog_str}")
        videoEngine.set_logger(logger)
        for step_num, step_info in videoEngine.makeContent():
            progress(progress_counter / (num_steps), f"Creating video - {step_info}")
            progress_counter += 1

        video_path = videoEngine.get_video_output_path()
        return video_path

# 定义一个简单的进度更新函数
def progress_update(progress, message):
    print(f"Progress: {progress*100}%, Message: {message}")


    

# 调用 make_video 方法
video_path = make_video(script, voice_module, isVertical, progress=progress_update)

print(f"Video saved to: {video_path}")
