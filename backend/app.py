import json
import os
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
import yt_dlp
import requests

# --- FLASK UYGULAMASI ---
app = Flask((__name__, template_folder="templates"))

# --- TEMEL DEĞİŞKENLER ---
USERS_DIR = 'Users'
if not os.path.exists(USERS_DIR):
    os.makedirs(USERS_DIR)

# --- YARDIMCI FONKSİYONLAR ---
def read_json(file_path, default_data=None):
    """JSON dosyasını okur, yoksa oluşturur."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if default_data is not None:
            write_json(file_path, default_data)
            return default_data
        return {}

def write_json(file_path, data):
    """Veriyi JSON dosyasına yazar."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- SAYFA ROTALARI ---
@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/login')
def login_page():
    return render_template('Login.html')

@app.route('/search')
def search_page():
    return render_template('Search.html')

@app.route('/library')
def library_page():
    return render_template('Library.html')
    
@app.route('/player')
def player_page():
    return render_template('Player.html')

# --- API ROTALARI ---

@app.route('/api/login', methods=['POST'])
def handle_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    passwords = read_json('Passwords.json', {})
    
    if username in passwords and passwords[username] == password:
        return jsonify({"success": True, "message": "Giriş başarılı."})
    return jsonify({"success": False, "message": "Kullanıcı adı veya şifre hatalı."}), 401

@app.route('/api/register', methods=['POST'])
def handle_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    passwords = read_json('Passwords.json', {})
    
    if username in passwords:
        return jsonify({"success": False, "message": "Bu kullanıcı adı zaten alınmış."}), 409
    
    passwords[username] = password
    write_json('Passwords.json', passwords)
    
    # Kullanıcıya özel JSON dosyalarını oluştur
    user_dir = os.path.join(USERS_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    write_json(os.path.join(user_dir, f'{username}.json'), {"history": []})
    write_json(os.path.join(user_dir, f'{username}likedandplaylist.json'), {"liked": [], "playlists": []})
    
    return jsonify({"success": True, "message": "Kayıt başarılı."})

@app.route('/api/search_songs', methods=['GET'])
def search_songs():
    query = request.args.get('q', '').lower()
    links_data = read_json('Links.json', {})
    results = []
    
    if not query:
        return jsonify(results)

    for artist, songs in links_data.items():
        for song_id, song_info in songs.items():
            if (query in song_info['title'].lower()) or (query in song_info['artist'].lower()) or (query in song_info['album'].lower()):
                results.append({
                    "id": f"{artist}/{song_id}",
                    "title": song_info['title'],
                    "artist": song_info['artist'],
                    "album": song_info['album'],
                    "cover": song_info['cover_url']
                })
    return jsonify(results)

@app.route('/stream/<artist>/<song_id>')
def stream_audio(artist, song_id):
    """Proxy stream: YouTube'dan ses akışını alıp istemciye yönlendirir."""
    links_data = read_json('Links.json')
    try:
        song_info = links_data[artist][song_id]
        youtube_url = song_info['youtube_url']

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            audio_url = info['url']

        # YouTube'dan ses akışını al ve istemciye parça parça gönder
        req = requests.get(audio_url, stream=True)
        return Response(req.iter_content(chunk_size=1024), content_type=req.headers['Content-Type'])

    except (KeyError, TypeError):
        return "Şarkı bulunamadı.", 404

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    # Bu kısım Algorithm.py ile entegre edilecek
    # Şimdilik popüler şarkılardan rastgele bir seçki gönderelim
    popular_data = read_json('Popular.json', {"songs": []})
    return jsonify(popular_data['songs'][:10]) # İlk 10 popüler şarkıyı öneri olarak gönder

# --- ANA ÇALIŞTIRMA ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
