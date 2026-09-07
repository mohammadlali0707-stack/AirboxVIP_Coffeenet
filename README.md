# AirboxVIP Coffeenet ☕📶

**AirboxVIP Coffeenet** is a Telegram bot designed to automate and manage guest WiFi access and hotspot vouchers for coffee shops, cafes, and co-working spaces.

---

## 🚀 Features

- **Guest Self-Service:** Customers can request and receive instant WiFi voucher codes directly via Telegram (`/wifi`).
- **Router & Hotspot Integration:** Built-in adapter for MikroTik RouterOS API and captive portals with time and bandwidth limits.
- **Admin Management:**
  - Issue custom vouchers with specified duration (`/issue [minutes]`).
  - Revoke vouchers immediately (`/revoke <code>`).
  - Monitor active vouchers and router connection status (`/active`, `/status`).
- **Bilingual Interface:** Persian (Farsi) and English support for guest instructions.
- **Offline / Mock Development:** Includes an in-memory mock router client for local development and CI testing without hardware dependencies.

---

## 📁 Project Structure

```
AirboxVIP_Coffeenet/
├── bot/
│   ├── config.py             # Environment configuration
│   ├── handlers/             # Bot command handlers
│   │   ├── admin.py          # Admin controls (/issue, /revoke, /status)
│   │   ├── common.py         # Start, help, and welcome messages
│   │   └── wifi.py           # Customer WiFi voucher requests
│   ├── models/               # Domain models (Voucher, etc.)
│   │   └── voucher.py
│   ├── services/             # Business logic & integrations
│   │   ├── router_client.py  # RouterOS API & mock client
│   │   └── wifi_service.py   # Voucher issuing & management service
│   └── main.py               # Bot entrypoint (Polling & CLI demo)
├── tests/                    # Unit & integration tests
│   └── test_wifi_service.py
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🛠️ Quickstart & Setup

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/momonakikugava-pixel/AirboxVIP_Coffeenet.git
cd AirboxVIP_Coffeenet

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and fill in your details:

```bash
cp .env.example .env
```

Key environment variables:
- `TELEGRAM_BOT_TOKEN`: Token obtained from [@BotFather](https://t.me/BotFather).
- `ADMIN_CHAT_IDS`: Comma-separated list of Telegram user IDs with admin privileges.
- `ROUTER_HOST`, `ROUTER_USER`, `ROUTER_PASSWORD`: MikroTik RouterOS credentials.
- `DEFAULT_VOUCHER_DURATION_MINUTES`: Default voucher validity (default: 60 minutes).

### 3. Run the Bot

**Demo / CLI Mode (No Telegram token required):**
```bash
python3 -m bot.main --demo
```

**Production Mode:**
```bash
python3 -m bot.main
```

### 4. Running Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## 🤖 Bot Commands

| Command | Role | Description |
|---|---|---|
| `/start` | All | Welcome message and instructions |
| `/wifi` | All | Request a temporary WiFi voucher |
| `/status` | All | Check network and system status |
| `/help` | All | Display help menu |
| `/issue [minutes]` | Admin | Issue a new voucher |
| `/revoke <code>` | Admin | Revoke an existing voucher |
| `/active` | Admin | View all active vouchers |

---

## 📄 License
MIT License
