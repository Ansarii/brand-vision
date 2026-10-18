import asyncio
import base64
import json
import subprocess
import time
import urllib.request
import websockets

def ensure_chrome():
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version")
        print("Chrome already running on 9222")
    except Exception:
        print("Starting Chrome on 9222...")
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
                print("Chrome started successfully")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def capture_candeur_and_footer():
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
        
        # 390 mobile viewport
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(1.0)

        # 1. Scroll to .night-viewer-stage
        await call("Runtime.evaluate", {
            "expression": """
                const stage = document.querySelector('.night-viewer-stage');
                if (stage) stage.scrollIntoView({behavior: 'instant', block: 'center'});
            """
        })
        await asyncio.sleep(1.0)

        # Make sure Day View is active
        await call("Runtime.evaluate", {
            "expression": """
                const dayBtn = document.getElementById('btn-view-day');
                if (dayBtn) dayBtn.click();
            """
        })
        await asyncio.sleep(0.8)

        # Capture Day View in-situ
        shot_day = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/insitu_day_view.png", "wb") as f:
            f.write(base64.b64decode(shot_day["data"]))
        print("Captured scratch/insitu_day_view.png")

        # Click Night View button
        await call("Runtime.evaluate", {
            "expression": """
                const nightBtn = document.getElementById('btn-view-night');
                if (nightBtn) nightBtn.click();
            """
        })
        await asyncio.sleep(0.8)

        # Capture Night View in-situ
        shot_night = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/insitu_night_view.png", "wb") as f:
            f.write(base64.b64decode(shot_night["data"]))
        print("Captured scratch/insitu_night_view.png")

        # Scroll to absolute bottom for 390px
        await call("Runtime.evaluate", {
            "expression": "window.scrollTo(0, document.body.scrollHeight);"
        })
        await asyncio.sleep(0.8)
        shot_foot_390 = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/insitu_footer_390.png", "wb") as f:
            f.write(base64.b64decode(shot_foot_390["data"]))
        print("Captured scratch/insitu_footer_390.png")

        # 360 mobile viewport
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 360,
            "height": 740,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)
        await call("Runtime.evaluate", {
            "expression": "window.scrollTo(0, document.body.scrollHeight);"
        })
        await asyncio.sleep(0.8)
        shot_foot_360 = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/insitu_footer_360.png", "wb") as f:
            f.write(base64.b64decode(shot_foot_360["data"]))
        print("Captured scratch/insitu_footer_360.png")

if __name__ == '__main__':
    asyncio.run(capture_candeur_and_footer())
