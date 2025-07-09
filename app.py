from flask import Flask, render_template
from database import DatabaseManager
import os

app = Flask(__name__)

# Configuração do banco de dados
DB_NAME = 'savi_dados_unificado mes 06 e 07 juntos.db'

def init_sample_data():
    """Inicializa dados de exemplo se o banco não existir"""
    if not os.path.exists(DB_NAME):
        db = DatabaseManager(DB_NAME)
        db.create_sample_data()
        db.close()

@app.route('/')
def index():
    """Página principal com os três relatórios"""
    try:
        # Inicializar dados de exemplo se necessário
        init_sample_data()
        
        # Conectar ao banco e buscar dados
        db = DatabaseManager(DB_NAME)
        
        # Obter os três relatórios
        relatorio_geral = db.get_relatorio_geral()
        relatorio_igor = db.get_relatorio_igor()
        relatorio_divinopolis = db.get_relatorio_divinopolis()
        
        # Calcular resumos para cada relatório
        resumo_geral = db.calcular_resumo(relatorio_geral)
        resumo_igor = db.calcular_resumo(relatorio_igor)
        resumo_divinopolis = db.calcular_resumo(relatorio_divinopolis)
        
        db.close()
        
        return render_template('index.html', 
                             relatorio_geral=relatorio_geral,
                             relatorio_igor=relatorio_igor,
                             relatorio_divinopolis=relatorio_divinopolis,
                             resumo_geral=resumo_geral,
                             resumo_igor=resumo_igor,
                             resumo_divinopolis=resumo_divinopolis)
    
    except Exception as e:
        return f"Erro ao processar dados: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)