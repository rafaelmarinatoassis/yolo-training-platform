import os
import shutil
from urllib.parse import urlparse

import requests
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

models_bp = Blueprint('models', __name__)

ULTRALYTICS_KNOWN_MODELS = {
    'yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt', 'yolov8x.pt',
    'yolov8n-seg.pt', 'yolov8s-seg.pt', 'yolov8m-seg.pt', 'yolov8l-seg.pt', 'yolov8x-seg.pt',
    'yolov8n-pose.pt', 'yolov8s-pose.pt', 'yolov8m-pose.pt', 'yolov8l-pose.pt', 'yolov8x-pose.pt',
    'yolov8n-cls.pt', 'yolov8s-cls.pt', 'yolov8m-cls.pt', 'yolov8l-cls.pt', 'yolov8x-cls.pt',
    'yolov8n-p6.pt', 'yolov8s-p6.pt', 'yolov8m-p6.pt', 'yolov8l-p6.pt', 'yolov8x-p6.pt',
    'yolov5n.pt', 'yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt',
    'yolov5n6.pt', 'yolov5s6.pt', 'yolov5m6.pt', 'yolov5l6.pt', 'yolov5x6.pt',
    'yolov3.pt', 'yolov3-spp.pt', 'yolov3-tiny.pt',
    'yolo_nas_s.pt', 'yolo_nas_m.pt', 'yolo_nas_l.pt',
}


def _models_cache_dir():
    cache_dir = os.path.join('data', 'models_cache')
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _is_url(value):
    try:
        parsed = urlparse(value)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def _build_model_path(model_name):
    filename = secure_filename(os.path.basename(model_name))
    return os.path.join(_models_cache_dir(), filename)


@models_bp.route('/models/list', methods=['GET'])
def list_models():
    cache_dir = _models_cache_dir()
    models = []
    for file_name in sorted(os.listdir(cache_dir)):
        if not file_name.lower().endswith('.pt'):
            continue
        file_path = os.path.join(cache_dir, file_name)
        models.append({
            'name': file_name,
            'path': os.path.abspath(file_path),
            'size_bytes': os.path.getsize(file_path)
        })

    return jsonify({'models': models, 'count': len(models)})


@models_bp.route('/models/check', methods=['POST'])
def check_model():
    data = request.get_json(silent=True) or {}
    model_name = (data.get('model_name') or '').strip()
    model_url = (data.get('model_url') or '').strip()

    if not model_name:
        return jsonify({'error': 'model_name is required'}), 400

    # Absolute or relative local path explicitly provided by user
    if os.path.exists(model_name):
        return jsonify({
            'exists': True,
            'local_path': os.path.abspath(model_name),
            'downloadable': True,
            'message': 'Modelo ja existe localmente.'
        })

    target_path = _build_model_path(model_name)
    if os.path.exists(target_path):
        return jsonify({
            'exists': True,
            'local_path': os.path.abspath(target_path),
            'downloadable': True,
            'message': 'Modelo disponivel no cache local.'
        })

    downloadable = bool(model_url) or model_name.lower() in ULTRALYTICS_KNOWN_MODELS
    return jsonify({
        'exists': False,
        'downloadable': downloadable,
        'local_path': os.path.abspath(target_path),
        'message': (
            'Modelo nao encontrado localmente.'
            if downloadable
            else 'Modelo nao encontrado localmente e nao esta na lista de pesos oficiais desta versao.'
        )
    })


@models_bp.route('/models/download', methods=['POST'])
def download_model():
    data = request.get_json(silent=True) or {}
    model_name = (data.get('model_name') or '').strip()
    model_url = (data.get('model_url') or '').strip()

    if not model_name:
        return jsonify({'error': 'model_name is required'}), 400

    # If user passed an existing local path, no download needed.
    if os.path.exists(model_name):
        return jsonify({
            'success': True,
            'downloaded': False,
            'model_name': os.path.basename(model_name),
            'local_path': os.path.abspath(model_name),
            'message': 'Modelo local ja disponivel.'
        })

    target_path = _build_model_path(model_name)
    if os.path.exists(target_path):
        return jsonify({
            'success': True,
            'downloaded': False,
            'model_name': os.path.basename(target_path),
            'local_path': os.path.abspath(target_path),
            'message': 'Modelo j estava no cache.'
        })

    try:
        if model_url:
            if not _is_url(model_url):
                return jsonify({'error': 'model_url must be a valid http(s) URL'}), 400

            with requests.get(model_url, stream=True, timeout=120) as response:
                response.raise_for_status()
                with open(target_path, 'wb') as model_file:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            model_file.write(chunk)
        else:
            from ultralytics.utils.downloads import attempt_download_asset

            downloaded_path = attempt_download_asset(model_name)
            if not downloaded_path or not os.path.exists(downloaded_path):
                return jsonify({
                    'error': (
                        'Modelo nao encontrado no repositorio da versao instalada do Ultralytics. '
                        'Use um modelo YOLOv8 oficial (ex.: yolov8n.pt) ou informe model_url.'
                    )
                }), 400

            if os.path.abspath(downloaded_path) != os.path.abspath(target_path):
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy2(downloaded_path, target_path)

        return jsonify({
            'success': True,
            'downloaded': True,
            'model_name': os.path.basename(target_path),
            'local_path': os.path.abspath(target_path),
            'message': 'Download concluido com sucesso.'
        })

    except requests.RequestException as e:
        return jsonify({'error': f'Falha no download HTTP: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

