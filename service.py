import json
import time
import schedule
from ytmusicapi import YTMusic
import yt_dlp

class MusicDataService:
    def __init__(self, artists_file='artists.json', links_file='Links.json'):
        self.ytmusic = YTMusic()
        self.artists_file = artists_file
        self.links_file = links_file
        self.links_data = self._load_json(self.links_file, {})

    def _load_json(self, file_path, default_data):
        """Yardımcı JSON okuma fonksiyonu."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_data

    def _write_json(self, file_path, data):
        """Yardımcı JSON yazma fonksiyonu."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _get_artists_from_file(self):
        """Sanatçı listesini dosyadan okur."""
        return self._load_json(self.artists_file, {"artists": []}).get("artists", [])

    def fetch_and_save_music_data(self):
        """Sanatçıların şarkılarını çeker ve Links.json'a kaydeder."""
        print("Müzik verileri güncelleniyor...")
        artists = self._get_artists_from_file()
        if not artists:
            print("Sanatçı listesi boş. Lütfen Admin.py ile sanatçı ekleyin.")
            return

        for artist_name in artists:
            print(f"'{artist_name}' için şarkılar alınıyor...")
            try:
                # Sanatçıyı ara ve ID'sini al
                search_results = self.ytmusic.search(artist_name, filter="artists")
                if not search_results:
                    print(f"'{artist_name}' adında bir sanatçı bulunamadı.")
                    continue
                
                artist_id = search_results[0]['browseId']
                artist_details = self.ytmusic.get_artist(artist_id)
                
                # Sanatçı adını JSON için güvenli bir hale getir
                sanitized_artist_name = artist_details['name'].replace(" ", "_").lower()
                
                if sanitized_artist_name not in self.links_data:
                    self.links_data[sanitized_artist_name] = {}
                
                # Sanatçının tüm şarkılarını al
                if 'songs' in artist_details and artist_details['songs'] and 'results' in artist_details['songs']:
                    for song in artist_details['songs']['results']:
                        video_id = song['videoId']
                        song_title = song['title']
                        album_name = song['album']['name'] if song['album'] else "Single"
                        
                        # Şarkı adını JSON için güvenli hale getir
                        sanitized_song_title = song_title.replace(" ", "_").lower()

                        # Eğer şarkı zaten varsa tekrar işlem yapma
                        if sanitized_song_title in self.links_data[sanitized_artist_name]:
                           continue
                           
                        thumbnail_url = song['thumbnails'][-1]['url'] # En yüksek çözünürlüklü kapak
                        # Çözünürlüğü 544x544 ile sınırla
                        if 'w544-h544' not in thumbnail_url:
                           thumbnail_url = thumbnail_url.split('=')[0] + '=w544-h544-l90-rj'

                        self.links_data[sanitized_artist_name][sanitized_song_title] = {
                            "title": song_title,
                            "artist": artist_details['name'],
                            "album": album_name,
                            "youtube_url": f"https://music.youtube.com/watch?v={video_id}",
                            "cover_url": thumbnail_url,
                            "proxy_stream_url": f"/stream/{sanitized_artist_name}/{sanitized_song_title}"
                        }
                        print(f"  + Eklendi: {song_title}")
                else:
                    print(f"'{artist_name}' için şarkı bulunamadı.")

            except Exception as e:
                print(f"'{artist_name}' işlenirken bir hata oluştu: {e}")

        # Tüm veriyi dosyaya yaz
        self._write_json(self.links_file, self.links_data)
        print("Müzik verileri başarıyla güncellendi.")

def job():
    service = MusicDataService()
    service.fetch_and_save_music_data()

if __name__ == '__main__':
    # İlk çalıştırmada hemen verileri çek
    job()
    
    # Her 3 saatte bir verileri güncelle
    schedule.every(3).hours.do(job)
    print("Servis başlatıldı. Her 3 saatte bir veriler güncellenecek.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

