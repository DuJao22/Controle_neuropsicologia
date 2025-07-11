import sqlite3
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def conectar(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        """Fecha a conexão com o banco"""
        self.conn.close()
    
    def get_listas_pacientes(self):
        """Retorna as listas de pacientes organizadas"""
        pacientes_igor = [
            'ANA LARA ALVES DOS SANTOS',
            'MIGUEL SILVA NASARE',
            'MARIANA CANDIDO BICALHO',
            'DJAVAN OLIVEIRA MATOS',
            'GABRIEL JUNIO DA SILVA',
            'MELISSA TORRES PASSOS FRAGA',
            'RAYSSA HAKIELLY SOUZA AMARAL',
            'PEDRO HENRIQUE CAMPOS ROCHA',
            'MARIA VITORIA RIBEIRO DE SOUSA RIQUETTI',
            'ANNE ROCHA PARREIRAS PASSOS',
            'Isabbelly Perilda Patricia Cristina',
            'JOAO LUIZ BERNARDES SANTOS PIMENTA',
            'LUCAS ANTONIO RODRIGUES SENA',
            'Bernardo Gabriel Laurindo',
            'BRYAN MIGUEL RODRIGUES BELARMINO',
            'EMANUEL ARAUJO CALAZANS',
            'MARCUS VINICIUS SANTANA DE SOUZA',
            'JOAO MARCOS DUARTE QUEIROZ'
        ]
        
        pacientes_divinopolis = [
            'Murilo Neves Lima Giatti',
            'GEISIVANIA TEIXEIRA MACHADO',
            'Gustavo Henrique Matos da Silva',
            'EDERSON LUCAS DE SOUSA',
            'Angelica Couto Da Silva De Elias',
            'Sophia De Sousa Cavalcante',
            'LAIS VITORIA SILVA LEAOS',
            'Gustavo Sena Moreira Braga',
            'Rafael Henrique Carvalho Campos',
            'Rubens Hilario De Oliveira',
            'Cecilia Neves Silveira',
            'Cecilia Alves De Oliveira',
            'GEISIVANIA TEIXEIRA MACHADO',
            'EDERSON LUCAS DE SOUSA',
            'LAIS VITORIA SILVA LEAOS'
        ]
        
        return pacientes_igor, pacientes_divinopolis
    
    def analisar_paciente(self, nome_paciente: str) -> Dict[str, Any]:
        """Analisa os procedimentos de um paciente específico"""
        self.conectar()
        try:
            query = '''
                SELECT DISTINCT procedimento_codigo, procedimento_nome, qtde_realizada
                FROM producao
                WHERE LOWER(usuario_nome) = LOWER(?)
                    AND qtde_realizada >= 1
                    AND procedimento_codigo IN ('60010142', '60010363')
                ORDER BY procedimento_codigo
            '''
            self.cursor.execute(query, (nome_paciente,))
            procedimentos = self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao consultar paciente {nome_paciente}: {e}")
            self.close()
            return {
                'nome': nome_paciente,
                'procedimentos': [],
                'status': "❌ Erro",
                'faltando': [],
                'tem_teste': False,
                'tem_consulta': False,
                'valor_total': 0
            }

        tem_teste = False
        tem_consulta = False
        procedimentos_encontrados = []
        valor_total_paciente = 0
        
        for proc in procedimentos:
            valor_unitario = 800.00 if proc['procedimento_codigo'] == '60010142' else 80.00
            valor_total_proc = proc['qtde_realizada'] * valor_unitario
            valor_total_paciente += valor_total_proc
            
            procedimentos_encontrados.append({
                'procedimento_codigo': proc['procedimento_codigo'],
                'nome': proc['procedimento_nome'],
                'quantidade': proc['qtde_realizada'],
                'valor_unitario': valor_unitario,
                'valor_total': valor_total_proc
            })
            
            if proc['procedimento_codigo'] == '60010142':
                tem_teste = True
            elif proc['procedimento_codigo'] == '60010363':
                tem_consulta = True
        
        faltando = []
        if not tem_teste:
            faltando.append("60010142 - Teste neuropsicológico")
        if not tem_consulta:
            faltando.append("60010363 - Consulta/sessão de neuropsicologia")
        
        if tem_teste and tem_consulta:
            status = "✅ Completo"
        elif tem_teste or tem_consulta:
            status = "⚠️ Incompleto"
        else:
            status = "❌ Nenhuma senha"

        self.close()
        return {
            'nome': nome_paciente,
            'procedimentos': procedimentos_encontrados,
            'status': status,
            'faltando': faltando,
            'tem_teste': tem_teste,
            'tem_consulta': tem_consulta,
            'valor_total': valor_total_paciente
        }

    def get_relatorio_geral(self) -> List[Dict[str, Any]]:
        """Gera relatório geral com todos os pacientes que realizaram procedimentos"""
        self.conectar()
        query = '''
            SELECT DISTINCT usuario_nome
            FROM producao
            WHERE qtde_realizada >= 1
                AND procedimento_codigo IN ('60010142', '60010363')
            ORDER BY usuario_nome
        '''
        self.cursor.execute(query)
        pacientes = self.cursor.fetchall()
        self.close()

        resultado = []
        for paciente in pacientes:
            analise = self.analisar_paciente(paciente['usuario_nome'])
            resultado.append(analise)
        
        return resultado

    def get_relatorio_igor(self) -> List[Dict[str, Any]]:
        """Gera relatório específico dos pacientes do Igor"""
        pacientes_igor, _ = self.get_listas_pacientes()
        
        resultado = []
        for paciente in pacientes_igor:
            analise = self.analisar_paciente(paciente)
            resultado.append(analise)
        
        return resultado

    def get_relatorio_divinopolis(self) -> List[Dict[str, Any]]:
        """Gera relatório específico dos pacientes de Divinópolis"""
        _, pacientes_divinopolis = self.get_listas_pacientes()
        
        resultado = []
        for paciente in pacientes_divinopolis:
            analise = self.analisar_paciente(paciente)
            resultado.append(analise)
        
        return resultado

    def calcular_resumo(self, relatorio: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula resumo estatístico de um relatório"""
        total_pacientes = len(relatorio)
        completos = 0
        so_teste = 0
        so_consulta = 0
        sem_nenhuma = 0
        valor_total_secao = 0
        
        for paciente in relatorio:
            valor_total_secao += paciente['valor_total']
            
            if paciente['status'] == "✅ Completo":
                completos += 1
            elif paciente['tem_teste'] and not paciente['tem_consulta']:
                so_teste += 1
            elif not paciente['tem_teste'] and paciente['tem_consulta']:
                so_consulta += 1
            else:
                sem_nenhuma += 1
        
        return {
            'total_pacientes': total_pacientes,
            'completos': completos,
            'so_teste': so_teste,
            'so_consulta': so_consulta,
            'sem_nenhuma': sem_nenhuma,
            'valor_total_secao': valor_total_secao
        }
