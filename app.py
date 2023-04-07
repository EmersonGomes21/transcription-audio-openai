from dotenv import load_dotenv
import os
import time
import openai
from flask import Flask, request, jsonify
import requests
from werkzeug.utils import secure_filename
load_dotenv()

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = './uploads'
openai.api_key = os.getenv("KEY_OPENAI") or os.environ.get('API_KEY')

ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}

# Helper function to check if the file type is allowed


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'ok'}), 200


@app.route('/upload-audio', methods=['POST'])
def upload_audio():

   # Check if the audio file was sent in the request
    if not request.files.get('file'):
        return 'arquivo inválido', 400

    file = request.files['file']

    # Check if the uploaded file is of a valid type
    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        return jsonify({
            'message':  'Tipo de arquivo inválido. Tipos permitidos: ' + ', '.join(ALLOWED_EXTENSIONS)+'.'}), 400

    filename = secure_filename(f"{int(time.time() * 1000)}_{file.filename}")
# Save the file in server
    pathFileTemp = filename
    file.save(filename)
    fileTemp = open(filename, 'rb')

    try:
        transcription = openai.Audio.transcribe("whisper-1", file=fileTemp)
        return transcription, 200
    except requests.exceptions.RequestException as e:
        return f'Erro ao transcrever áudio: {e}', 500
    finally:
        fileTemp.close()
        os.remove(pathFileTemp)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
