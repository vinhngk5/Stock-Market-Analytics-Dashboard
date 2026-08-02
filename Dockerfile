FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]