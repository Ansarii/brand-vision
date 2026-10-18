#!/usr/bin/env python3
"""
Capture workflow from top of message so cards 01, 02, 03 are visible.
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

async def capture_workflow_top():
    ensure_chrome()
    os.makedirs("scratch/qc", exist_ok=True)
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

        # Mobile Viewport
        await call("Emulation.setDeviceMetricsOverride", {
            "width": 390,
            "height": 844,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        await asyncio.sleep(0.8)

        # Clear sessionStorage and open chat
        await call("Runtime.evaluate", {
            "expression": """(() => {
                sessionStorage.clear();
                const launcher = document.getElementById('bv-chat-launcher');
                if (launcher) launcher.click();
            })()"""
        })
        await asyncio.sleep(0.5)

        # Submit question
        await call("Runtime.evaluate", {
            "expression": """(() => {
                const inp = document.getElementById('bv-chat-input');
                const form = document.getElementById('bv-chat-form');
                inp.value = 'How fast can our campaign go live?';
                form.dispatchEvent(new Event('submit', { cancelable: true }));
            })()"""
        })
        await asyncio.sleep(1.2)

        # Ensure scroll is at the top of the bot response
        await call("Runtime.evaluate", {
            "expression": """(() => {
                const botRows = document.querySelectorAll('.bv-msg-bot');
                const lastBot = botRows[botRows.length - 1];
                if (lastBot) lastBot.scrollIntoView({ behavior: 'auto', block: 'start' });
            })()"""
        })
        await asyncio.sleep(0.3)

        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/workflow_mobile_top_view.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/workflow_mobile_top_view.png")

if __name__ == "__main__":
    asyncio.run(capture_workflow_top())
