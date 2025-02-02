# AitanMall eCommerce & Customer Service Platform

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)

Refurbished Python implementation of a SaaS eCommerce platform originally engineered in PHP (Summer 2023). Includes a customer service subsystem with plans for AI automation.

## Overview

- This application was created (in 2019) when I first taught myself programming and therefore this project is not very professional. 
- Feel free to clone and use the code!

### 1. **AitanMall (Main eCommerce Platform)**
- **Domain**: `aitanmall.com`
- **Stack**: Flask + MySQL + Flask-SocketIO
- **Features**:
  - Multi-vendor SaaS eCommerce platform
  - Integrated payment gateways (ToyyibPay, Stripe)
  - NinjaVan shipping integration
  - Bulk emailing system
  - Real-time chat with Socket.IO
  - Webhook handlers for 3rd-party services

### 2. **Customer Service Portal**
- **Domain**: `cs.aitanmall.com`
- **Stack**: Flask + MySQL + Flask-SocketIO
- **Features**:
  - Agent authentication system
  - Real-time chat interface
  - Future AI integration roadmap
  - Unified customer interaction management

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Node.js (for Socket.IO client dependencies)

```bash
# Clone repository
git clone https://github.com/yourusername/aitanmall-repo.git
cd aitanmall-repo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows

# Customer Service App
CS_DATABASE_URI=mysql://user:password@localhost/aitanmall_cs

Main Application (aitanmall.com)

Copy

├── webapp/
    |-- views/
        ├── api/               # REST endpoints
        ├── webhooks/          # 3rd-party webhook handlers
    ├── static/                # Frontend assets
    ├── templates/             # Jinja2 templates
    ├── helper/                # All helper functioins
    └── classes                # All classes
├── socket/                # Socket.IO implementation


Customer Service Portal (cs.aitanmall.com)


Note: This Python implementation represents a complete overhaul of the original PHP codebase, with enhanced security, improved database optimization, and modular architecture for future scalability. The customer service AI integration remains in undone stages.