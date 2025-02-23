import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import logging
from collection_module.pipeline.analysis.pipeline import DataPipeline
from collection_module.pipeline.ingestion.get_data import fetch_data_for_period, get_data
from collection_module.pipeline.utils.utils import setup_logging
from collection_module.pipeline.utils.config import Config

logger = setup_logging()

class AmplitudeDataUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Importation de données Amplitude")
        self.root.geometry("600x400")
        
        # Configuration du logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Variables
        self.api_key_var = tk.StringVar(value=Config.API_KEY or "")
        self.days_var = tk.StringVar(value="30")
        self.status_var = tk.StringVar(value="Prêt")
        
        # Widgets
        ttk.Label(main_frame, text="Clé API Amplitude :").grid(row=0, column=0, pady=5, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.api_key_var, width=50).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Nombre de jours à importer :").grid(row=1, column=0, pady=5, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.days_var, width=10).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Importer les données", command=self.import_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Traiter les données", command=self.process_data).pack(side=tk.LEFT, padx=5)
        
        # Barre de progression
        self.progress = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Status
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2)
        
        # Log viewer
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        self.log_text.pack(expand=True, fill=tk.BOTH)
        
        # Scrollbar pour les logs
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def update_status(self, message, is_error=False):
        """Met à jour le status et les logs"""
        self.status_var.set(message)
        
        # Ajouter le message aux logs
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_level = "ERROR" if is_error else "INFO"
        log_message = f"[{timestamp}] {log_level}: {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)  # Scroll to bottom
        
        if is_error:
            self.logger.error(message)
            messagebox.showerror("Erreur", message)
        else:
            self.logger.info(message)
            
    def import_data(self):
        """Importe les données depuis Amplitude"""
        try:
            self.logger.info("Import des données en cours...")
            
            # Vérification de la configuration
            if not Config.API_KEY:
                raise ValueError("La clé API n'est pas configurée")
                
            # Valider les entrées
            days = int(self.days_var.get())
            if days <= 0:
                raise ValueError("Le nombre de jours doit être positif")
                
            # Mettre à jour la clé API si nécessaire
            if self.api_key_var.get():
                Config.API_KEY = self.api_key_var.get()
                
            # Débuter l'import
            self.update_status("Import des données en cours...")
            self.progress['value'] = 20
            self.root.update_idletasks()
            
            # Récupérer les données
            fetch_data_for_period(days)
            
            self.progress['value'] = 100
            self.update_status("Import terminé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'import: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de l'import: {str(e)}")
            self.progress['value'] = 0
            
    def process_data(self):
        """Traite les données importées"""
        try:
            self.update_status("Traitement des données en cours...")
            self.progress['value'] = 20
            self.root.update_idletasks()
            
            # Lancer le pipeline
            pipeline = DataPipeline()
            if pipeline.run():
                self.progress['value'] = 100
                self.update_status("Traitement terminé avec succès")
            else:
                raise Exception("Échec du traitement des données")
                
        except Exception as e:
            self.update_status(f"Erreur lors du traitement: {str(e)}", True)
            self.progress['value'] = 0

def main():
    root = tk.Tk()
    app = AmplitudeDataUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()