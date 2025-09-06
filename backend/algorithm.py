import json
import os
import random

class RecommendationEngine:
    def __init__(self, users_dir='Users', popular_file='Popular.json', tab50_file='Tab50.json'):
        self.users_dir = users_dir
        self.popular_songs = self._load_json(popular_file, {"songs": []}).get("songs", [])
        self.top_50_songs = self._load_json(tab50_file, {"songs": []}).get("songs", [])

    def _load_json(self, file_path, default_data):
        """Yardımcı JSON okuma fonksiyonu."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_data

    def get_user_history(self, username):
        """Kullanıcının dinleme geçmişini alır."""
        history_file = os.path.join(self.users_dir, username, f'{username}.json')
        return self._load_json(history_file, {"history": []}).get("history", [])

    def get_user_likes(self, username):
        """Kullanıcının beğendiği şarkıları alır."""
        likes_file = os.path.join(self.users_dir, username, f'{username}likedandplaylist.json')
        return self._load_json(likes_file, {"liked": []}).get("liked", [])

    def get_recommendations(self, username, num_recommendations=20):
        """
        Kullanıcı için şarkı önerileri oluşturur.
        Bu fonksiyon daha gelişmiş algoritmalarla (içerik tabanlı, işbirlikçi filtreleme vb.) değiştirilebilir.
        Mevcut sürüm, basit bir mantık kullanır:
        1. Beğenilen şarkıların sanatçılarından başka şarkılar önerir.
        2. Dinleme geçmişindeki popüler sanatçılardan şarkılar önerir.
        3. Genel popüler listelerden şarkılar ekler.
        """
        
        history = self.get_user_history(username)
        likes = self.get_user_likes(username)
        
        # Basitçe popüler şarkılardan bir seçki döndürelim (geliştirilecek)
        recommendations = []
        
        # Kullanıcının beğendiği ve dinlediği şarkıları öneri listesine eklememek için bir set oluşturalım
        seen_songs = set(item['id'] for item in history) | set(like['id'] for like in likes)

        # Popüler ve Top 50 listelerini birleştirip karıştıralım
        candidate_pool = self.popular_songs + self.top_50_songs
        random.shuffle(candidate_pool)

        for song in candidate_pool:
            if len(recommendations) >= num_recommendations:
                break
            if song['id'] not in seen_songs:
                recommendations.append(song)
                seen_songs.add(song['id']) # Tekrar eklenmemesi için
        
        return recommendations

if __name__ == '__main__':
    # Örnek kullanım
    engine = RecommendationEngine()
    
    # 'User1' adında örnek bir kullanıcı için öneri alalım.
    # Bu kullanıcının JSON dosyalarının 'Users/User1/' altında olması gerekir.
    # Önce örnek dosyaları oluşturduğunuzdan emin olun.
    
    # Örnek kullanıcı dosyası yoksa oluştur:
    if not os.path.exists('Users/User1'):
        os.makedirs('Users/User1')
        with open('Users/User1/User1.json', 'w') as f:
            json.dump({"history": []}, f)
        with open('Users/User1/User1likedandplaylist.json', 'w') as f:
            json.dump({"liked": [], "playlists": []}, f)
            
    recommendations = engine.get_recommendations('User1')
    
    print("User1 için öneriler:")
    for i, rec in enumerate(recommendations):
        print(f"{i+1}. {rec['title']} - {rec['artist']}")

                   
