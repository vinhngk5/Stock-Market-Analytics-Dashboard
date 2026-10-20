# 📈 Stock Market Analytics Dashboard

🚀 An end-to-end stock market analytics platform built with **Python, PostgreSQL, Streamlit, and Docker**.

The project collects 📊 stock market data, stores it in 🗄️ PostgreSQL, performs 🔎 analytical queries, and presents the results through an 📈 interactive dashboard.

---

## ✨ Features

* 📥 Collect stock market data using **Yahoo Finance (`yfinance`)**
* 🗄️ Store structured data in **PostgreSQL**
* 🔎 Perform data analysis using **SQL**
* 📊 Build interactive visualizations with **Streamlit** and **Plotly**
* 🐳 Containerize the application and database using **Docker Compose**
* 💾 Persist PostgreSQL data using Docker volumes
* ❤️ Automatically wait for PostgreSQL to become healthy before starting the application

---

## 🏗️ Architecture

```text
              📡 Yahoo Finance
                     │
                     ▼
              🐍 Python / yfinance
                     │
                     ▼
             ⚙️ Data Processing
                     │
                     ▼
                🗄️ PostgreSQL
                     │
                     ▼
                🔎 SQL Analytics
                     │
                     ▼
             📊 Streamlit Dashboard
```

### 🛠️ Technology Stack

| Component           | Technology             |
| ------------------- | ---------------------- |
| 🐍 Programming      | Python 3.12            |
| 📥 Data Collection  | yfinance               |
| 🔢 Data Processing  | Pandas, NumPy          |
| 🗄️ Database        | PostgreSQL 16          |
| 🔌 Database Driver  | psycopg 3              |
| 📊 Visualization    | Streamlit, Plotly      |
| 🐳 Containerization | Docker, Docker Compose |
| 🐧 Environment      | Linux / Ubuntu         |

---

## 📂 Project Structure

```text
📦 Stock-Market-Analytics-Dashboard/
│
├── 📁 src/
│   │
│   ├── 📁 core/
│   │   └── ⚙️ config.py
│   │       └── Application and environment configuration
│   │
│   ├── 📁 database/
│   │   ├── 🔌 connection.py
│   │   │   └── PostgreSQL connection management
│   │   ├── 🗄️ init.sql
│   │   │   └── Database schema initialization
│   │   └── 📚 repository.py
│   │       └── Database access and data retrieval operations
│   │
│   ├── 📁 provider/
│   │   └── 📈 yfinance_loader.py
│   │       └── Stock market data loading from Yahoo Finance
│   │
│   ├── 📁 service/
│   │   ├── 📊 analytics_service.py
│   │   │   └── Analytical logic and financial data processing
│   │   └── 📥 ingestion_service.py
│   │       └── Data ingestion workflow
│   │
│   └── 🚀 app.py
│       └── Streamlit dashboard entry point
│
├── ⚙️ .env.example
│   └── Environment variable template
│
├── 🐳 Dockerfile
│   └── Application container configuration
│
├── 🐳 docker-compose.yml
│   └── Multi-container application orchestration
│
├── 📦 requirements.txt
│   └── Python dependencies
│
├── 📖 README.md
│   └── Project documentation
│
└── 📄 LICENSE
    └── MIT License
```

---

## 📋 Requirements

Before running the project, make sure you have:

* 🐍 Python 3.12+
* 🐳 Docker
* 🐳 Docker Compose
* 🔧 Git

💡 The project can run entirely with Docker, so installing Python packages locally is not required.

---

## ⚙️ Configuration

Create a `.env` file from the provided example:

```bash
cp .env.example .env
```

Configure the PostgreSQL credentials in `.env`.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=stocks
```

🔐 **Security:** Do not commit `.env` to GitHub if it contains real credentials.

---

## 🚀 Run with Docker Compose

The recommended way to run the project is with Docker Compose.

### 1️⃣ Clone the repository

```bash
git clone https://github.com/vinhngk5/Stock-Market-Analytics-Dashboard.git

cd Stock-Market-Analytics-Dashboard
```

### 2️⃣ Create environment configuration

```bash
cp .env.example .env
```

Edit `.env` if necessary.

### 3️⃣ Build and start the services

```bash
docker compose up --build
```

The project starts two services:

```text
🐳 stock-market-app
        │
        │ PostgreSQL
        ▼
