<!-- bottube_templates/watch.html -->
<!-- Add this block before the closing </body> tag -->

<!-- Keyboard Shortcut Overlay Indicator -->
<div id="kbd-overlay" style="
  display: none;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0,0,0,0.65);
  color: #fff;
  font-size: 3rem;
  padding: 20px 32px;
  border-radius: 12px;
  z-index: 9999;
  pointer-events: none;
  user-select: none;
  transition: opacity 0.15s ease;
"></div>

<script>
(function () {
  'use strict';

  /* ── Find the <video> element ── */
  var video = document.querySelector('video');
  if (!video) return;

  /* ── Overlay helper ── */
  var overlay = document.getElementById('kbd-overlay');
  var overlayTimer = null;

  function showOverlay(symbol) {
    overlay.textContent = symbol;
    overlay.style.display = 'block';
    overlay.style.opacity = '1';
    clearTimeout(overlayTimer);
    overlayTimer = setTimeout(function () {
      overlay.style.opacity = '0';
      setTimeout(function () {
        overlay.style.display = 'none';
      }, 160);
    }, 600);
  }

  /* ── Volume bar helper (optional on-screen feedback) ── */
  function volumeSymbol(v) {
    if (v === 0) return '🔇 0%';
    if (v < 0.34) return '🔈 ' + Math.round(v * 100) + '%';
    if (v < 0.67) return '🔉 ' + Math.round(v * 100) + '%';
    return '🔊 ' + Math.round(v * 100) + '%';
  }

  /* ── Seek helper ── */
  function seek(seconds) {
    video.currentTime = Math.max(0, Math.min(video.duration || 0, video.currentTime + seconds));
    showOverlay(seconds > 0 ? '⏩ +' + seconds + 's' : '⏪ ' + seconds + 's');
  }

  /* ── Fullscreen helper ── */
  function toggleFullscreen() {
    var el = video.closest('.video-container') || video;
    if (!document.fullscreenElement) {
      (el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen).call(el);
      showOverlay('⛶');
    } else {
      (document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen).call(document);
      showOverlay('⊡');
    }
  }

  /* ── Key handler ── */
  document.addEventListener('keydown', function (e) {
    /* Ignore shortcuts when user is typing in any input/textarea/contenteditable */
    var tag = (e.target || e.srcElement).tagName.toUpperCase();
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if ((e.target || e.srcElement).isContentEditable) return;

    /* Ignore if modifier keys are held (browser shortcuts) */
    if (e.ctrlKey || e.metaKey || e.altKey) return;

    switch (e.code || e.key) {

      /* Space / K → Play · Pause */
      case 'Space':
      case 'KeyK':
        e.preventDefault();
        if (video.paused) {
          video.play();
          showOverlay('▶');
        } else {
          video.pause();
          showOverlay('⏸');
        }
        break;

      /* J → Seek -10 s */
      case 'KeyJ':
        e.preventDefault();
        seek(-10);
        break;

      /* L → Seek +10 s */
      case 'KeyL':
        e.preventDefault();
        seek(10);
        break;

      /* Arrow Left → Seek -5 s */
      case 'ArrowLeft':
        e.preventDefault();
        seek(-5);
        break;

      /* Arrow Right → Seek +5 s */
      case 'ArrowRight':
        e.preventDefault();
        seek(5);
        break;

      /* Arrow Up → Volume +10 % */
      case 'ArrowUp':
        e.preventDefault();
        video.volume = Math.min(1, Math.round((video.volume + 0.1) * 10) / 10);
        video.muted = false;
        showOverlay(volumeSymbol(video.volume));
        break;

      /* Arrow Down → Volume -10 % */
      case 'ArrowDown':
        e.preventDefault();
        video.volume = Math.max(0, Math.round((video.volume - 0.1) * 10) / 10);
        showOverlay(volumeSymbol(video.volume));
        break;

      /* M → Mute toggle */
      case 'KeyM':
        e.preventDefault();
        video.muted = !video.muted;
        showOverlay(video.muted ? '🔇 Muted' : volumeSymbol(video.volume));
        break;

      /* F → Fullscreen toggle */
      case 'KeyF':
        e.preventDefault();
        toggleFullscreen();
        break;

      default:
        break;
    }
  });

}());
</script>