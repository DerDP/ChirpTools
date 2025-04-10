```markdown
# ChirpTools

A Flask application to manage ChirpStack assets (bulk import, bulk move, bulk delete, etc.).

## 📦 Requirements

- Git
- Python 3.9+
- Docker & Docker Compose (for containerized setup)

## 🧪 Clone the Repository

```bash
git clone https://gitlab.opencode.de/smart-city-potsdam/udp-lorawan/tools.git
cd ChirpTools
```

## ⚙️ Environment Configuration

Copy `.env.example` to `.env` and adjust environment variables as needed:

```bash
cp .env.example .env
```

---

## 🐳 Run with Docker

Build and run the app using Docker Compose:

```bash
docker-compose up --build
```

- App will be available at: `http://localhost:5000`
- Make sure `.env` is configured correctly before running

To stop the app:

```bash
docker-compose down
```

---

## 🧪 Run Locally (Python venv)

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Set environment variables from `.env` (or export them manually)

4. Start the Flask app:

```bash
python -m flask --app main run --debug
```

App will be accessible at: `http://localhost:5000`

---

