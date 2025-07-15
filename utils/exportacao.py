import csv
import sqlite3
from datetime import datetime
import os
from utils.haversine import haversine

class ExportadorDados:
    def __init__(self, db_path='pulverizacao.db'):
        self.db_path = db_path
        
    def exportar_csv(self, nome_arquivo=None):
        """
        Exporta dados da sessão atual para CSV
        
        Args:
            nome_arquivo: Nome do arquivo (default: auto-gerado)
            
        Returns:
            str: Caminho do arquivo gerado
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"pulverizacao_{timestamp}.csv"
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar todos os pontos
            cursor.execute("""
                SELECT timestamp, latitude, longitude, hectares 
                FROM pontos 
                ORDER BY timestamp
            """)
            
            pontos = cursor.fetchall()
            conn.close()
            
            if not pontos:
                raise ValueError("Nenhum dado encontrado para exportar")
            
            # Criar arquivo CSV
            with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Hectares', 'Distancia_m', 'Velocidade_kmh'])
                
                # Dados
                for i, (timestamp, lat, lon, hectares) in enumerate(pontos):
                    if i == 0:
                        distancia = 0
                        velocidade = 0
                    else:
                        # Calcular distância e velocidade
                        ponto_anterior = pontos[i-1]
                        distancia = haversine(ponto_anterior[1], ponto_anterior[2], lat, lon)
                        
                        # Calcular velocidade baseada no tempo
                        tempo_atual = datetime.fromisoformat(timestamp)
                        tempo_anterior = datetime.fromisoformat(ponto_anterior[0])
                        delta_tempo = (tempo_atual - tempo_anterior).total_seconds()
                        
                        if delta_tempo > 0:
                            velocidade = (distancia / delta_tempo) * 3.6  # km/h
                        else:
                            velocidade = 0
                    
                    writer.writerow([timestamp, lat, lon, hectares, round(distancia, 2), round(velocidade, 1)])
            
            return nome_arquivo
            
        except Exception as e:
            raise Exception(f"Erro ao exportar CSV: {str(e)}")
    
    def gerar_relatorio_resumo(self, nome_arquivo=None):
        """
        Gera relatório resumido da sessão
        
        Args:
            nome_arquivo: Nome do arquivo (default: auto-gerado)
            
        Returns:
            str: Caminho do arquivo gerado
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_{timestamp}.txt"
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Buscar todos os pontos
            cursor.execute("""
                SELECT timestamp, latitude, longitude, hectares 
                FROM pontos 
                ORDER BY timestamp
            """)
            
            pontos = cursor.fetchall()
            conn.close()
            
            if not pontos:
                raise ValueError("Nenhum dado encontrado para o relatório")
            
            # Calcular estatísticas
            estatisticas = self._calcular_estatisticas(pontos)
            
            # Gerar relatório
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write("=" * 50 + "\n")
                arquivo.write("RELATÓRIO DE PULVERIZAÇÃO\n")
                arquivo.write("=" * 50 + "\n\n")
                
                arquivo.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                arquivo.write(f"Arquivo de dados: {self.db_path}\n\n")
                
                arquivo.write("RESUMO DA SESSÃO\n")
                arquivo.write("-" * 20 + "\n")
                arquivo.write(f"Pontos coletados: {estatisticas['total_pontos']}\n")
                arquivo.write(f"Área total pulverizada: {estatisticas['area_total']:.2f} hectares\n")
                arquivo.write(f"Distância percorrida: {estatisticas['distancia_total']:.2f} metros\n")
                arquivo.write(f"Tempo total: {estatisticas['tempo_total']}\n")
                arquivo.write(f"Velocidade média: {estatisticas['velocidade_media']:.1f} km/h\n")
                arquivo.write(f"Velocidade máxima: {estatisticas['velocidade_maxima']:.1f} km/h\n\n")
                
                arquivo.write("COORDENADAS EXTREMAS\n")
                arquivo.write("-" * 20 + "\n")
                arquivo.write(f"Latitude mínima: {estatisticas['lat_min']:.6f}\n")
                arquivo.write(f"Latitude máxima: {estatisticas['lat_max']:.6f}\n")
                arquivo.write(f"Longitude mínima: {estatisticas['lon_min']:.6f}\n")
                arquivo.write(f"Longitude máxima: {estatisticas['lon_max']:.6f}\n\n")
                
                arquivo.write("EFICIÊNCIA\n")
                arquivo.write("-" * 20 + "\n")
                arquivo.write(f"Hectares por hora: {estatisticas['hectares_por_hora']:.2f}\n")
                arquivo.write(f"Metros por hectare: {estatisticas['metros_por_hectare']:.2f}\n\n")
                
                # Histórico detalhado (últimos 20 pontos)
                arquivo.write("HISTÓRICO DETALHADO (últimos 20 pontos)\n")
                arquivo.write("-" * 40 + "\n")
                arquivo.write(f"{'Timestamp':<20} {'Latitude':<12} {'Longitude':<12} {'Hectares':<10}\n")
                arquivo.write("-" * 60 + "\n")
                
                for timestamp, lat, lon, hectares in pontos[-20:]:
                    dt = datetime.fromisoformat(timestamp)
                    arquivo.write(f"{dt.strftime('%H:%M:%S'):<20} {lat:<12.6f} {lon:<12.6f} {hectares:<10.4f}\n")
                
            return nome_arquivo
            
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
    
    def _calcular_estatisticas(self, pontos):
        """Calcula estatísticas dos pontos"""
        if not pontos:
            return {}
            
        lats = [p[1] for p in pontos]
        lons = [p[2] for p in pontos]
        hectares = [p[3] for p in pontos]
        
        # Estatísticas básicas
        estatisticas = {
            'total_pontos': len(pontos),
            'area_total': sum(hectares),
            'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons)
        }
        
        # Calcular distância total e velocidades
        distancia_total = 0
        velocidades = []
        
        for i in range(1, len(pontos)):
            p1 = pontos[i-1]
            p2 = pontos[i]
            
            # Distância
            dist = haversine(p1[1], p1[2], p2[1], p2[2])
            distancia_total += dist
            
            # Velocidade
            tempo1 = datetime.fromisoformat(p1[0])
            tempo2 = datetime.fromisoformat(p2[0])
            delta_tempo = (tempo2 - tempo1).total_seconds()
            
            if delta_tempo > 0:
                velocidade = (dist / delta_tempo) * 3.6
                if velocidade < 50:  # Filtrar velocidades absurdas
                    velocidades.append(velocidade)
        
        estatisticas['distancia_total'] = distancia_total
        
        # Tempo total
        if len(pontos) > 1:
            inicio = datetime.fromisoformat(pontos[0][0])
            fim = datetime.fromisoformat(pontos[-1][0])
            tempo_total = fim - inicio
            estatisticas['tempo_total'] = str(tempo_total).split('.')[0]  # Remover microssegundos
            
            # Velocidades
            if velocidades:
                estatisticas['velocidade_media'] = sum(velocidades) / len(velocidades)
                estatisticas['velocidade_maxima'] = max(velocidades)
            else:
                estatisticas['velocidade_media'] = 0
                estatisticas['velocidade_maxima'] = 0
                
            # Eficiência
            horas_totais = tempo_total.total_seconds() / 3600
            if horas_totais > 0:
                estatisticas['hectares_por_hora'] = estatisticas['area_total'] / horas_totais
            else:
                estatisticas['hectares_por_hora'] = 0
                
            if estatisticas['area_total'] > 0:
                estatisticas['metros_por_hectare'] = distancia_total / estatisticas['area_total']
            else:
                estatisticas['metros_por_hectare'] = 0
        else:
            estatisticas['tempo_total'] = "00:00:00"
            estatisticas['velocidade_media'] = 0
            estatisticas['velocidade_maxima'] = 0
            estatisticas['hectares_por_hora'] = 0
            estatisticas['metros_por_hectare'] = 0
        
        return estatisticas
    
    def limpar_dados(self):
        """Limpa todos os dados do banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pontos")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Erro ao limpar dados: {str(e)}")
    
    def backup_dados(self, nome_arquivo=None):
        """Cria backup do banco de dados"""
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"backup_{timestamp}.db"
            
        try:
            import shutil
            shutil.copy2(self.db_path, nome_arquivo)
            return nome_arquivo
        except Exception as e:
            raise Exception(f"Erro ao fazer backup: {str(e)}")
    
    def obter_estatisticas_rapidas(self):
        """Retorna estatísticas rápidas para exibição"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar pontos
            cursor.execute("SELECT COUNT(*) FROM pontos")
            total_pontos = cursor.fetchone()[0]
            
            # Área total
            cursor.execute("SELECT SUM(hectares) FROM pontos")
            area_total = cursor.fetchone()[0] or 0
            
            # Último ponto
            cursor.execute("SELECT timestamp FROM pontos ORDER BY timestamp DESC LIMIT 1")
            ultimo_ponto = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_pontos': total_pontos,
                'area_total': area_total,
                'ultimo_ponto': ultimo_ponto[0] if ultimo_ponto else None
            }
            
        except Exception as e:
            return {
                'total_pontos': 0,
                'area_total': 0,
                'ultimo_ponto': None
            } 