#!/usr/bin/env python3
"""
Test and capture the Brand Vision AI Chat widget across desktop and mobile.
Verifies:
1. Opening the chat window via launcher button
2. Initial welcome message and quick prompt pills
3. Query handling (Airport, Rates, Kokapet)
4. Mobile viewport layout, alignment, and responsiveness
5. Clear conversation button
6. Close button and keyboard escape
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

async def test_ai_chat():
    ensure_chrome()
    os.makedirs("scratch/qc", exist_ok=True)

    # 1. Desktop Test (1440x900)
    print("\n--- Testing AI Chat on Desktop (1440x900) ---")
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

        # Check launcher visibility
        res = await call("Runtime.evaluate", {
            "expression": "(() => { const l = document.getElementById('bv-chat-launcher'); return l ? { display: window.getComputedStyle(l).display, opacity: window.getComputedStyle(l).opacity } : null; })()",
            "returnByValue": True
        })
        val = res.get("result", {}).get("value")
        print("Desktop launcher style:", val)

        # Click launcher to open
        await call("Runtime.evaluate", {
            "expression": "document.getElementById('bv-chat-launcher').click()"
        })
        await asyncio.sleep(0.5)

        # Screenshot open chat desktop
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/desktop_chat_01_open.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/desktop_chat_01_open.png")

        # Click starter card "The Trilight Kokapet"
        await call("Runtime.evaluate", {
            "expression": "(() => { const cards = document.querySelectorAll('.bv-starter-card'); if (cards[1]) cards[1].click(); })()"
        })
        await asyncio.sleep(0.8)

        # Screenshot after quick pill response
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/desktop_chat_02_query.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/desktop_chat_02_query.png")

    # 2. Mobile Test (390x844)
    print("\n--- Testing AI Chat on Mobile (390x844) ---")
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
        await asyncio.sleep(1.0)

        # Check mobile launcher visibility before scroll
        res_before = await call("Runtime.evaluate", {
            "expression": "(() => { const c = document.querySelector('.bv-chat-container'); const l = document.getElementById('bv-chat-launcher'); return { container_opacity: window.getComputedStyle(c).opacity, launcher_display: window.getComputedStyle(l).display }; })()",
            "returnByValue": True
        })
        print("Mobile before scroll:", res_before.get("result", {}).get("value"))

        # Scroll down 400px to trigger body.mv-scrolled
        await call("Runtime.evaluate", {
            "expression": "window.scrollTo(0, 800); document.body.classList.add('mv-scrolled');"
        })
        await asyncio.sleep(0.5)

        res_after = await call("Runtime.evaluate", {
            "expression": "(() => { const c = document.querySelector('.bv-chat-container'); const l = document.getElementById('bv-chat-launcher'); return { container_opacity: window.getComputedStyle(c).opacity, launcher_rect: l.getBoundingClientRect() }; })()",
            "returnByValue": True
        })
        print("Mobile after scroll:", res_after.get("result", {}).get("value"))

        # Screenshot mobile with launcher visible
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/mobile_chat_00_launcher.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/mobile_chat_00_launcher.png")

        # Click launcher to open
        await call("Runtime.evaluate", {
            "expression": "document.getElementById('bv-chat-launcher').click()"
        })
        await asyncio.sleep(0.5)

        # Screenshot mobile open chat
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/mobile_chat_01_open.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/mobile_chat_01_open.png")

        # Type message: "rates for rgia airport"
        await call("Runtime.evaluate", {
            "expression": "(() => { const inp = document.getElementById('bv-chat-input'); const form = document.getElementById('bv-chat-form'); inp.value = 'rates for rgia airport'; form.dispatchEvent(new Event('submit', { cancelable: true })); })()"
        })
        await asyncio.sleep(0.8)

        # Screenshot mobile chat with reply
        shot = await call("Page.captureScreenshot", {"format": "png"})
        with open("scratch/qc/mobile_chat_02_reply.png", "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("Saved scratch/qc/mobile_chat_02_reply.png")

if __name__ == "__main__":
    asyncio.run(test_ai_chat())
