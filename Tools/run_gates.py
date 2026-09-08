#!/usr/bin/env python3
"""AirboxVIP Coffeenet - Verification Gates"""
import os, sys, json

PASS = []; FAIL = []

def check(name, condition, msg=""):
    if condition: print(f"  PASS {name}"); PASS.append(name)
    else: print(f"  FAIL {name}" + (f": {msg}" if msg else "")); FAIL.append(name)

print("=== AirboxVIP Coffeenet Verification Gates ===\n")

print("[ Gate 1: Frontend Structure ]")
check("package.json exists", os.path.exists("package.json"))
check("index.html exists", os.path.exists("index.html"))
check("vite.config.ts exists", os.path.exists("vite.config.ts"))
check("src/App.tsx exists", os.path.exists("src/App.tsx"))

print("\n[ Gate 2: Package Config ]")
if os.path.exists("package.json"):
    with open("package.json") as f: pkg = json.load(f)
    check("build script", "build" in pkg.get("scripts", {}))
    check("vite dep", "vite" in pkg.get("devDependencies", {}))
    check("react dep", "react" in pkg.get("dependencies", {}))

print("\n[ Gate 3: Telegram Bot ]")
check("bot.py", os.path.exists("telegram_bot/bot.py"))
check("config.py", os.path.exists("telegram_bot/config.py"))
check("requirements.txt", os.path.exists("telegram_bot/requirements.txt"))

print("\n[ Gate 4: Components ]")
for c in ["Hero", "Navbar", "Services", "Footer", "FAQ"]:
    check(f"{c}", os.path.exists(f"src/{c}.jsx") or os.path.exists(f"src/{c}.tsx"))

print(f"\n=== {len(PASS)} passed, {len(FAIL)} failed ===")
if FAIL: print(f"Failed: {', '.join(FAIL)}"); sys.exit(1)
else: print("All gates passed!"); sys.exit(0)