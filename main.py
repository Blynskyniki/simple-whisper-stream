from flask import Flask, request, jsonify, Response, render_template
import whisper
import os
import json
import time

app = Flask(__name__)


print("Загрузка модели Whisper...", flush=True)
model = whisper.load_model("large")
print("Модель загружена успешно", flush=True)

def transcribe_audio_in_realtime(file_path):

    try:
        print(f"Начинаем транскрипцию файла: {file_path}", flush=True)


        result = model.transcribe(file_path, verbose=True, language='ru')


        for i, segment in enumerate(result['segments']):
            text = segment['text']
            data = {
                'text': text
             }


            yield f"data: {json.dumps(data)}\n\n"




    except Exception as e:
        # Ловим ошибки и передаем их в поток в формате SSE
        error_message = {'error': str(e)}
        print(f"Ошибка при транскрипции: {str(e)}", flush=True)
        yield f"data: {json.dumps(error_message)}\n\n"

@app.route('/')
def index():
    """Отдаем HTML страницу по корневому маршруту"""
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    print(f"Файл {file.filename} сохранен на сервере для транскрипции", flush=True)

    # Возвращаем SSE-ответ с частичной транскрибацией
    return Response(transcribe_audio_in_realtime(file_path), mimetype='text/event-stream')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, threaded=True)
