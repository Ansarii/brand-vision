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

async def capture_verification():
    ensure_chrome()

    # 1. Test directly on http://localhost:8765/v2/ at mobile viewport 390x844
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
        await call("DOM.enable")
        
        # Set mobile viewport 390 x 844
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(1.5)

        # Scroll to Day/Night section
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('#day-night').scrollIntoView({behavior: 'instant'});"
        })
        await asyncio.sleep(1.0)

        # Capture Day View
        shot_day = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/verified_mweb_day_view.png", "wb") as f:
            f.write(base64.b64decode(shot_day["data"]))
        print("Captured scratch/verified_mweb_day_view.png")

        # Click Night View tab/toggle
        await call("Runtime.evaluate", {
            "expression": """
                const nightBtn = document.querySelector('[data-view=\"night\"], .toggle-night, button:has(.night), .day-night-toggle button:last-child') || 
                                 Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Night'));
                if (nightBtn) nightBtn.click();
            """
        })
        await asyncio.sleep(1.0)

        # Capture Night View
        shot_night = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/verified_mweb_night_view.png", "wb") as f:
            f.write(base64.b64decode(shot_night["data"]))
        print("Captured scratch/verified_mweb_night_view.png")

        # Scroll to footer
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.footer-bottom-bar').scrollIntoView({behavior: 'instant', block: 'center'});"
        })
        await asyncio.sleep(1.0)

        # Capture footer on 390px
        shot_footer_390 = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/verified_mweb_footer_390.png", "wb") as f:
            f.write(base64.b64decode(shot_footer_390["data"]))
        print("Captured scratch/verified_mweb_footer_390.png")

        # Now test 360px small phone viewport
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 360,
            "height": 740,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)
        shot_footer_360 = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/verified_mweb_footer_360.png", "wb") as f:
            f.write(base64.b64decode(shot_footer_360["data"]))
        print("Captured scratch/verified_mweb_footer_360.png")

    # 2. Test in phone.html emulator
    req2 = urllib.request.Request("http://127.0.0.1:9222/json/new?http://localhost:8765/.claude/phone.html", method="PUT")
    with urllib.request.urlopen(req2) as resp2:
        page_info2 = json.loads(resp2.read().decode())
    ws_url2 = page_info2["webSocketDebuggerUrl"]

    async with websockets.connect(ws_url2, max_size=25*1024*1024) as ws2:
        msg_id2 = 0
        async def call2(method, params=None):
            nonlocal msg_id2
            msg_id2 += 1
            await ws2.send(json.dumps({"id": msg_id2, "method": method, "params": params or {}}))
            while True:
                res = json.loads(await ws2.recv())
                if res.get("id") == msg_id2:
                    return res.get("result", {})

        await call2("Page.enable")
        await call2("Emulation.setDeviceMetricsOverride", {
            "width": 1280,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1.5)

        # Capture phone.html
        shot_phone_html = await call2("Page.captureScreenshot", {"format": "png"})
        with open("scratch/verified_phone_html_emulator.png", "wb") as f:
            f.write(base64.b64decode(shot_phone_html["data"]))
        print("Captured scratch/verified_phone_html_emulator.png")

if __name__ == '__main__':
    asyncio.run(capture_verification())
