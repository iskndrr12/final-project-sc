# Final Project SC

## Development Installation
1. Jalankan docker-compose
```
docker-compose up
```
2. Install dependencies
```
pip install -r requirements.txt
```
3. Inisialisasi database migration (optional)
```
flask --app app/app.py db init
flask --app app/app.py db migrate -m "initial migration"
```
4. Untuk migrasi database ulang (optional)
```
flask --app app/app.py db stamp head
flask --app app/app.py db migrate
flask --app app/app.py db upgrade

docker-compose up --build
```
Kalo waktu upgrade ada error, buka file hasil command migrate, terus ubah urutan di fungsi upgrade()

5. Jalankan seeder
```
flask --app app/app.py seed run
```

## Usage
Flask API akan berjalan pada ```localhost:5000```


Database dapat diakses dengan creds :

- USER = user
- PASSWORD = password
- HOST = localhost
- DB = final-project-sc
- PORT = 15432

