import requests

url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=43.2965&longitude=5.3698&hourly=pm10&start_date=2026-11-15&end_date=2026-11-15&timezone=Europe/Paris"

reponse = requests.get(url)
donnees = reponse.json()

print(donnees["hourly"]["pm10"])