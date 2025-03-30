# YouTube Music API Servisi

Bu proje, YouTube Music API'sine erişim sağlayan bir Flask uygulamasıdır.

## Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
python app.py
```

## API Rotaları

### Ana Sayfa Verileri
```
http://localhost:5000/API/home/?limit=10&language=tr
```

### Mood Kategorileri
```
http://localhost:5000/API/mood/categories/?limit=10&language=tr
```

### Mood Playlistleri
```
http://localhost:5000/API/mood/playlists/?param=ggMPOg1uXzIxYkNac21YZ2Z0&language=tr
```

### Trendler
```
http://localhost:5000/API/trends/?country=TR
```

### Arama
```
http://localhost:5000/API/search/?q=nimet&language=tr
http://localhost:5000/API/search/?q=nimet&type=songs&language=tr
http://localhost:5000/API/search/?q=nimet&type=artists&language=tr
http://localhost:5000/API/search/?q=nimet&type=albums&language=tr
http://localhost:5000/API/search/?q=nimet&type=playlists&language=tr
http://localhost:5000/API/search/?q=nimet&type=videos&language=tr
http://localhost:5000/API/search/?q=nimet&type=podcasts&language=tr
http://localhost:5000/API/search/?q=nimet&type=episodes&language=tr
```

### Arama Önerileri
```
http://localhost:5000/API/search/?suggestions=nimet&language=tr
```

### Sanatçı Bilgileri
```
http://localhost:5000/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g
```

### Playlist Bilgileri
```
http://localhost:5000/API/playlist/RDCLAK5uy_nX6UmhaEyaWe200N_vATudKrScwKqiawI
```

### Sanatçı Şarkıları
```
http://localhost:5000/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g/songs?start=1&end=50&language=tr
```

### Şarkı Önerileri
```
http://localhost:5000/API/song/6F_ODhFVVow/suggestions?limit=10&language=tr
```

### Şarkı İndirme
```
http://localhost:5000/API/song/6F_ODhFVVow/download?path=\cıktı&language=tr
```

### Şarkı Stream
```
http://localhost:5000/API/song/6F_ODhFVVow/stream?signature_timestamp=123456&language=tr
```

### Şarkı Sözleri
```
http://localhost:5000/API/lyrics/?song=nimet&artist=didomido&language=tr
```

## Parametre Açıklamaları

- `limit`: Sonuç sayısı (varsayılan: 10)
- `language`: Dil seçeneği (varsayılan: tr)
- `q`: Arama terimi (zorunlu)
- `suggestions`: Arama önerileri için terim
- `type`: Arama türü (songs, artists, albums, playlists, videos, podcasts, episodes)
- `start`: Başlangıç indeksi (varsayılan: 1)
- `end`: Bitiş indeksi (varsayılan: 50)
- `path`: İndirme yolu (zorunlu)
- `signature_timestamp`: İmza zaman damgası (varsayılan: 123456)

## Özellikler

- Türkçe karakter desteği
- Şarkı indirme özelliği
- Şarkı sözleri erişimi
- Playlist bilgilerine erişim
- Arama önerileri 