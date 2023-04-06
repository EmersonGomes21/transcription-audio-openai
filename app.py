from dotenv import load_dotenv
import os
import time
import openai
from flask import Flask, request
import requests
from werkzeug.utils import secure_filename
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
openai.api_key = os.getenv("KEY_OPENAI")

ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# Função auxiliar para verificar se o tipo de arquivo é permitido


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/', methods=['GET'])
def index():
    return 'OK', 200


@app.route('/upload-audio', methods=['POST'])
def upload_audio():

    # Verifica se o arquivo de áudio foi enviado na requisição
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    file = request.files['file']

    # Verifica se o nome do arquivo é válido
    if file.filename == '':
        return 'Nome de arquivo inválido', 400

        # Verifica se o arquivo enviado é de um tipo válido
    # if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
    #     return 'Tipo de arquivo inválido. Tipos permitidos: mp3, wav.', 400

        # Salva o arquivo no servidor
    filename = secure_filename(
        str(round(time.time() * 1000)) + '_' + str(file.filename))

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    audio = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb')

    try:
        transcription = openai.Audio.transcribe("whisper-1", file=audio)
        return transcription, 200
    except requests.exceptions.RequestException as e:
        return f'Erro ao transcrever áudio: {e}', 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
