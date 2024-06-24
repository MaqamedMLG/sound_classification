from flask import Blueprint, render_template, request, jsonify, send_file, after_this_request, flash
from flask_login import login_required, current_user
import os
import torch
import pickle
import numpy as np
from . import utils
from .models import User
from . import db
from .models import User, AudioFile
from flask import redirect
from flask import url_for
from werkzeug.utils import secure_filename
import soundfile as sf
from werkzeug.security import generate_password_hash
import io
import base64
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

views = Blueprint('views', __name__)

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

with open('C:/Users/Maham/Desktop/Thesis/Project/website/models/idx2cat.pkl', 'rb') as f:
    idx2cat = pickle.load(f)

model = torch.load('C:/Users/Maham/Desktop/Thesis/Project/website/models/resNet.pth', map_location=device)

#visualization of soundwaves function
def generate_waveform(file_path, predictions):
    y, sr = librosa.load(file_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    time = np.linspace(0, duration, len(y))

    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(time, y, color='blue')
    ax.set_title('Waveform of the uploaded audio with detected events', color='white', pad=60, fontsize=16)
    plt.xlabel('Time (seconds)', color='white')
    plt.ylabel('Amplitude', color='white')
    fig.patch.set_facecolor('#2B3E50')
    ax.set_facecolor('#2B3E50')
    ax.tick_params(axis='both', colors='white')

    for pred in predictions:
        start = pred['start']
        end = pred['end']
        label = pred['label']
        confidence = pred['confidence']

        ax.axvspan(start, end, color='red', alpha=0.3)
        ax.text((start + end) / 2, max(y) * 0.8, f"{label} ({confidence:.2f})",
                color='white', fontsize=10, ha='center', va='bottom', rotation=45, backgroundcolor='black')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    waveform_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return waveform_base64

#visualization of spectrograms function
def generate_spectrogram(file_path):
    y, sr = librosa.load(file_path, sr=None)
    S = librosa.feature.melspectrogram(y=y, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 4))
    img = librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', ax=ax)
    cbar = fig.colorbar(img, ax=ax, format='%+2.0f dB', label='Intensity (dB)')

    ax.set_title('Mel-frequency spectrogram of the uploaded audio', color='white')
    fig.patch.set_facecolor('#2B3E50')
    ax.set_facecolor('#2B3E50')
    ax.tick_params(axis='both', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.yaxis.set_tick_params(color='white')
    cbar.ax.yaxis.set_tick_params(labelcolor='white')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    spectrogram_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return spectrogram_base64

#prediction function
def predict_from_upload(model, cats, fpath, window_size=2, step_size=1):
    y, sr = librosa.load(fpath, sr=None)
    window_samples = int(window_size * sr)
    step_samples = int(step_size * sr)
    predictions = []

    for start in range(0, len(y) - window_samples + 1, step_samples):
        end = start + window_samples

        window = y[start:end]
        temp_path = 'temp_window.wav'
        sf.write(temp_path, window, sr)

        spec = utils.melspectrogram_db(temp_path)
        spec = utils.spec_to_img(spec)
        spec = torch.from_numpy(spec).to(device, dtype=torch.float32)

        preds = model.forward(spec.unsqueeze(0).unsqueeze(0))[0].cpu().detach().numpy()
        pred = {name: preds[idx] for idx, name in cats.items()}

        s = sum(np.exp(val) for val in pred.values())
        for key in pred:
            pred[key] = np.exp(pred[key]) / s

        sorted_pred = sorted(pred.items(), key=lambda x: x[1], reverse=True)
        top_pred = sorted_pred[0]
        if top_pred[1] > 0.5:
            predictions.append({
                'start': start / sr,
                'end': end / sr,
                'label': top_pred[0],
                'confidence': top_pred[1]
            })

    os.remove(temp_path)

    grouped_predictions = []
    if predictions:
        current_group = predictions[0]
        for pred in predictions[1:]:
            if pred['label'] == current_group['label'] and pred['confidence'] > 0.5:
                current_group['end'] = pred['end']
            else:
                grouped_predictions.append(current_group)
                current_group = pred
        grouped_predictions.append(current_group)

    return jsonify(grouped_predictions)


#home page route
@views.route('/homemain')
def homemain():
    return render_template("homemain.html", user=current_user)

# my profile route
@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        email = request.form.get('email')
        new_password = request.form.get('password')

        user = User.query.get(current_user.id)
        if user:
            user.firstName = firstName
            user.email = email

            if new_password:
                if len(new_password) >= 8:
                    user.password = generate_password_hash(new_password)
                    flash('✅ Profile updated!', category='true')
                else:
                    flash('⚠️ The password that you entered must be at least 8 characters. Please try again!', category='false')
            else:
                flash('✅ Profile updated!', category='true')

            db.session.commit()
        else:
            flash('User not found.', category='false')

    return render_template("profile.html", user=current_user)

# Main page route
@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)

#upload route
@views.route('/uploadajax', methods=['POST'])
@login_required
def upload():
    if 'inputFile' not in request.files:
        return jsonify({'error': 'No file input in the request'}), 400

    file = request.files['inputFile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.mimetype.split('/')[0] != 'audio':
        return jsonify({'error': 'The file is not an audio file'}), 400

    if file.content_length > 10 * 1024 * 1024:  # Check file size > 10MB
        return jsonify({'error': 'The file is too large. Please select an audio file less than 10MB.'}), 400

    filename = secure_filename(file.filename)
    temp_path = os.path.join('uploads', filename)
    file.save(temp_path)

    try:
        audio_info = sf.info(temp_path)
        file_duration = audio_info.duration
        file_type = audio_info.format
        file_size = os.path.getsize(temp_path)

        if file_size > 10 * 1024 * 1024:  # Double-check file size > 10MB
            return jsonify({'error': 'The file is too large. Please select an audio file less than 10MB.'}), 400

        response_data = {
            'duration': file_duration,
            'type': file_type,
            'size': file_size,
        }

        prediction = predict_from_upload(model, idx2cat, temp_path)
        prediction_data = prediction.get_json()
        response_data['predictions'] = prediction_data

        spectrogram_data = generate_spectrogram(temp_path)
        response_data['spectrogram'] = f"data:image/png;base64,{spectrogram_data}"

        waveform_data = generate_waveform(temp_path, prediction_data)
        response_data['waveform'] = f"data:image/png;base64,{waveform_data}"

        new_file = AudioFile(name=filename, data=file.read(), mimetype=file.mimetype, user_id=current_user.id)
        db.session.add(new_file)
        db.session.commit()

        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

#clear file
@views.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_audio(file_id):
    audio_to_delete = AudioFile.query.get_or_404(file_id)
    if audio_to_delete.user_id != current_user.id:
        return redirect(url_for('views.home'))

    db.session.delete(audio_to_delete)
    db.session.commit()
    return redirect(url_for('views.home'))

#clear all
@views.route('/delete-all-audios', methods=['POST'])
@login_required
def delete_all_audios():
    try:
        AudioFile.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
    except Exception as e:
        flash('⚠️ Error in deleting the audio files', category='false')
        return jsonify({'error': str(e)}), 500

    return redirect(url_for('views.home'))