async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || data.message || "Chyba požadavku.");
  }

  return data;
}

function updatePlayerBar(status) {
  const titleEl = document.getElementById("playerbar-title");
  const metaEl = document.getElementById("playerbar-meta");
  const volumeEl = document.getElementById("playerbar-volume");
  const pauseBtn = document.getElementById("playerbar-pause-btn");

  if (!titleEl || !metaEl || !volumeEl || !pauseBtn) return;

  if (status.is_playing && status.station_name) {
    titleEl.textContent = status.station_name;
    metaEl.textContent = status.is_paused
      ? `Pozastaveno • ${status.station_group || "Rádio"}`
      : `${status.station_group || "Rádio"}`;
  } else {
    titleEl.textContent = "Nic nehraje";
    metaEl.textContent = "Vyber stanici";
  }

  if (typeof status.volume === "number") {
    volumeEl.value = status.volume;
  }

  pauseBtn.textContent = status.is_paused ? "▶" : "⏯";
}

async function refreshPlayerStatus() {
  try {
    const data = await fetchJson("/api/player/status");
    updatePlayerBar(data);
  } catch (err) {
    console.error("Status error:", err);
  }
}

async function playStation(stationId) {
  try {
    const data = await fetchJson(`/api/player/play/${stationId}`, {
      method: "POST"
    });
    updatePlayerBar(data.status);
  } catch (err) {
    alert(err.message);
  }
}

async function stopPlayback() {
  try {
    const data = await fetchJson("/api/player/stop", {
      method: "POST"
    });
    updatePlayerBar(data.status);
  } catch (err) {
    alert(err.message);
  }
}

async function togglePause() {
  try {
    const data = await fetchJson("/api/player/pause-toggle", {
      method: "POST"
    });
    updatePlayerBar(data.status);
  } catch (err) {
    alert(err.message);
  }
}

async function setVolume(volume) {
  try {
    const data = await fetchJson("/api/player/volume", {
      method: "POST",
      body: JSON.stringify({ volume })
    });
    updatePlayerBar(data.status);
  } catch (err) {
    alert(err.message);
  }
}

async function closeUi() {
  try {
    await fetchJson("/api/system/close-ui", { method: "POST" });
  } catch (err) {
    alert("Nepodařilo se zavřít UI: " + err.message);
  }
}

async function restartUi() {
  try {
    await fetchJson("/api/system/restart-ui", { method: "POST" });
  } catch (err) {
    alert("Nepodařilo se restartovat UI: " + err.message);
  }
}

async function rebootPi() {
  if (!confirm("Opravdu restartovat Raspberry Pi?")) return;
  try {
    await fetchJson("/api/system/reboot", { method: "POST" });
  } catch (err) {
    alert("Nepodařilo se restartovat zařízení: " + err.message);
  }
}

async function shutdownPi() {
  if (!confirm("Opravdu vypnout Raspberry Pi?")) return;
  try {
    await fetchJson("/api/system/shutdown", { method: "POST" });
  } catch (err) {
    alert("Nepodařilo se vypnout zařízení: " + err.message);
  }
}

async function displayOff() {
  try {
    await fetchJson("/api/system/display-off", { method: "POST" });
  } catch (err) {
    alert("Nepodařilo se vypnout displej: " + err.message);
  }
}

function bindPlayerButtons() {
  document.querySelectorAll("[data-play-station-id]").forEach(btn => {
    btn.addEventListener("click", () => {
      playStation(btn.dataset.playStationId);
    });
  });

  const stopBtn = document.getElementById("playerbar-stop-btn");
  if (stopBtn) {
    stopBtn.addEventListener("click", stopPlayback);
  }

  const pauseBtn = document.getElementById("playerbar-pause-btn");
  if (pauseBtn) {
    pauseBtn.addEventListener("click", togglePause);
  }

  const volumeEl = document.getElementById("playerbar-volume");
  if (volumeEl) {
    let volumeTimer = null;
    volumeEl.addEventListener("input", () => {
      clearTimeout(volumeTimer);
      volumeTimer = setTimeout(() => {
        setVolume(Number(volumeEl.value));
      }, 120);
    });
  }

  const closeBtn = document.getElementById("close-ui-btn");
  if (closeBtn) {
    closeBtn.addEventListener("click", closeUi);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  bindPlayerButtons();
  refreshPlayerStatus();
  setInterval(refreshPlayerStatus, 2000);
});
