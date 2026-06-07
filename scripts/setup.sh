#!/bin/bash

echo "🔥 RemotePay Setup Script"
echo "========================"

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm not found"; exit 1; }

echo "✅ Prerequisites OK"

# Setup backend
echo ""
echo "📦 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
echo "✅ Backend ready"

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd ../frontend
npm install
cp .env.example .env
echo "✅ Frontend ready"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start:"
echo "  Backend: cd backend && source venv/bin/activate && python main.py"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Open http://localhost:5173"
