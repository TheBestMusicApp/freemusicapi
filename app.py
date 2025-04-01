from flask import Flask, request, jsonify, Response, render_template
import json
from ytmusicapi import YTMusic
import os
import requests
from dotenv import load_dotenv

# .env dosyasını yükle (varsa)
load_dotenv()

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
DEFAULT_COUNTRY ="TR"
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404 # HTTP 404 kodu ile döndür

@app.errorhandler(500)
def page_not_found(error):
    return render_template("404.html"), 500 # HTTP 500 kodu ile döndür

# 404
@app.route("/404")
def custom_404():
    return render_template("404.html"), 404  # HTTP 404 kodu ile döndür

@app.route("/docs")
def docs():
    return render_template("docs.html"), 200

# Ana sayfa
@app.route('/')
def index():
    return render_template("docs.html"), 200

# TASTE PROFİLE
@app.route('/API/tasteprofile/', defaults={'country': None, 'language': None})
@app.route('/API/tasteprofile/<country>/', defaults={'language': None})
@app.route('/API/tasteprofile/<country>/<language>/')
def tasteprofile(country, language):
    country = country or DEFAULT_COUNTRY  # Varsayılan değerleri kullan
    language = language or DEFAULT_LANG
    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_tasteprofile()

    return create_response(result)

# HOME
@app.route('/API/home/', defaults={'country': None, 'language': None, 'limit': None})
@app.route('/API/home/<country>/', defaults={'language': None, 'limit': None})
@app.route('/API/home/<country>/<language>/', defaults={'limit': None})
@app.route('/API/home/<country>/<language>/<int:limit>/')
def home(country, language, limit):
    country = country or DEFAULT_COUNTRY  # Varsayılan değerleri kullan
    language = language or DEFAULT_LANG
    limit = limit or DEFAULT_LIMIT

    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_home(limit)

    return create_response(result)

# MOOD CATEGORİES
@app.route('/API/mood/categories/', defaults={'country': None, 'language': None})
@app.route('/API/mood/categories/<country>/', defaults={'language': None})
@app.route('/API/mood/categories/<country>/<language>/')
def mood_categories(country, language):
    country = country or DEFAULT_COUNTRY  # Varsayılan değerleri kullan
    language = language or DEFAULT_LANG

    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_mood_categories()

    return create_response(result)

