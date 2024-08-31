from datetime import datetime
import os

def run_imagen(audio_path, whisper_model, imagen_model, output_path, index):
    # 音声をテキストに変換
    transcribe_text, detected_language = whisper_model.transcribe_audio2text(audio_path)
    print(f"Detected text: {transcribe_text}")

    # 画像生成
    try:
        generated_image = imagen_model.generate_image(transcribe_text, index, detected_language)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_filename = f"{output_path}/imagen_output_{timestamp}_{index}.png"
        print(f"Saving image to {output_filename}")
        generated_image.save(output_filename)
        print(f"Imagen saved: {output_filename}")
        os.chmod(output_filename, 0o666)
    except Exception as e:
        print(f"Error saving image: {e}")
