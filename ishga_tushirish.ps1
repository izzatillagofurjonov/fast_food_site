Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\izzatilla\OneDrive\Ishchi stol\web_app\fast_food_site'; & 'venv\Scripts\Activate.ps1'; python manage.py runserver"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\izzatilla\OneDrive\Ishchi stol\web_app\sarab-restaurant-web'; npm run dev"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cloudflared tunnel --url http://localhost:5173"