🐘 stock-market-db
```

PostgreSQL runs on port `5432` inside the Docker network, while Streamlit is exposed on port `8501`.

❤️ The application waits for the PostgreSQL healthcheck to pass before starting the Streamlit service.

### 4️⃣ Open the dashboard

🌐 Open your browser and navigate to:

```text
http://localhost:8501
```

---

## 🛑 Stop the Application

Press:

```text
Ctrl + C
```

or run:

```bash
docker compose down
```

This stops and removes the containers while keeping PostgreSQL data stored in the Docker volume.

---

## ▶️ Start Again

After the initial build:

```bash
docker compose up
```

Run services in the background:

```bash
docker compose up -d
```

Check running services:

```bash
docker compose ps
```

---

## 📜 Logs

### 🖥️ Application logs

```bash
docker compose logs app
```

### 🗄️ PostgreSQL logs

```bash
docker compose logs db
```

### 🔴 Follow all logs

```bash
docker compose logs -f
```

---

## 🗄️ Database

The application uses **PostgreSQL 16** as the primary data store.

The database schema is initialized from:

```text
src/database/init.sql
```

### 💾 Persistent Storage

PostgreSQL data is persisted through the Docker volume:

```text
pg_data
```

This allows database data to survive container recreation.

### ⚠️ Important

`init.sql` is executed automatically by the PostgreSQL image **only when the database is initialized for the first time with an empty data volume**.

To completely recreate the database:

```bash
docker compose down -v
docker compose up --build
```

⚠️ **Warning:** `-v` removes the PostgreSQL volume and therefore deletes the stored database data.

---

## 💻 Run Without Docker

You can also run the Streamlit application directly on the host machine.

### 1️⃣ Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Start PostgreSQL

Make sure PostgreSQL is running and configure the required environment variables.

### 4️⃣ Start Streamlit

```bash
streamlit run src/app.py
```

🌐 Dashboard:

```text
http://localhost:8501
```

---

## 🔄 Data Workflow

The project follows an end-to-end analytics workflow:

### 1️⃣ 📥 Data Collection

Stock market data is collected using:

```text
yfinance
```

The collected data is prepared for storage and analysis.

### 2️⃣ 🧹 Data Processing

Raw data is transformed and prepared before being stored in the database.

### 3️⃣ 🗄️ Data Storage

Processed stock data is stored in PostgreSQL.

The application communicates with PostgreSQL using:

```text
psycopg 3
```

### 4️⃣ 🔎 Data Analysis

SQL queries are used to retrieve and aggregate the data required for analytics.

This separates the **data layer** from the **presentation layer**.

### 5️⃣ 📊 Visualization

**Streamlit** provides the dashboard interface, while **Plotly** is used to generate interactive charts.

---

## 🐳 Docker Architecture

```text
┌─────────────────────────────┐
│       📊 Streamlit App      │
│       stock-market-app      │
│          Port 8501          │
└──────────────┬──────────────┘
               │
               │ 🔌 PostgreSQL
               ▼
┌─────────────────────────────┐
│       🐘 PostgreSQL DB      │
│       stock-market-db       │
│          Port 5432          │
└──────────────┬──────────────┘
               │
               ▼
          💾 pg_data
```

The application connects to PostgreSQL using the Docker service name:

```text
db
```

instead of:

```text
localhost
```

---

## 🧰 Useful Docker Commands

### 🔨 Build

```bash
docker compose build
```

### ▶️ Start

```bash
docker compose up
```

### 🌙 Start in background

```bash
docker compose up -d
```

### 🛑 Stop

```bash
docker compose down
```

### 🗑️ Stop and remove database volume

```bash
docker compose down -v
```

### ♻️ Rebuild from scratch

```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### 🔍 Check containers

```bash
docker ps
```

### 📜 Check logs

```bash
docker compose logs -f
```

---

## 🧑‍💻 Development

The application source code is mounted into the container:

```yaml
volumes:
  - ./src:/app/src
```

This allows changes in the local `src/` directory to be reflected inside the running container without rebuilding the entire image.

---

## 🚧 Future Improvements

* ⏰ Add scheduled data ingestion
* ✅ Add data validation and quality checks
* 🔄 Add incremental loading instead of full refresh
* 📊 Add more analytical indicators
* 🔐 Add authentication and user access control
* 🧪 Add automated testing
* ⚙️ Add CI/CD with GitHub Actions
* ☁️ Deploy the application to a cloud platform

---

## 📄 License

This project is licensed under the **MIT License**.

---

## ⭐ Acknowledgements

* 📡 [Yahoo Finance](https://finance.yahoo.com/)
* 🐍 [Python](https://www.python.org/)
* 🐘 [PostgreSQL](https://www.postgresql.org/)
* 📊 [Streamlit](https://streamlit.io/)
* 🐳 [Docker](https://www.docker.com/)

