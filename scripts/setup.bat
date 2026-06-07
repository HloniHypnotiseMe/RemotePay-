@echo off
echo 🔥 RemotePay Setup Script
echo ========================

echo 📦 Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
echo ✅ Backend ready

echo.
echo 🎨 Setting up frontend...
cd ..\frontend
npm install
copy .env.example .env
echo ✅ Frontend ready

echo.
echo 🎉 Setup complete!
echo.
echo To start:
echo   Backend: cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo   Frontend: cd frontend ^&^& npm run dev
echo.
echo Open http://localhost:5173
