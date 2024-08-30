from datetime import datetime
import os

def process_audio(audio_path, whisper_model, imagen_model, output_path):
    # Transcribe audio to text
    transcribe_text, detected_language = whisper_model.transcribe_audio2text(audio_path)
    print(f"Detected text: {transcribe_text}")

    # Generate image
    index = "0-0"  # Placeholder for index
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        audio_file_path = sys.argv[1]
        process_audio(audio_file_path)
    else:
        print("No audio file path provided.")
