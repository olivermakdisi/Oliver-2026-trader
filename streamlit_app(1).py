import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Forex Signals", layout="centered")

st.markdown(
    "<style>#MainMenu{visibility:hidden}footer{visibility:hidden}"
    "header{visibility:hidden}.block-container{padding:0}</style>",
    unsafe_allow_html=True,
)

HTML = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:sans-serif;max-width:480px;margin:auto;padding:16px;background:#111;color:#fff}
h2{text-align:center}
.row{display:flex;justify-content:space-between;align-items:center;padding:14px;margin:8px 0;border-radius:10px;background:#333;font-size:18px}
.UP{background:#1e7d32}
.DOWN{background:#c62828}
small{color:#aaa;display:block;text-align:center;margin:8px 0}
</style>
</head>
<body>
<h2>إشارات الفوركس</h2>
<small id="upd">جاري التحميل...</small>
<div id="rows"></div>
<small>Not financial advice. Trading involves risk of loss.</small>

<script>
const PAIRS = ["EURUSDT", "GBPUSDT", "AUDUSDT", "TRYUSDT", "BRLUSDT"];
const KL = "https://api.binance.com/api/v3/klines?interval=1m&limit=60&symbol=";
const last = {};

function ema(v, p) {
  const k = 2 / (p + 1);
  let e = v[0];
  for (let i = 1; i < v.length; i++) e = v[i] * k + e * (1 - k);
  return e;
}

function rsi(v, p = 14) {
  let g = 0, l = 0;
  const a = v.slice(-(p + 1));
  for (let i = 1; i < a.length; i++) {
    const d = a[i] - a[i - 1];
    if (d > 0) g += d; else l -= d;
  }
  if (l === 0) return 100;
  return 100 - 100 / (1 + (g / p) / (l / p));
}

async function analyze(sym) {
  const r = await fetch(KL + sym);
  const kl = await r.json();
  const closes = kl.slice(0, -1).map(k => parseFloat(k[4]));
  const e9 = ema(closes, 9), e21 = ema(closes, 21), rs = rsi(closes);
  const px = closes[closes.length - 1];
  if (e9 > e21 && rs > 50 && rs < 70) return { dir: "UP", rsi: rs, px };
  if (e9 < e21 && rs > 30 && rs < 50) return { dir: "DOWN", rsi: rs, px };
  return { dir: "WAIT", rsi: rs, px };
}

function notify(sym, dir, px) {
  const txt = sym + " " + (dir === "UP" ? "⬆ طالع" : "⬇ نازل") + " @ " + px;
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("Forex Signal", { body: txt });
  }
  if (navigator.vibrate) navigator.vibrate(200);
}

async function refresh() {
  const rows = document.getElementById("rows");
  let html = "";
  for (const sym of PAIRS) {
    try {
      const s = await analyze(sym);
      if (s.dir !== "WAIT" && last[sym] !== undefined && last[sym] !== s.dir) {
        notify(sym, s.dir, s.px);
      }
      last[sym] = s.dir;
      const label = s.dir === "UP" ? "⬆ طالع" : s.dir === "DOWN" ? "⬇ نازل" : "— انتظر";
      html += '<div class="row ' + s.dir + '"><b>' + sym + "</b><span>" + label +
        " | " + s.px + "</span></div>";
    } catch (e) {
      html += '<div class="row"><b>' + sym + "</b><span>خطأ</span></div>";
    }
  }
  rows.innerHTML = html;
  document.getElementById("upd").textContent =
    "آخر تحديث: " + new Date().toLocaleTimeString();
}

document.addEventListener("click", () => {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }
}, { once: true });

refresh();
setInterval(refresh, 20000);
</script>
</body>
</html>
"""

components.html(HTML, height=700, scrolling=True)