# MOOD PLAYLIST
@app.route('/API/mood/playlist/', defaults={'param': None, 'country': None, 'language': None})
@app.route('/API/mood/playlist/<param>/', defaults={'country': None,'language': None})
@app.route('/API/mood/playlist/<param>/<country>/', defaults={'language': None})
@app.route('/API/mood/playlist/<param>/<country>/<language>/')
def mood_playlists(param, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    param = param or None  # param zorunlu değil
    language = language or DEFAULT_LANG  # Eğer language parametresi verilmezse varsayılan değer kullanılır
    country = country or DEFAULT_COUNTRY

    if not param:
        return create_response({"error": "param parametresi zorunludur"}, 400)
    
    try:
        # YTMusic nesnesi oluşturuluyor
        ytmusic = YTMusic(language=language, location=country)
        
        # Mood Playlists verilerini al
        result = ytmusic.get_mood_playlists(param)
        
        # Sonuç kontrolü
        if result is None:
            return create_response({"error": "Mood Playlists için veri bulunamadı"}, 404)
        
        return create_response(result)
    
    except Exception as e:
        print(f"Mood playlists alınırken hata: {str(e)}")
        return create_response({"error": f"Mood playlists alınırken hata oluştu: {str(e)}"}, 500)

# TRENDS MUSİCS
@app.route('/API/trends/', defaults={'country': None, 'language': None})
@app.route('/API/trends/<country>/', defaults={'language': None})
@app.route('/API/trends/<country>/<language>/')
def trends(country, language):
    # Parametrelerin varsayılan değerler ile alınması
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG

    if not country:
        return create_response({"error": "country parametresi zorunludur"}, 400)
    
    try:
        # YTMusic nesnesi oluşturuluyor
        ytmusic = YTMusic(language=language, location=country)
        
        # Trend bilgilerini alırken hata ayıklama için
        print(f"Trendler için istek: ülke={country}, dil={language}")
        
        # Trendler için veriyi al
        result = ytmusic.get_charts(country)
        
        # Sonucun içeriğini kontrol et
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
        
        # Veri yapısını temizle
        filtered_result = filter_non_serializable(result)
        
        return create_response(filtered_result)
    
    except Exception as e:
        print(f"Trendler alınırken hata: {str(e)}")
        return create_response({"error": f"Trendler alınırken hata oluştu: {str(e)}"}, 500)

# SEARCH 
@app.route('/API/search/', defaults={'q': None, 'search_type': None, 'country': None, 'language': None})
@app.route('/API/search/<q>/', defaults={'search_type': None, 'country': None, 'language': None})
@app.route('/API/search/<q>/<search_type>/', defaults={'country': None, 'language': None})
@app.route('/API/search/<q>/<search_type>/<country>/<language>/')
def search(q, search_type, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    q = q or None
    search_type = search_type or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG

    # Eğer q parametresi eksikse hata mesajı
    if not q:
        return create_response({"error": "q parametresi zorunludur"}, 400)

    # Eğer search_type "suggestions" ise, arama önerileri al
    if search_type == "suggestions":
        try:
            ytmusic = YTMusic(language=language, location=country)
            result = ytmusic.get_search_suggestions(q, detailed_runs=False)  # suggestions özelliği
            return create_response(result)
        except Exception as e:
            print(f"Öneri alınırken hata: {str(e)}")
            return create_response({"error": f"Öneri alınırken hata oluştu: {str(e)}"}, 500)

    # Eğer search_type "all" ise, genel arama yapılır
    if search_type == "all":
        try:
            ytmusic = YTMusic(language=language, location=country)
            result = ytmusic.search(q)  # Genel arama
            return create_response(result)
        except Exception as e:
            print(f"Genel arama yapılırken hata: {str(e)}")
            return create_response({"error": f"Genel arama yapılırken hata oluştu: {str(e)}"}, 500)

    # Diğer türlerde (normal arama) arama yapılır
    try:
        ytmusic = YTMusic(language=language, location=country)
        
        # search_type varsa, ona göre arama yapılır, yoksa genel arama yapılır
        if search_type:
            result = ytmusic.search(q, filter=search_type)
        else:
            result = ytmusic.search(q)
        
        return create_response(result)
    except Exception as e:
        print(f"Arama yapılırken hata: {str(e)}")
        return create_response({"error": f"Arama yapılırken hata oluştu: {str(e)}"}, 500)

# ARTIST DETAİLS
@app.route('/API/artist/', defaults={'artist_id': None,  'country': None, 'language': None})
@app.route('/API/artist/<artist_id>/', defaults={ 'country': None, 'language': None})
@app.route('/API/artist/<artist_id>/<country>/', defaults={'language': None})
@app.route('/API/artist/<artist_id>/<country>/<language>/')
def artist_details(artist_id, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    artist_id = artist_id or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG

    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_artist(artist_id)

    return create_response(result)

# ARTIST SONGS
@app.route('/API/artist/songs/', defaults={'artist_id': None,  'country': None, 'language': None})
@app.route('/API/artist/songs/<artist_id>/', defaults={ 'country': None, 'language': None})
@app.route('/API/artist/songs/<artist_id>/<country>/', defaults={'language': None})
@app.route('/API/artist/songs/<artist_id>/<country>/<language>/')
def artist_songs(artist_id, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    artist_id = artist_id or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG

    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_artist(artist_id)

    return create_response(result)

# PLAYLİST DETAILS
@app.route('/API/playlist/', defaults={'playlist_id': None,  'country': None, 'language': None})
@app.route('/API/playlist/<playlist_id>/', defaults={ 'country': None, 'language': None})
@app.route('/API/playlist/<playlist_id>/<country>/', defaults={'language': None})
@app.route('/API/playlist/<playlist_id>/<country>/<language>/')
def playlist_details(playlist_id, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    playlist_id = playlist_id or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG

    ytmusic = YTMusic(language=language, location=country)
    result = ytmusic.get_playlist(playlist_id)
    
    return create_response(result)

# SONG SUGGESTIONS
@app.route('/API/song/suggestions/', defaults={'song_id': None,  'country': None, 'language': None})
@app.route('/API/song/suggestions/<song_id>/', defaults={ 'country': None, 'language': None})
@app.route('/API/song/suggestions/<song_id>/<country>/', defaults={'language': None})
@app.route('/API/song/suggestions/<song_id>/<country>/<language>/')
def song_suggestions(song_id, country, language):
    # Parametrelerin varsayılan değerler ile alınması
    song_id = song_id or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG
    try:
        ytmusic = YTMusic(language=language, location=country)
        
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

#SONG STREAM
@app.route('/API/stream/', defaults={'song_id': None,  'country': None, 'language': None, 'signature_timestamp': None})
@app.route('/API/stream/<song_id>/', defaults={ 'country': None, 'language': None, 'signature_timestamp': None})
@app.route('/API/stream/<song_id>/<country>/', defaults={'language': None, 'signature_timestamp': None})
@app.route('/API/stream/<song_id>/<country>/<language>/', defaults={'signature_timestamp': None})
@app.route('/API/stream/<song_id>/<country>/<language>/<int:signature_timestamp>/')
def song_stream(song_id, signature_timestamp, country, language):
    song_id = song_id or None
    country = country or DEFAULT_COUNTRY
    language = language or DEFAULT_LANG
    signature_timestamp = signature_timestamp or DEFAULT_SIGNATURE_TIMESTAMP

    ytmusic = YTMusic(language=language, location=country)
    
    result = ytmusic.get_song(videoId=song_id, signatureTimestamp=signature_timestamp)
    return create_response(result)

# LYRICS
@app.route('/API/lyrics/', defaults={'song': None, 'artist': None})
@app.route('/API/lyrics/<artist>/', defaults={'song': None})
@app.route('/API/lyrics/<artist>/<song>/')
def lyrics(artist, song):
    song = song or None
    artist = artist or None
    api_url = f"https://lrclib.net/api/get?artist_name={artist}&track_name={song}"
    
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

if __name__ == '__main__':
    # Render.com için port ayarı
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 