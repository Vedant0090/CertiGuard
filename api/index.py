from flask import Flask, request, jsonify
from app import app   # import your existing flask app

# Vercel expects variable named "app"
# so just re-export it

# no changes needed if app.py already has:
# app = Flask(__name__)