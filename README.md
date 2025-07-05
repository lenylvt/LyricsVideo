
██╗  ██╗   ██╗██████╗ ██╗ ██████╗███████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗ 
██║  ╚██╗ ██╔╝██╔══██╗██║██╔════╝██╔════╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██║   ╚████╔╝ ██████╔╝██║██║     ███████╗    ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
██║    ╚██╔╝  ██╔══██╗██║██║     ╚════██║    ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
███████╗██║   ██║  ██║██║╚██████╗███████║     ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝      ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                                     

# 🎤 Lyrics Video Maker – Version « Chabat & Cie »

Bienvenue dans le royaume un peu fou de **Lyrics Video Maker** : un script Python qui prend une chanson de Deezer au hasard, en extrait les paroles, crée des images stylées, monte une vidéo verticale et la dépose comme un galet sur TikTok. Auto‑piloté, sans stress !

---

## 🚀 Fonctionnalités

- 🎲 **Choix aléatoire** d’un morceau dans ta playlist Deezer  
- 🖼 **Cover d’album** téléchargée automatiquement  
- 🎶 **Paroles synchronisées** via MusicXMatch / LRCLib  
- 📱 **Images stylées (format vertical 9:16)**, pensées pour smartphone  
- 🎥 **Montage vidéo dynamique** calé au rythme (BPM), avec effets cool  
- 🔊 **Audio extrait de YouTube**, automatiquement récupéré  
- 📤 **Publication sur TikTok en brouillon** (faut bien relire avant de partager…)

---

## 🛠 Prérequis

- **Python ≥ 3.8**  
- **ffmpeg** installé (support du montage via moviepy)  
- Un compte **TikTok API‑ready** (sandbox suffisant)

---

## 📥 Installation rapide

```bash
git clone https://github.com/votre-utilisateur/lyrics-video-maker.git
cd lyrics-video-maker
pip install -r requirements.txt

---

⚙️ Configuration (.env)
	1.	Renomme .env.exemple → .env
	2.	Renseigne les infos suivantes :

🕺 TikTok
	•	Crée une app via le portail dev TikTok
	•	Active Login Kit + Content Posting API
	•	Remplis dans .env :
	•	TIKTOK_CLIENT_KEY
	•	TIKTOK_CLIENT_SECRET
	•	TIKTOK_REDIRECT_URI
	•	TIKTOK_TOKEN
(Lance le script localement, clique sur le lien généré, récupère le code=xxx dans l’URL et colle-le dans le terminal pour générer tiktok_tokens.txt. Copie son contenu dans .env)

🎧 Deezer
	•	PLAYLIST_ID → extrait l’ID dans l’URL :
https://www.deezer.com/playlist/1234567890

🎼 YouTube
	•	COOKIES_TXT → exporte tes cookies YouTube (connecté) via extension navigateur, colle-les ici.
👉 Extension recommandée : Get cookies.txt

---

▶️ Utilisation

python -m src.main.py

Le script va :
	1.	🎵 Choisir une chanson
	2.	🖼 Télécharger la cover
	3.	📝 Récupérer les paroles synchronisées
	4.	🎨 Générer les images et monter la vidéo
	5.	📤 Publier en brouillon sur TikTok

---

⏰ Automatisation avec GitHub Actions

Tu veux envoyer ça tous les matins sans bouger le petit doigt ?
	•	Forke le repo
	•	Mets chaque variable .env dans Settings → Secrets
	•	Ajuste le cron dans .github/workflows/python-app.yml (ex. cron: '30 6 * * *' → 6h30 quotidien)
	•	Et ça tourne tout seul 🚀

---

🧠 Crédits & inspirations
	•	Développé par moi (auto‑proclamé codeur pro)
	•	Utilise Deezer, LRCLib/MusicXMatch, TikTok API
	•	Basé sur le reverse‑engineer de MusicMatch par Strvm
	•	Fork initial de Pranavgnn