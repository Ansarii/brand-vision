import asyncio
import base64
import json
import os
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

async def capture_all_sections():
    ensure_chrome()
    os.makedirs("scratch/qc", exist_ok=True)

    # 1. Desktop full inspection (1440x900)
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
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1.0)

        sections = [
            ("desktop_01_hero", "#top"),
            ("desktop_02_inventory", "#inventory"),
            ("desktop_03_clients", "#clients"),
            ("desktop_04_live_footage", "#live-footage"),
            ("desktop_05_journey", "#journey"),
            ("desktop_06_locations", "#locations"),
            ("desktop_07_day_night", "#day-night"),
            ("desktop_08_preview", "#preview"),
            ("desktop_09_about", "#about"),
            ("desktop_10_contact", "#contact"),
            ("desktop_11_footer", ".main-footer")
        ]

        for name, sel in sections:
            await call("Runtime.evaluate", {
                "expression": f"document.querySelector('{sel}')?.scrollIntoView({{behavior: 'instant', block: 'start'}});"
            })
            await asyncio.sleep(0.5)
            shot = await call("Page.captureScreenshot", {"format": "png"})
            with open(f"scratch/qc/{name}.png", "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"Captured scratch/qc/{name}.png")

        # Open drawer on desktop
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.coral-menu-toggle')?.click();"
        })
        await asyncio.sleep(0.6)
        shot_drawer = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/desktop_12_drawer.png", "wb") as f:
            f.write(base64.b64decode(shot_drawer["data"]))
        print("Captured scratch/qc/desktop_12_drawer.png")

        # Close drawer
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.coral-drawer-close')?.click();"
        })
        await asyncio.sleep(0.4)

        # Open doc modal
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('button[data-doc-target=\"terms\"]')?.click();"
        })
        await asyncio.sleep(0.6)
        shot_modal = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/desktop_13_doc_modal.png", "wb") as f:
            f.write(base64.b64decode(shot_modal["data"]))
        print("Captured scratch/qc/desktop_13_doc_modal.png")

        # Close doc modal
        await call("Runtime.evaluate", {
            "expression": "document.getElementById('doc-modal-close')?.click();"
        })
        await asyncio.sleep(0.4)

        # 2. Mobile phone inspection (390x844)
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)

        mobile_sections = [
            ("mobile_01_hero", "#top"),
            ("mobile_02_subnav", ".mv-subnav"),
            ("mobile_03_inventory", "#inventory"),
            ("mobile_04_clients", "#clients"),
            ("mobile_05_live_footage", "#live-footage"),
            ("mobile_06_journey", "#journey"),
            ("mobile_07_locations", "#locations"),
            ("mobile_08_day_night", "#day-night"),
            ("mobile_09_preview", "#preview"),
            ("mobile_10_about", "#about"),
            ("mobile_11_contact", "#contact"),
            ("mobile_12_footer", ".footer-bottom-bar")
        ]

        for name, sel in mobile_sections:
            await call("Runtime.evaluate", {
                "expression": f"document.querySelector('{sel}')?.scrollIntoView({{behavior: 'instant', block: 'start'}});"
            })
            await asyncio.sleep(0.5)
            shot = await call("Page.captureScreenshot", {"format": "png"})
            with open(f"scratch/qc/{name}.png", "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"Captured scratch/qc/{name}.png")

        # Open drawer on mobile
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.coral-menu-toggle')?.click();"
        })
        await asyncio.sleep(0.6)
        shot_mob_drawer = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/mobile_13_drawer.png", "wb") as f:
            f.write(base64.b64decode(shot_mob_drawer["data"]))
        print("Captured scratch/qc/mobile_13_drawer.png")

if __name__ == '__main__':
    asyncio.run(capture_all_sections())
