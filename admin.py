import json
import sys

ARTISTS_FILE = 'artists.json'

def load_artists():
    """Sanatçı listesini JSON dosyasından yükler."""
    try:
        with open(ARTISTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('artists', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_artists(artists):
    """Sanatçı listesini JSON dosyasına kaydeder."""
    with open(ARTISTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'artists': artists}, f, indent=4, ensure_ascii=False)

def add_artist(artist_name):
    """Listeye yeni bir sanatçı ekler."""
    artists = load_artists()
    if artist_name not in artists:
        artists.append(artist_name)
        save_artists(artists)
        print(f"Başarılı: '{artist_name}' sanatçısı eklendi.")
        print("Değişikliklerin etkili olması için Service.py'yi yeniden başlatın veya bir sonraki güncellemeyi bekleyin.")
    else:
        print(f"Uyarı: '{artist_name}' zaten listede mevcut.")

def remove_artist(artist_name):
    """Listeden bir sanatçıyı siler."""
    artists = load_artists()
    if artist_name in artists:
        artists.remove(artist_name)
        save_artists(artists)
        print(f"Başarılı: '{artist_name}' sanatçısı silindi.")
    else:
        print(f"Hata: '{artist_name}' listede bulunamadı.")

def list_artists():
    """Mevcut tüm sanatçıları listeler."""
    artists = load_artists()
    if not artists:
        print("Sanatçı listesi boş.")
    else:
        print("--- Takip Edilen Sanatçılar ---")
        for artist in artists:
            print(f"- {artist}")
        print("------------------------------")

def print_help():
    """Yardım menüsünü gösterir."""
    print("\n--- Yönetici Paneli Kullanımı ---")
    print("list                      : Mevcut sanatçıları listeler.")
    print("add \"Sanatçı Adı\"         : Yeni bir sanatçı ekler (tırnak işareti kullanın).")
    print("remove \"Sanatçı Adı\"      : Bir sanatçıyı siler (tırnak işareti kullanın).")
    print("help                      : Bu yardım menüsünü gösterir.")
    print("---------------------------------")
    print("\nÖrnek: python Admin.py add \"blok3\"")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'list':
        list_artists()
    elif command == 'add' and len(sys.argv) > 2:
        add_artist(sys.argv[2])
    elif command == 'remove' and len(sys.argv) > 2:
        remove_artist(sys.argv[2])
    elif command == 'help':
        print_help()
    else:
        print("Hatalı komut veya eksik parametre.")
        print_help()

