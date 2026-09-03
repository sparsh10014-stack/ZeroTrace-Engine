<div align = "center">

# 🔒 ZeroTrace

### Privacy-Preserving Identity Verification using Zero-Knowledge Proofs

Prove eligibility. Reveal nothing.

Built for **Smart India Hackathon (SIH)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![Status](https://img.shields.io/badge/status-active--development-blue)](#)
[![Made with Flask](https://img.shields.io/badge/backend-Flask-black)](#)
[![ZKP](https://img.shields.io/badge/proofs-Zero--Knowledge-purple)](#)

</div>

---

## 📖 Table of Contents

- [About ZeroTrace](#-about-zerotrace)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally](#running-locally)
- [Demo Personas](#-demo-personas)
- [Team](#-team)
- [License](#-license)

---

## 🧠 About ZeroTrace

**ZeroTrace** is a privacy-first verification system that lets a user *prove* they meet a condition — such as being above a certain age — **without ever revealing the underlying personal data** (like their exact date of birth) to anyone, including the verifying server.

Instead of the traditional model (send your data → server checks it → server stores it), ZeroTrace uses **Zero-Knowledge Proofs (ZKP)**:



This means:
- ✅ No personal data ever leaves the user's device
- ✅ No personal data is ever stored in the database
- ✅ The verifier still gets a mathematically guaranteed, trustworthy yes/no answer

### Why not just encrypt the database?

Encryption still requires decrypting the data at some point to check it — meaning it's exposed at that moment. Zero-Knowledge Proofs never expose the underlying data **at any point in the process**, even during verification.

---

## ⚙️ How It Works

```
Step 1: User enters data  →  Step 2: Proof generated  →  Step 3: Flask verifies  →  Step 4: DB logs
```

| Step | What Happens | Component |
|------|--------------|------------|
| 1️⃣ | User enters their attribute (e.g., date of birth) into the frontend | `/frontend` |
| 2️⃣ | A zero-knowledge proof is generated **on the client**, proving the condition (e.g., age ≥ 18) without revealing the actual value | `/zkp-circuits` |
| 3️⃣ | Only the proof (never the raw data) is sent to the backend, which verifies it | `/backend` |
| 4️⃣ | The pass/fail result + timestamp is logged — no personal data is stored | `/backend` (DB layer) |

If the proof is valid → ✅ green success screen.
If the proof is invalid → ❌ red rejection screen.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | *(e.g., React / HTML-CSS-JS — confirm with Snehalata)* |
| Backend | Flask (Python) |
| Proof System | Zero-Knowledge Proofs — *(e.g., circom + snarkjs — confirm with Sparsh)* |
| Database | *(e.g., SQLite / PostgreSQL — confirm with Sachin)* |
| Networking | Local network / mobile hotspot (demo-safe, no external internet dependency) |

> 📌 **To-do before submission:** Replace the placeholders above with your team's confirmed tools.

---

## 📁 Project Structure

```
ZeroTrace/
├── frontend/          # User-facing input form + result screens
├── backend/           # Flask server — proof verification + logging
├── zkp-circuits/       # Zero-knowledge proof generation & verification logic
├── docs/               # SRS, flowcharts, and supporting documentation
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have installed:
- Python 3.10+
- Node.js 18+ and npm
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/<your-org>/ZeroTrace.git
cd ZeroTrace
```

Install backend dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

Install ZKP circuit dependencies:

```bash
cd ../zkp-circuits
npm install
```

### Running Locally

Start the backend (Flask):

```bash
cd backend
flask run
```

Start the frontend:

```bash
cd frontend
npm start
```

By default:
- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:5000`

**Demo tip:** For hackathon WiFi reliability, run both frontend and backend over a local mobile hotspot instead of relying on venue internet.

---

## 🧪 Demo Personas

To keep the live demo predictable, use these fixed test identities:

| Persona | Input | Expected Result |
|---------|-------|------------------|
| **Persona A** — Valid User | Rahul, Age 22 | 🟢 Green success screen |
| **Persona B** — Invalid User | Aditya, Age 16 | 🔴 Red rejection screen |

---

## 👥 Team

| Name | Role |
|------|------|
| Sparsh | ZKP Circuits & Proof Generation |
| Sachin | Database & Mock Scripts |
| Snehalata | Frontend |
| Ritik | Backend |
| Tanu | Presentation & Design |
| Prakhar | Documentation, GitHub & Demo Coordination |

---

## 📄 License

This project is submitted as part of Smart India Hackathon (SIH) and is licensed under the [MIT License](LICENSE).

---

<div align="center">

Made with ❤️ and zero-knowledge, for **Smart India Hackathon**

</div>
