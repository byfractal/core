from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.pipeline import DataPipeline
from config import Config
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.json
        api_key = request.headers.get('Authorization')
        
        if not api_key or not api_key.startswith('Bearer '):
            return jsonify({'error': 'Invalid or missing API key'}), 401
            
        # Extrait le token sans le préfixe 'Bearer '
        token = api_key.split(' ')[1]
        
        # Vérifie si le token correspond à l'API_KEY configurée
        if token != Config.API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Récupère les données de la requête
        date_range = data.get('date_range')
        
        if not date_range:
            return jsonify({'error': 'Missing date_range parameter'}), 400
            
        try:
            # Valide la configuration avant d'exécuter
            Config.validate()
            
            # Initialise et exécute le pipeline
            pipeline = DataPipeline()
            result = pipeline.run()
            
            if result:
                return jsonify({
                    'success': True,
                    'data': "Pipeline executed successfully"
                })
            else:
                return jsonify({
                    'success': False,
                    'error': "Pipeline execution failed"
                }), 500
                
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error': str(ve)
            }), 400
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Pour le debugging
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')