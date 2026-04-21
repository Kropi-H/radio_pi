# Postup nasazení

## 1. Instalace systémových balíků
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mpv chromium x11-xserver-utils
```

## 2. Nakopírování projektu
Rozbal balík do:
```bash
/home/honza/audio_panel
```

## 3. Python virtuální prostředí
```bash
cd /home/honza/audio_panel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Inicializace databáze
```bash
python scripts/init_db.py
```

## 5. Otestování aplikace ručně
```bash
python app.py
```
V browseru otevři:
```text
http://127.0.0.1:5000
```

## 6. Nastavení sudoers pro systémové akce
```bash
sudo visudo -f /etc/sudoers.d/audio-panel
```
Vlož:
```text
honza ALL=(ALL) NOPASSWD: /home/honza/audio_panel/scripts/close_ui.sh
honza ALL=(ALL) NOPASSWD: /home/honza/audio_panel/scripts/restart_ui.sh
honza ALL=(ALL) NOPASSWD: /home/honza/audio_panel/scripts/reboot_pi.sh
honza ALL=(ALL) NOPASSWD: /home/honza/audio_panel/scripts/shutdown_pi.sh
honza ALL=(ALL) NOPASSWD: /home/honza/audio_panel/scripts/display_off.sh
```

## 7. Instalace systemd jednotek
```bash
sudo cp systemd/audio-panel.service /etc/systemd/system/
sudo cp systemd/chromium-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable audio-panel.service
sudo systemctl enable chromium-kiosk.service
```

## 8. Spuštění služeb
```bash
sudo systemctl start audio-panel.service
sudo systemctl start chromium-kiosk.service
```

## 9. Kontrola stavu
```bash
sudo systemctl status audio-panel.service
sudo systemctl status chromium-kiosk.service
```

## 10. Poznámky
- Pokud používáš jiného uživatele než `honza`, uprav cesty v `systemd/*.service`, `scripts/display_off.sh` a v sudoers.
- Pokud Chromium není v systému jako `chromium`, uprav `scripts/restart_ui.sh` a `systemd/chromium-kiosk.service`.
- Tlačítko Spotify je zatím jen placeholder v hlavní obrazovce.
