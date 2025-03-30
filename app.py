from flask import Flask, request, jsonify, Response
import json
from ytmusicapi import YTMusic
import os
import requests
import yt_dlp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Türkçe karakterlerin düzgün görüntülenmesi için
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Her yanıt için Content-Type başlığını UTF-8 ile ayarla
@app.after_request
def add_header(response):
    if response.headers.get('Content-Type') == 'application/json':
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# Varsayılan değerler
DEFAULT_LIMIT = 10
DEFAULT_LANG = "tr"
DEFAULT_START = 1
DEFAULT_END = 50
DEFAULT_SIGNATURE_TIMESTAMP = 123456

# Yanıt çevirici fonksiyon - Unicode karakterleri düzgün hale getirir
def clean_response(resp):
    if isinstance(resp, dict):
        return {k: clean_response(v) for k, v in resp.items()}
    elif isinstance(resp, list):
        return [clean_response(item) for item in resp]
    elif isinstance(resp, str):
        return resp.encode('latin1').decode('utf-8') if '\\u' in resp else resp
    else:
        return resp

def create_response(data, status_code=200):
    """Türkçe karakterleri düzgün görüntülemek için özel bir response oluşturucu"""
    resp = app.response_class(
        response=json.dumps(clean_response(data), ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )
    return resp

# Şarkı sözleri modülünden alınan fonksiyonlar
def clean_unicode_chars(text):
    if isinstance(text, str):
        return text.encode('latin1').decode('utf-8') if '\\u' in text else text
    return text

def get_lyrics(artist_name, track_name):
    api_url = f"https://lrclib.net/api/get?artist_name={artist_name}&track_name={track_name}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        
        # Parse the JSON response
        data = response.json()

        # Veriyi temizle
        if isinstance(data, dict):
            if 'syncedLyrics' in data:
                data['syncedLyrics'] = clean_unicode_chars(data['syncedLyrics'])
            if 'plainLyrics' in data:
                data['plainLyrics'] = clean_unicode_chars(data['plainLyrics'])
            if 'lyrics' in data:
                data['lyrics'] = clean_unicode_chars(data['lyrics'])

        lyrics_data = {
            "Süreli Şarkı Sözleri": data.get('syncedLyrics', data.get('lyrics', "Şarkı sözleri bulunamadı")),
            "Süresiz Şarkı Sözleri": data.get('plainLyrics', "Şarkı sözleri bulunamadı")
        }
        
        # JSON yanıtında Türkçe karakterleri düzgün görüntülemek için ensure_ascii=False
        return Response(
            json.dumps(lyrics_data, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )
            
    except requests.exceptions.RequestException as e:
        error_data = {
            "Süreli Şarkı Sözleri": f"Şarkı sözleri alınamadı: {str(e)}",
            "Süresiz Şarkı Sözleri": f"Şarkı sözleri alınamadı: {str(e)}"
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )
    except Exception as e:
        error_data = {
            "Süreli Şarkı Sözleri": f"Bir beklenmeyen hata oluştu: {str(e)}",
            "Süresiz Şarkı Sözleri": f"Bir beklenmeyen hata oluştu: {str(e)}"
        }
        return Response(
            json.dumps(error_data, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )

@app.route('/API/home/', methods=['GET'])
def home():
    limit = request.args.get('limit', DEFAULT_LIMIT, type=int)
    language = request.args.get('language', DEFAULT_LANG)
    
    ytmusic = YTMusic(language=language, location="TR")
    result = ytmusic.get_home(limit)
    
    return create_response(result)

@app.route('/API/mood/categories/', methods=['GET'])
def mood_categories():
    limit = request.args.get('limit', DEFAULT_LIMIT, type=int)
    language = request.args.get('language', DEFAULT_LANG)
    
    ytmusic = YTMusic(language=language)
    result = ytmusic.get_mood_categories()
    
    return create_response(result)

@app.route('/API/mood/playlists/', methods=['GET'])
def mood_playlists():
    param = request.args.get('param')
    language = request.args.get('language', DEFAULT_LANG)
    
    if not param:
        return create_response({"error": "param parametresi zorunludur"}, 400)
    
    ytmusic = YTMusic(language=language)
    result = ytmusic.get_mood_playlists(param)
    
    return create_response(result)

@app.route('/API/trends/', methods=['GET'])
def trends():
    country = request.args.get('country')
    
    if not country:
        return create_response({"error": "country parametresi zorunludur"}, 400)
    
    try:
        ytmusic = YTMusic()
        
        # Trend bilgilerini alırken hata ayıklama için
        print(f"Trendler için istek: ülke={country}")
        
        # get_charts fonksiyonunu çağıralım ve sonucu yazdıralım
        result = ytmusic.get_charts(country)

        
        # Sonucun içeriğini kontrol edelim
        if result is None:
            return create_response({"error": "Trendler için veri bulunamadı"}, 404)
            
        
        # Serileştirilebilir veriler için fonksiyon
        def is_json_serializable(obj):
            try:
                json.dumps(obj)
                return True
            except (TypeError, OverflowError):
                return False
                
        # Serileştirilemez verileri süzme fonksiyonu
        def filter_non_serializable(data):
            if isinstance(data, dict):
                return {k: filter_non_serializable(v) for k, v in data.items() if is_json_serializable(k)}
            elif isinstance(data, list):
                return [filter_non_serializable(item) for item in data if is_json_serializable(item)]
            elif is_json_serializable(data):
                return data
            else:
                return str(data)
        
        # Veri yapısını temizleyelim
        filtered_result = filter_non_serializable(result)
        
        return create_response(filtered_result)
    except Exception as e:
        print(f"Trendler alınırken hata: {str(e)}")
        return create_response({"error": f"Trendler alınırken hata oluştu: {str(e)}"}, 500)

@app.route('/API/search/', methods=['GET'])
def search():
    q = request.args.get('q')
    search_type = request.args.get('type')
    language = request.args.get('language', DEFAULT_LANG)
    suggestions = request.args.get('suggestions')
    
    if suggestions:
        ytmusic = YTMusic(language=language)
        result = ytmusic.get_search_suggestions(suggestions, detailed_runs=False)
        return create_response(result)
    
    if not q:
        return create_response({"error": "q parametresi zorunludur"}, 400)
    
    ytmusic = YTMusic(language=language)
    
    if search_type:
        result = ytmusic.search(q, filter=search_type)
    else:
        result = ytmusic.search(q)
    
    return create_response(result)

@app.route('/API/artist/<artist_id>', methods=['GET'])
def artist_details(artist_id):
    ytmusic = YTMusic()
    result = ytmusic.get_artist(artist_id)
    
    return create_response(result)

@app.route('/API/playlist/<playlist_id>', methods=['GET'])
def playlist_details(playlist_id):
    ytmusic = YTMusic()
    result = ytmusic.get_playlist(playlist_id)
    
    return create_response(result)

@app.route('/API/artist/<artist_id>/songs', methods=['GET'])
def artist_songs(artist_id):
    language = request.args.get('language', DEFAULT_LANG)
    
    try:
        ytmusic = YTMusic(language=language)
        # Sanatçı bilgilerini alalım
        artist_info = ytmusic.get_artist(artist_id)
        
        # Sanatçının şarkılarını içeren bir sonuç oluşturalım
        result = {}
        
        # Sanatçı bilgisi içinde "songs" alanı varsa şarkıları alalım
        if "songs" in artist_info:
            result["songs"] = artist_info["songs"]
        
        # Albümler, singles veya videos gibi diğer içerikleri de ekleyelim
        for section in ["albums", "singles", "videos"]:
            if section in artist_info:
                result[section] = artist_info[section]
        
        return create_response(result)
    except Exception as e:
        return create_response({"error": f"Sanatçı şarkıları getirilirken hata oluştu: {str(e)}"}, 500)

@app.route('/API/song/<song_id>/suggestions', methods=['GET'])
def song_suggestions(song_id):
    language = request.args.get('language', DEFAULT_LANG)
    
    try:
        ytmusic = YTMusic(language=language)
        
        # song.suggestions.py'deki yaklaşımı kullanarak get_watch_playlist fonksiyonunu çağıralım
        watch_playlist = ytmusic.get_watch_playlist(videoId=song_id)
        
        # Önerileri kontrol edelim
        if "tracks" in watch_playlist and watch_playlist["tracks"]:
            related_tracks = watch_playlist["tracks"]
            # İlk 50 öneriyi döndürelim (varsa)
            result = related_tracks[:50]
            return create_response(result)
        else:
            return create_response({"error": "Bu şarkı için öneri bulunamadı"}, 404)
            
    except Exception as e:
        return create_response({"error": f"Öneriler getirilirken hata oluştu: {str(e)}"}, 500)

@app.route('/API/song/<song_id>/download', methods=['GET'])
def song_download(song_id):
    path = request.args.get('path')
    language = request.args.get('language', DEFAULT_LANG)
    
    if not path:
        return create_response({"error": "path parametresi zorunludur"}, 400)
    
    url = f"https://www.youtube.com/watch?v={song_id}"
    
    try:
        # Ses dosyasını indirme seçenekleri
        ydl_opts = {
            'format': 'bestaudio/best',  # En iyi ses formatını seç
            'quiet': False,  # Daha fazla bilgi al
            'extractaudio': True,  # Ses dosyasını çıkar
            'audioquality': 1,  # En yüksek ses kalitesi
            'noplaylist': True,  # Playlist yerine sadece tek video
            'outtmpl': f'{path}/%(id)s.%(ext)s',  # Dosyanın kaydedileceği yer
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        response_data = {
            "status": "success", 
            "message": f"Şarkı {path} yoluna indirildi", 
            "filename": f"{info['id']}.{info['ext'] if 'ext' in info else 'mp3'}"
        }
        
        return create_response(response_data)
            
    except Exception as e:
        return create_response({"error": str(e)}, 500)

@app.route('/API/song/<song_id>/stream', methods=['GET'])
def song_stream(song_id):
    signature_timestamp = request.args.get('signature_timestamp', DEFAULT_SIGNATURE_TIMESTAMP)
    language = request.args.get('language', DEFAULT_LANG)
    
    ytmusic = YTMusic(language=language)
    
    try:
        result = ytmusic.get_song(videoId=song_id, signatureTimestamp=signature_timestamp)
        return create_response(result)
    except Exception as e:
        return create_response({"error": str(e)}, 500)

@app.route('/API/lyrics/', methods=['GET'])
def lyrics():
    song = request.args.get('song')
    artist = request.args.get('artist')
    language = request.args.get('language', DEFAULT_LANG)
    
    if not song or not artist:
        return create_response({"error": "song ve artist parametreleri zorunludur"}, 400)
    
    try:
        lyrics_data = get_lyrics(artist, song)
        return lyrics_data
    except Exception as e:
        return create_response({"error": str(e)}, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 
    
