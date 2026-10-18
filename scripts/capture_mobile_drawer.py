import asyncio
import base64
import json
import time
import urllib.request
import websockets

def ensure_chrome():
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version")
    except Exception:
        import subprocess
        subprocess.Popen([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless=new",
            "--remote-debugging-port=9222",
            "--user-data-dir=scratch/chrome_user_data"
        ])
        for _ in range(20):
            time.sleep(0.3)
            try:
                urllib.request.urlopen("http://127.0.0.1:9222/json/version")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def capture_mobile_drawer():
    ensure_chrome()
    req = urllib.request.Request("http://127.0.0.1:9222/json/new?http://localhost:8765/v2/", method="PUT")
    with urllib.request.urlopen(req) as resp:
        page_info = json.loads(resp.read().decode())
    ws_url = page_info["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        msg_id = 0
        async def call(method, params=None):
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws.recv())
                if res.get("id") == msg_id:
                    return res.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)

        # Click menu button
        await call("Runtime.evaluate", {
            "expression": "const btn = document.getElementById('coral-menu-toggle'); if (btn) btn.click(); else document.getElementById('coral-drawer-overlay').classList.add('active');"
        })
        await asyncio.sleep(0.6)

        # Scroll drawer container down to bottom to see policy pills
        await call("Runtime.evaluate", {
            "expression": "const d = document.querySelector('.coral-drawer-container'); if (d) d.scrollTop = d.scrollHeight;"
        })
        await asyncio.sleep(0.4)

        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/mobile_menu_drawer_pills.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/mobile_menu_drawer_pills.png")

if __name__ == "__main__":
    asyncio.run(capture_mobile_drawer())
