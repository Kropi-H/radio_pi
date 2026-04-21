import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional


class AudioService:
    def __init__(self) -> None:
        self._socket_path = "/tmp/audio-panel-mpv.sock"
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.RLock()

        self._current_station_id: Optional[int] = None
        self._current_station_name: Optional[str] = None
        self._current_station_group: Optional[str] = None
        self._current_url: Optional[str] = None
        self._volume: int = 70

        self._ensure_mpv_running()

    def _ensure_mpv_running(self) -> None:
        with self._lock:
            if self._process and self._process.poll() is None and self._socket_exists():
                return

            self._cleanup_socket_file()

            cmd = [
                "mpv",
                "--idle=yes",
                "--no-video",
                "--quiet",
                "--keep-open=no",
                f"--input-ipc-server={self._socket_path}",
                f"--volume={self._volume}",
            ]

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            self._wait_for_socket()

    def _socket_exists(self) -> bool:
        return Path(self._socket_path).exists()

    def _cleanup_socket_file(self) -> None:
        try:
            if os.path.exists(self._socket_path):
                os.remove(self._socket_path)
        except OSError:
            pass

    def _wait_for_socket(self, timeout: float = 3.0) -> None:
        start = time.time()
        while time.time() - start < timeout:
            if self._socket_exists():
                return
            time.sleep(0.05)
        raise RuntimeError("mpv IPC socket nebyl vytvořen.")

    def _send_command(self, command: list) -> dict:
        self._ensure_mpv_running()

        payload = json.dumps({"command": command}) + "\n"

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(2)
            client.connect(self._socket_path)
            client.sendall(payload.encode("utf-8"))

            data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in chunk:
                    break

        lines = data.decode("utf-8", errors="ignore").strip().splitlines()
        if not lines:
            return {}

        try:
            return json.loads(lines[-1])
        except json.JSONDecodeError:
            return {}

    def play(self, station_id: int, name: str, group_name: str, url: str) -> None:
        with self._lock:
            self._ensure_mpv_running()
            self._send_command(["loadfile", url, "replace"])
            self._send_command(["set_property", "pause", False])
            self._send_command(["set_property", "volume", self._volume])

            self._current_station_id = station_id
            self._current_station_name = name
            self._current_station_group = group_name
            self._current_url = url

    def stop(self) -> None:
        with self._lock:
            try:
                self._send_command(["stop"])
            except Exception:
                pass

            self._current_station_id = None
            self._current_station_name = None
            self._current_station_group = None
            self._current_url = None

    def pause(self) -> None:
        with self._lock:
            self._send_command(["set_property", "pause", True])

    def resume(self) -> None:
        with self._lock:
            self._send_command(["set_property", "pause", False])

    def toggle_pause(self) -> bool:
        with self._lock:
            paused = self.is_paused()
            self._send_command(["set_property", "pause", not paused])
            return True

    def set_volume(self, volume: int) -> None:
        with self._lock:
            self._volume = max(0, min(100, int(volume)))
            try:
                self._send_command(["set_property", "volume", self._volume])
            except Exception:
                pass

    def set_persisted_volume(self, volume: int) -> None:
        with self._lock:
            self._volume = max(0, min(100, int(volume)))
            try:
                self._send_command(["set_property", "volume", self._volume])
            except Exception:
                pass

    def get_property(self, name: str):
        try:
            response = self._send_command(["get_property", name])
            if response.get("error") == "success":
                return response.get("data")
        except Exception:
            return None
        return None

    def is_paused(self) -> bool:
        value = self.get_property("pause")
        return bool(value)

    def is_idle(self) -> bool:
        value = self.get_property("idle-active")
        return bool(value)

    def is_playing(self) -> bool:
        if self._current_url is None:
            return False
        return not self.is_idle()

    def status(self) -> dict:
        playing = self.is_playing()
        paused = self.is_paused() if self._current_url else False

        return {
            "is_playing": playing,
            "is_paused": paused,
            "station_id": self._current_station_id,
            "station_name": self._current_station_name,
            "station_group": self._current_station_group,
            "stream_url": self._current_url,
            "volume": self._volume,
            "pause_supported": True,
        }

    def shutdown(self) -> None:
        with self._lock:
            try:
                self._send_command(["quit"])
            except Exception:
                pass

            if self._process and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()

            self._process = None
            self._cleanup_socket_file()
