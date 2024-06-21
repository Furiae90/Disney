# Basisimage
FROM python:3.9

# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere requirements.txt ins Arbeitsverzeichnis
COPY requirements.txt .

# Pakete installieren (mit --no-cache-dir, um Probleme mit Caches zu vermeiden)
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere spezifische Dateien und Ordner ins Arbeitsverzeichnis
COPY . .

# Expose port 80
EXPOSE 8089:8050

# Anwendung starten
CMD ["python", "test_disney_dashboard.py"]