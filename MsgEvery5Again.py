# MsgEvery5 - escribe una frase cada X minutos en la ventana activa.
# Uso:  python MsgEvery5.py   -> se abre el panel en tu navegador, pulsa Run.
import sys, json, time, secrets, threading, subprocess, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def need(mod, pkg):
    try:
        __import__(mod)
    except ImportError:
        print("Instalando", pkg, "...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])


need("pyautogui", "pyautogui")
need("pyperclip", "pyperclip")
import pyautogui, pyperclip

PORT = 8765
TOKEN = secrets.token_hex(16)
CUENTA = 10  # segundos para que pinches en el chat tras pulsar Run
pyautogui.FAILSAFE = True  # ratón a la esquina superior izquierda = abortar
st = {"running": False, "phase": "idle", "left": 0, "sent": 0, "last": ""}
stop = threading.Event()


def pegar(texto, enter):
    pyperclip.copy(texto)
    pyautogui.hotkey("command" if sys.platform == "darwin" else "ctrl", "v")
    time.sleep(0.3)
    if enter:
        pyautogui.press("enter")


def esperar(n):
    for i in range(int(n), 0, -1):
        if stop.is_set():
            return False
        st["left"] = i
        time.sleep(1)
    return not stop.is_set()


def worker(frase, seg, enter):
    st.update(running=True, phase="countdown", sent=0, last="")
    try:
        if esperar(CUENTA):
            while True:
                st["phase"] = "sending"
                pegar(frase, enter)
                st["sent"] += 1
                st["last"] = time.strftime("%H:%M:%S")
                st["phase"] = "waiting"
                if not esperar(seg):
                    break
    except Exception as e:
        st["last"] = "Error: " + str(e)
    st.update(running=False, phase="idle", left=0)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def origen_ok(self):
        # solo acepta peticiones de esta misma pagina local
        propios = ("127.0.0.1:%d" % PORT, "localhost:%d" % PORT)
        if self.headers.get("Host", "") not in propios:
            return False
        o = self.headers.get("Origin")
        return o is None or o.replace("http://", "") in propios

    def responder(self, code, body, ctype="application/json"):
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if not self.origen_ok():
            return self.responder(403, "{}")
        if self.path == "/":
            self.responder(200, PAGE.replace("__TOKEN__", TOKEN), "text/html; charset=utf-8")
        elif self.path == "/status":
            self.responder(200, json.dumps(st))
        else:
            self.responder(404, "{}")

    def do_POST(self):
        if not self.origen_ok() or self.headers.get("X-Token") != TOKEN:
            return self.responder(403, "{}")
        n = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/run" and not st["running"]:
            stop.clear()
            st["running"] = True
            threading.Thread(target=worker, daemon=True,
                             args=(str(d["frase"]), max(1, int(d["seg"])), bool(d["enter"]))).start()
        elif self.path == "/stop":
            stop.set()
        self.responder(200, json.dumps(st))


PAGE = '<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>MsgEvery5</title><style>\n:root{--bg:#000802;--card:rgba(0,16,6,.82);--ink:#c8ffd6;--mute:#5fbf7a;--line:#0b5d22;--acc:#00ff41;--accink:#001a07;--code:#000a03;--codeink:#7dff9f;color-scheme:dark;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}\n*{box-sizing:border-box}\nhtml,body{background:var(--bg)}\nbody{margin:0;color:var(--ink);font:15px/1.55 ui-monospace,"Cascadia Code",Menlo,Consolas,monospace;min-height:100vh;position:relative}\n#rain{position:fixed;inset:0;z-index:0;opacity:.35;pointer-events:none}\nbody::before{content:"";position:fixed;inset:0;z-index:1;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 1px,transparent 1px 3px)}\nbody::after{content:"";position:fixed;inset:0;z-index:1;pointer-events:none;background:radial-gradient(ellipse at center,transparent 45%,rgba(0,0,0,.75))}\nmain{position:relative;z-index:2;max-width:780px;margin:0 auto;padding:34px 18px 60px}\n.jp{color:var(--mute);letter-spacing:.35em;font-size:12px;text-transform:uppercase}\nh1{position:relative;font-size:clamp(40px,10vw,68px);margin:6px 0 4px;letter-spacing:.04em;color:var(--acc);text-shadow:0 0 8px var(--acc),0 0 28px rgba(0,255,65,.55);font-weight:800;line-height:1.05}\nh1::before,h1::after{content:attr(data-t);position:absolute;left:0;top:0;width:100%;overflow:hidden}\nh1::before{color:#00ffd5;transform:translate(2px,0);clip-path:inset(0 0 62% 0);animation:gl 3.2s infinite steps(1);text-shadow:none;opacity:.7}\nh1::after{color:#b6ff00;transform:translate(-2px,0);clip-path:inset(60% 0 0 0);animation:gl 2.6s infinite steps(1) reverse;text-shadow:none;opacity:.6}\n@keyframes gl{0%,90%{transform:translate(0)}92%{transform:translate(3px,-1px)}95%{transform:translate(-3px,1px)}100%{transform:translate(0)}}\n@media (prefers-reduced-motion:reduce){h1::before,h1::after{animation:none}}\n.sub{margin:0 0 26px;font-size:17px;color:var(--ink)}\n.sub::before{content:"> ";color:var(--acc)}\n.sub::after{content:"_";color:var(--acc);animation:bl 1s infinite steps(1)}\n@keyframes bl{50%{opacity:0}}\n.card{position:relative;background:var(--card);border:1px solid var(--line);padding:20px;margin-bottom:20px;backdrop-filter:blur(3px);box-shadow:0 0 18px rgba(0,255,65,.12),inset 0 0 22px rgba(0,255,65,.05);clip-path:polygon(0 0,calc(100% - 18px) 0,100% 18px,100% 100%,18px 100%,0 calc(100% - 18px))}\n.card::before{content:"";position:absolute;left:0;top:0;width:4px;height:100%;background:var(--acc);box-shadow:0 0 10px var(--acc)}\nlabel{display:block;font-weight:700;font-size:13px;margin-bottom:6px;color:var(--acc);text-transform:uppercase;letter-spacing:.12em}\nlabel small{color:var(--mute);font-weight:400;letter-spacing:.2em;margin-left:6px}\ntextarea,input[type=number]{width:100%;padding:10px 12px;border:1px solid var(--line);background:#000d04;color:var(--ink);font:inherit;outline:none;border-radius:0}\ntextarea:focus,input[type=number]:focus{border-color:var(--acc);box-shadow:0 0 10px rgba(0,255,65,.45)}\ntextarea{resize:vertical;min-height:72px}\n.row{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-end;margin-top:16px}\n.row>div{flex:1;min-width:150px}\n.chk{display:flex;gap:10px;align-items:center;margin:0;color:var(--ink);text-transform:none;letter-spacing:0;font-weight:500;cursor:pointer}\n.chk input{accent-color:var(--acc);width:18px;height:18px}\n.tabs{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}\n.tab{padding:8px 16px;border:1px solid var(--line);background:transparent;color:var(--mute);font:inherit;font-size:13px;text-transform:uppercase;letter-spacing:.1em;cursor:pointer;clip-path:polygon(10px 0,100% 0,calc(100% - 10px) 100%,0 100%)}\n.tab:hover{color:var(--acc)}\n.tab[aria-selected=true]{background:var(--acc);color:var(--accink);font-weight:800;box-shadow:0 0 14px var(--acc)}\npre{background:var(--code);color:var(--codeink);padding:14px;border:1px solid var(--line);overflow-x:auto;max-height:260px;font:12px/1.5 ui-monospace,Menlo,Consolas,monospace;margin:0 0 14px;white-space:pre-wrap;word-break:break-all}\n.btns{display:flex;gap:12px;flex-wrap:wrap}\n.btn{padding:11px 20px;border:1px solid var(--acc);background:transparent;color:var(--acc);font:inherit;font-weight:800;text-transform:uppercase;letter-spacing:.12em;cursor:pointer;text-decoration:none;display:inline-block;clip-path:polygon(0 0,calc(100% - 12px) 0,100% 12px,100% 100%,12px 100%,0 calc(100% - 12px));transition:.15s}\n.btn:hover{background:rgba(0,255,65,.14);box-shadow:0 0 16px rgba(0,255,65,.6)}\n.btn.main{background:var(--acc);color:var(--accink)}\n.btn.main:hover{background:#6bff8d}\n.btn.main::before{content:"▶ "}\nol{margin:0;padding-left:22px}ol li{margin:7px 0}\n.note{font-size:13px;color:var(--mute);margin-top:12px}\nkbd{background:#001a08;border:1px solid var(--line);color:var(--acc);padding:1px 6px;font-size:12.5px}\n.foot{text-align:center;color:var(--mute);font-size:11px;letter-spacing:.4em;margin-top:8px}\n\n.btn[disabled]{opacity:.35;pointer-events:none}\n#stop::before{content:"■ "}\n.state{margin-top:16px;padding:12px 14px;border:1px dashed var(--line);color:var(--mute);min-height:48px}\n.state b{color:var(--acc)}\n.state.on{border-color:var(--acc);color:var(--ink);box-shadow:0 0 14px rgba(0,255,65,.25)}\n</style></head>\n<body>\n<canvas id="rain" aria-hidden="true"></canvas>\n<main>\n  <div class="jp">メッセージ送信機 // AUTO-SEND SYSTEM</div>\n  <h1 data-t="MsgEvery5">MsgEvery5</h1>\n  <p class="sub">Drop your Message every Five</p>\n  <section class="card">\n    <label for="frase">frase =<small>言葉</small></label>\n    <textarea id="frase">ok, sigue</textarea>\n    <div class="row">\n      <div><label for="min">tiempo = (minutos)<small>時間</small></label><input id="min" type="number" min="0.1" step="0.5" value="5"></div>\n      <div><label class="chk"><input id="enter" type="checkbox" checked> Enviar (Enter) tras escribir</label></div>\n    </div>\n  </section>\n  <section class="card">\n    <div class="btns"><button class="btn main" id="run">Run</button><button class="btn" id="stop" disabled>Stop</button></div>\n    <div class="state" id="state">En espera. Pulsa Run, y en la cuenta atrás cambia a la ventana del chat y haz clic en su cuadro de texto.</div>\n  </section>\n  <div class="foot">送 信 // SYSTEM ONLINE</div>\n</main>\n<script>\nconst $ = id => document.getElementById(id), T = "__TOKEN__";\nasync function api(p, b){ const r = await fetch(p, {method:"POST", headers:{"X-Token":T,"Content-Type":"application/json"}, body:JSON.stringify(b||{})}); return r.json(); }\nfunction draw(s){\n  const el = $("state");\n  $("run").disabled = s.running; $("stop").disabled = !s.running;\n  el.classList.toggle("on", s.running);\n  if (s.phase === "countdown") el.innerHTML = "Cambia ya a la ventana del chat y haz clic en su cuadro de texto. Empieza en <b>" + s.left + "s</b>";\n  else if (s.running) el.innerHTML = "<b>ACTIVO</b> · enviados: " + s.sent + " · último: " + (s.last || "-") + " · próximo en " + s.left + "s";\n  else el.textContent = (s.last && s.last.startsWith("Error") ? s.last : "En espera." + (s.sent ? " Enviados en la última sesión: " + s.sent + "." : ""));\n}\n$("run").onclick = () => api("/run", {frase:$("frase").value, seg:Math.max(1, Math.round((parseFloat($("min").value) || 5) * 60)), enter:$("enter").checked}).then(draw);\n$("stop").onclick = () => api("/stop").then(draw);\nsetInterval(() => fetch("/status").then(r => r.json()).then(draw).catch(() => { $("state").textContent = "Servidor desconectado: vuelve a ejecutar MsgEvery5.py"; }), 1000);\n// lluvia katakana\n(function(){\n  const c = $("rain"), x = c.getContext("2d");\n  const chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789";\n  let cols, drops, fs = 16;\n  function size(){ c.width = innerWidth; c.height = innerHeight; cols = Math.ceil(c.width / fs); drops = Array.from({length: cols}, () => Math.random() * -50); }\n  size(); addEventListener("resize", size);\n  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;\n  setInterval(() => {\n    x.fillStyle = "rgba(0,8,2,.12)"; x.fillRect(0, 0, c.width, c.height);\n    x.fillStyle = "#00ff41"; x.font = fs + "px monospace";\n    drops.forEach((y, i) => {\n      x.fillText(chars[Math.floor(Math.random() * chars.length)], i * fs, y * fs);\n      if (y * fs > c.height && Math.random() > .975) drops[i] = 0; else drops[i] = y + 1;\n    });\n  }, 60);\n})();\n\n</script></body></html>'


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    url = "http://127.0.0.1:%d/" % PORT
    print("MsgEvery5 en", url, "  (Ctrl+C para cerrar)")
    webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        stop.set()
        print("Cerrado.")
