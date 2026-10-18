#!/usr/bin/env python3
"""
Targeted test script to capture the Brand Vision AI chat workflow response
and verify the typographic and visual alignment of the step cards.
"""

import asyncio
import base64
import json
import os
import time
import urllib.request
import websockets

def ensure_chrome():
    try:
        urllib.request.urlopen("http://127.0.0.1:9222/json/version")
        print("Chrome already running on 9222")
    except Exception:
        print("Starting Chrome on 9222...")
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
                print("Chrome started successfully")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def capture_workflow():
    ensure_chrome()
    os.makedirs("scratch/qc", exist_ok=True)

    # Use a fresh tab
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

        # Desktop Viewport first
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1.0)

        # Clear sessionStorage and open chat
        await call("Runtime.evaluate", {
            "expression": """(() => {
                sessionStorage.clear();
                const launcher = document.getElementById('bv-chat-launcher');
                if (launcher) launcher.click();
            })()"""
        })
        await asyncio.sleep(0.6)

        # Click starter card 3 ("Execution & Timelines" / "How fast can our campaign go live?")
        await call("Runtime.evaluate", {
            "expression": """(() => {
                const cards = document.querySelectorAll('.bv-starter-card');
                if (cards.length >= 3) {
                    cards[2].click();
                } else {
                    const inp = document.getElementById('bv-chat-input');
                    const form = document.getElementById('bv-chat-form');
                    inp.value = 'How fast can our campaign go live?';
                    form.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            })()"""
        })
        await asyncio.sleep(1.0)

        # Scroll to bottom
        await call("Runtime.evaluate", {
            "expression": """(() => {
                const msgBox = document.getElementById('bv-chat-messages');
                if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;
            })()"""
        })
        await asyncio.sleep(0.4)

        # Desktop Screenshot
        shot_dt = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/workflow_desktop_fixed.png", "wb") as f:
            f.write(base64.b64decode(shot_dt["data"]))
        print("Saved scratch/qc/workflow_desktop_fixed.png")

        # Mobile Viewport (390x844)
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)

        # Scroll messages to bottom on mobile
        await call("Runtime.evaluate", {
            "expression": """(() => {
                const msgBox = document.getElementById('bv-chat-messages');
                if (msgBox) msgBox.scrollTop = msgBox.scrollHeight;
            })()"""
        })
        await asyncio.sleep(0.4)

        shot_mob = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/workflow_mobile_fixed.png", "wb") as f:
            f.write(base64.b64decode(shot_mob["data"]))
        print("Saved scratch/qc/workflow_mobile_fixed.png")

if __name__ == "__main__":
    asyncio.run(capture_workflow())
