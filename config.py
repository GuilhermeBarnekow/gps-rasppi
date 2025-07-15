import json
import os
import sqlite3
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.configuracoes_padrao = {
            'gnss': {
                'porta': '/dev/serial0',
                'baudrate': 9600,
                'timeout': 2.0,
                'modo_simulacao': False,
                'posicao_simulacao': [-15.7801, -47.9292]
            },
            'interface': {
                'largura_tela': 800,
                'altura_tela': 480,
                'fullscreen': True,
                'fps': 30,
                'mouse_visivel': False
            },
            'mapa': {
                'zoom_inicial': 2.0,
                'auto_centralize': True,
                'mostrar_grid': True,
                'mostrar_escala': True
            },
            'pulverizacao': {
                'largura_implemento_padrao': 12.0,
                'unidade_area': 'hectares',
                'precisao_decimal': 2
            },
            'exportacao': {
                'formato_padrao': 'csv',
                'incluir_cabecalho': True,
                'separador_csv': ',',
                'encoding': 'utf-8'
            },
            'velocimetro': {
                'janela_tempo': 5,
                'filtro_velocidade_maxima': 50.0,
                'threshold_parado': 0.5
            },
            'sistema': {
                'debug': False,
                'log_level': 'INFO',
                'backup_automatico': True,
                'intervalo_backup': 3600  # segundos
            }
        }
        
        self.configuracoes = self.carregar_configuracoes()
        
    def carregar_configuracoes(self):
        """Carrega configurações do arquivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    configuracoes = json.load(f)
                    
                # Mesclar com configurações padrão para garantir completude
                return self._mesclar_configuracoes(self.configuracoes_padrao, configuracoes)
            else:
                # Criar arquivo de configuração com valores padrão
                self.salvar_configuracoes(self.configuracoes_padrao)
                return self.configuracoes_padrao.copy()
                
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self.configuracoes_padrao.copy()
    
    def salvar_configuracoes(self, configuracoes=None):
        """Salva configurações no arquivo JSON"""
        try:
            if configuracoes is None:
                configuracoes = self.configuracoes
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configuracoes, f, indent=4, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def obter(self, caminho, valor_padrao=None):
        """
        Obtém valor de configuração usando caminho pontuado
        
        Args:
            caminho: Caminho da configuração (ex: 'gnss.porta')
            valor_padrao: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração ou valor padrão
        """
        try:
            keys = caminho.split('.')
            valor = self.configuracoes
            
            for key in keys:
                valor = valor[key]
                
            return valor
            
        except (KeyError, TypeError):
            return valor_padrao
    
    def definir(self, caminho, valor):
        """
        Define valor de configuração usando caminho pontuado
        
        Args:
            caminho: Caminho da configuração (ex: 'gnss.porta')
            valor: Novo valor
        """
        try:
            keys = caminho.split('.')
            config_atual = self.configuracoes
            
            # Navegar até o penúltimo nível
            for key in keys[:-1]:
                if key not in config_atual:
                    config_atual[key] = {}
                config_atual = config_atual[key]
            
            # Definir o valor final
            config_atual[keys[-1]] = valor
            
            # Salvar automaticamente
            self.salvar_configuracoes()
            
            return True
            
        except Exception as e:
            print(f"Erro ao definir configuração: {e}")
            return False
    
    def resetar_secao(self, secao):
        """Reseta uma seção para valores padrão"""
        if secao in self.configuracoes_padrao:
            self.configuracoes[secao] = self.configuracoes_padrao[secao].copy()
            self.salvar_configuracoes()
            return True
        return False
    
    def resetar_todas(self):
        """Reseta todas as configurações para valores padrão"""
        self.configuracoes = self.configuracoes_padrao.copy()
        self.salvar_configuracoes()
        return True
    
    def _mesclar_configuracoes(self, padrao, atual):
        """Mescla configurações mantendo estrutura padrão"""
        resultado = padrao.copy()
        
        for chave, valor in atual.items():
            if chave in resultado:
                if isinstance(valor, dict) and isinstance(resultado[chave], dict):
                    resultado[chave] = self._mesclar_configuracoes(resultado[chave], valor)
                else:
                    resultado[chave] = valor
            else:
                resultado[chave] = valor
                
        return resultado
    
    def obter_configuracoes_completas(self):
        """Retorna todas as configurações"""
        return self.configuracoes.copy()
    
    def validar_configuracoes(self):
        """Valida se as configurações estão corretas"""
        erros = []
        
        # Validar porta GNSS
        porta = self.obter('gnss.porta')
        if not isinstance(porta, str) or not porta.strip():
            erros.append("Porta GNSS inválida")
        
        # Validar baudrate
        baudrate = self.obter('gnss.baudrate')
        if not isinstance(baudrate, int) or baudrate <= 0:
            erros.append("Baudrate inválido")
        
        # Validar resolução da tela
        largura = self.obter('interface.largura_tela')
        altura = self.obter('interface.altura_tela')
        if not isinstance(largura, int) or largura <= 0:
            erros.append("Largura da tela inválida")
        if not isinstance(altura, int) or altura <= 0:
            erros.append("Altura da tela inválida")
        
        # Validar largura do implemento
        largura_impl = self.obter('pulverizacao.largura_implemento_padrao')
        if not isinstance(largura_impl, (int, float)) or largura_impl <= 0:
            erros.append("Largura do implemento inválida")
        
        return erros
    
    def exportar_configuracoes(self, arquivo):
        """Exporta configurações para arquivo"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.configuracoes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao exportar configurações: {e}")
            return False
    
    def importar_configuracoes(self, arquivo):
        """Importa configurações de arquivo"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                configuracoes = json.load(f)
            
            # Validar antes de aplicar
            config_temp = ConfigManager()
            config_temp.configuracoes = configuracoes
            erros = config_temp.validar_configuracoes()
            
            if erros:
                print(f"Configurações inválidas: {erros}")
                return False
            
            self.configuracoes = self._mesclar_configuracoes(self.configuracoes_padrao, configuracoes)
            self.salvar_configuracoes()
            return True
            
        except Exception as e:
            print(f"Erro ao importar configurações: {e}")
            return False

# Instância global para uso em toda a aplicação
config_manager = ConfigManager()

# Funções de conveniência
def get_config(caminho, valor_padrao=None):
    """Obtém configuração"""
    return config_manager.obter(caminho, valor_padrao)

def set_config(caminho, valor):
    """Define configuração"""
    return config_manager.definir(caminho, valor)

def save_config():
    """Salva configurações"""
    return config_manager.salvar_configuracoes()

def reset_config(secao=None):
    """Reseta configurações"""
    if secao:
        return config_manager.resetar_secao(secao)
    else:
        return config_manager.resetar_todas()

# Configurações específicas para desenvolvimento
def setup_development():
    """Configura para desenvolvimento"""
    config_manager.definir('gnss.modo_simulacao', True)
    config_manager.definir('sistema.debug', True)
    config_manager.definir('interface.fullscreen', False)
    config_manager.definir('interface.mouse_visivel', True)

def setup_production():
    """Configura para produção"""
    config_manager.definir('gnss.modo_simulacao', False)
    config_manager.definir('sistema.debug', False)
    config_manager.definir('interface.fullscreen', True)
    config_manager.definir('interface.mouse_visivel', False) 