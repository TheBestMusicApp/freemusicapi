# YouTube Music API Servisi

Bu proje, YouTube Music API'sine ücretsiz erişim sağlayan bir Flask uygulamasıdır.

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
[https://freemusicapi.onrender.com/API/home/TR/tr/15/](https://freemusicapi.onrender.com/API/home/TR/tr/15/)
```

### Mood Kategorileri
```
[https://freemusicapi.onrender.com//API/tasteprofile/TR/tr/](https://freemusicapi.onrender.com//API/tasteprofile/TR/tr/)
```

### Mood Playlistleri
```
[https://freemusicapi.onrender.com/API/mood/playlist/ggMPOg1uXzIxYkNac21YZ2Z0/TR/tr/](https://freemusicapi.onrender.com/API/mood/playlist/ggMPOg1uXzIxYkNac21YZ2Z0/TR/tr/)
```

### Trendler
```
[https://freemusicapi.onrender.com/API/trends/TR/tr](https://freemusicapi.onrender.com/API/trends/TR/tr)
```

### Arama
```
[https://freemusicapi.onrender.com/API/search/nimet/all/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/all/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/songs/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/songs/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/albums/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/albums/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/playlists/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/playlists/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/videos/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/videos/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/podcasts/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/podcasts/TR/tr)
[https://freemusicapi.onrender.com/API/search/nimet/episodes/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/episodes/TR/tr)

```

### Arama Önerileri
```
[https://freemusicapi.onrender.com/API/search/nimet/suggestions/TR/tr](https://freemusicapi.onrender.com/API/search/nimet/suggestions/TR/tr)
```

### Sanatçı Bilgileri
```
[https://freemusicapi.onrender.com/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g](https://freemusicapi.onrender.com/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g)
```

### Playlist Bilgileri
```
[https://freemusicapi.onrender.com/API/playlist/RDCLAK5uy_nX6UmhaEyaWe200N_vATudKrScwKqiawI/TR/tr](https://freemusicapi.onrender.com/API/playlist/RDCLAK5uy_nX6UmhaEyaWe200N_vATudKrScwKqiawI/TR/tr)
```

### Sanatçı Şarkıları
```
[https://freemusicapi.onrender.com/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g/TR/tr](https://freemusicapi.onrender.com/API/artist/UCBEUl6RYNAz4MDeEKXQPL3g/TR/tr)
```

### Şarkı Önerileri
```
[https://freemusicapi.onrender.com/API/song/suggestions/6F_ODhFVVow/TR/tr](https://freemusicapi.onrender.com/API/song/suggestions/6F_ODhFVVow/TR/tr)
```

### Şarkı Stream
```
[https://freemusicapi.onrender.com/API/stream/song/6F_ODhFVVow/TR/tr/123456](https://freemusicapi.onrender.com/API/stream/song/6F_ODhFVVow/TR/tr/123456)
```

### Şarkı Sözleri
```
[https://freemusicapi.onrender.com/API/lyrics/diodmido/nimet](https://freemusicapi.onrender.com/API/lyrics/diodmido/nimet)
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
