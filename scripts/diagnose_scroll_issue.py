#!/usr/bin/env python3
"""Diagnose exact scroll calculation for #contact and other sections."""
import asyncio
import json
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
        import time
        for _ in range(20):
            time.sleep(0.3)
            try:
                urllib.request.urlopen("http://127.0.0.1:9222/json/version")
                return
            except Exception:
                pass
        raise RuntimeError("Failed to start Chrome")

async def diagnose():
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
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })
        await asyncio.sleep(1.0)

        # 1. Inspect all sections and their content-visibility styles and offsetTop at start
        res1 = await call("Runtime.evaluate", {
            "expression": """(() => {
                const sections = Array.from(document.querySelectorAll('section[id]')).map(s => {
                    const cs = window.getComputedStyle(s);
                    const rect = s.getBoundingClientRect();
                    return {
                        id: s.id,
                        offsetTop: s.offsetTop,
                        rectTop: rect.top,
                        height: rect.height,
                        contentVisibility: cs.contentVisibility,
                        containIntrinsicSize: cs.containIntrinsicSize,
                        scrollMarginTop: cs.scrollMarginTop
                    };
                });
                return {
                    docHeight: document.documentElement.scrollHeight,
                    sections
                };
            })()""",
            "returnByValue": True
        })
        print("Initial Document & Sections State:")
        print(json.dumps(res1.get("result", {}).get("value"), indent=2))

        # 2. Test clicking .coral-quote-btn and measuring every 200ms
        await call("Runtime.evaluate", {
            "expression": "document.querySelector('.coral-quote-btn').click();"
        })
        for i in range(15):
            await asyncio.sleep(0.2)
            prog = await call("Runtime.evaluate", {
                "expression": """(() => {
                    const target = document.getElementById('contact');
                    const rect = target.getBoundingClientRect();
                    return {
                        scrollY: window.scrollY,
                        docHeight: document.documentElement.scrollHeight,
                        targetRectTop: rect.top
                    };
                })()""",
                "returnByValue": True
            })
            val = prog.get("result", {}).get("value")
            print(f"t={(i+1)*200}ms:", val)

if __name__ == "__main__":
    asyncio.run(diagnose())
