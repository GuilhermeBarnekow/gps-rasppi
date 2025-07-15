# GPS Navegador para Pulverização Agrícola

Sistema completo de navegação GPS para pulverização agrícola desenvolvido em Python/Pygame, otimizado para Raspberry Pi OS e tela touchscreen 800x480.

## 🚀 Características Principais

### ✅ Funcionalidades Implementadas

- **Sistema GNSS Robusto**: Leitura confiável de dados GPS via UART (módulo M10FLY)
- **Interface Moderna**: Layout responsivo com paleta de cores consistente e componentes reutilizáveis
- **Mapa 2D Interativo**: Visualização em tempo real com coordenadas GPS reais
- **Velocímetro Integrado**: Cálculo de velocidade instantânea, média e máxima
- **Painel de Métricas**: Exibição organizada de estatísticas de pulverização
- **Controles Touch**: Botões touchscreen para iniciar/parar rota
- **Exportação de Dados**: Exportação para CSV e relatórios detalhados
- **Sistema de Backup**: Backup automático dos dados coletados
- **Modo Simulação**: Simulação GPS para desenvolvimento e testes

### 🛠 Melhorias Implementadas

1. **Sistema de UI Modular**
   - Componentes reutilizáveis (botões, painéis, métricas)
   - Paleta de cores moderna e consistente
   - Animações suaves e feedback visual

2. **Velocímetro Real**
   - Cálculo baseado em pontos GNSS consecutivos
   - Velocidade instantânea, média e máxima
   - Detecção de parada automática

3. **Coordenadas GPS Reais**
   - Conversão precisa de lat/lon para pixels
   - Sistema de zoom e pan interativo
   - Auto-ajuste para mostrar toda a trilha

4. **Controles Touch**
   - Botões para iniciar/parar rota
   - Exportação e limpeza de dados
   - Teclado virtual melhorado

5. **Exportação Avançada**
   - Relatórios CSV detalhados
   - Resumos de sessão em texto
   - Estatísticas de eficiência

6. **Tratamento de Erros GNSS**
   - Reconexão automática
   - Fallback inteligente
   - Validação de dados GPS

## 📋 Requisitos do Sistema

### Hardware
- Raspberry Pi 4 (recomendado)
- Tela touchscreen 800x480
- Módulo GNSS M10FLY ou compatível
- Conexão UART (/dev/serial0)

### Software
- Raspberry Pi OS (Debian-based)
- Python 3.8+
- Pygame 2.5.2+

## 🔧 Instalação

### 1. Clonar o Repositório
```bash
git clone <url_do_repositorio>
cd gps_navegador
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar UART (Raspberry Pi)
```bash
# Habilitar UART
sudo raspi-config
# Navegar para: Interfacing Options > Serial > No > Yes

# Adicionar ao /boot/config.txt
echo "enable_uart=1" | sudo tee -a /boot/config.txt
echo "dtoverlay=disable-bt" | sudo tee -a /boot/config.txt

# Reiniciar
sudo reboot
```

### 4. Executar o Sistema
```bash
# Modo desenvolvimento (simulação)
python main.py

# Modo produção (GPS real)
# Editar config.py para desabilitar simulação
python main.py
```

## 🎮 Uso do Sistema

### Controles
- **ESC**: Sair do sistema
- **F1**: Alternar modo simulação/GPS real
- **WASD**: Navegar pelo mapa
- **+/-**: Zoom in/out
- **Mouse**: Arrastar para mover o mapa
- **Scroll**: Zoom com mouse

### Fluxo de Operação
1. **Configurar Largura**: Inserir largura do implemento
2. **Iniciar Rota**: Pressionar botão "Iniciar Rota"
3. **Monitorar**: Acompanhar métricas em tempo real
4. **Parar Rota**: Pressionar botão novamente
5. **Exportar**: Salvar dados para análise

### Interface Principal
- **Mapa**: Área esquerda com trilha e posição do trator
- **Painel Lateral**: Métricas e controles
- **Status**: Informações do sistema na parte inferior

## 📊 Dados Coletados

### Banco de Dados
- **Localização**: `pulverizacao.db`
- **Tabela**: `pontos`
- **Campos**: timestamp, latitude, longitude, hectares

### Exportação
- **CSV**: Dados detalhados por ponto
- **Relatório**: Resumo da sessão
- **Campos**: coordenadas, velocidade, área, tempo

## ⚙️ Configuração

### Arquivo config.json
```json
{
  "gnss": {
    "porta": "/dev/serial0",
    "baudrate": 9600,
    "modo_simulacao": false
  },
  "interface": {
    "largura_tela": 800,
    "altura_tela": 480,
    "fullscreen": true
  },
  "pulverizacao": {
    "largura_implemento_padrao": 12.0
  }
}
```

### Configurações Principais
- **GNSS**: Porta serial, baudrate, modo simulação
- **Interface**: Resolução, fullscreen, FPS
- **Pulverização**: Largura padrão, unidades
- **Exportação**: Formatos, encoding

## 🔍 Desenvolvimento

### Estrutura do Projeto
```
gps_navegador/
├── main.py              # Aplicação principal
├── config.py            # Sistema de configuração
├── db.py                # Banco de dados SQLite
├── gnss.py              # Módulo GNSS melhorado
├── ui/
│   ├── components.py    # Componentes UI reutilizáveis
│   ├── mapa.py          # Sistema de mapa 2D
│   ├── widgets.py       # Widgets do HUD
│   └── teclado.py       # Teclado virtual
├── utils/
│   ├── area_calc.py     # Cálculos de área
│   ├── coordenadas.py   # Sistema de coordenadas
│   ├── exportacao.py    # Exportação de dados
│   ├── haversine.py     # Cálculos de distância
│   └── velocimetro.py   # Cálculos de velocidade
└── requirements.txt     # Dependências Python
```

### Modo Desenvolvimento
```python
# Ativar simulação GPS
from config import setup_development
setup_development()

# Ou manual
from config import set_config
set_config('gnss.modo_simulacao', True)
```

### Teste de Componentes
```python
# Testar velocímetro
from utils.velocimetro import Velocimetro
v = Velocimetro()
v.adicionar_ponto(-15.7801, -47.9292)

# Testar coordenadas
from utils.coordenadas import SistemaCoordenadasGPS
coords = SistemaCoordenadasGPS()
x, y = coords.gps_para_pixel(-15.7801, -47.9292)
```

## 📝 Próximos Passos

### Melhorias Futuras
- [ ] Menu de configurações na interface
- [ ] Alertas sonoros e visuais
- [ ] Integração com sensores adicionais
- [ ] API REST para monitoramento remoto
- [ ] Relatórios em PDF com gráficos
- [ ] Backup automático na nuvem

### Otimizações
- [ ] Cache de tiles de mapa
- [ ] Otimização de performance
- [ ] Redução de consumo de energia
- [ ] Melhor tratamento de memória

## 🐛 Solução de Problemas

### GPS Não Conecta
```bash
# Verificar dispositivo serial
ls -la /dev/serial*

# Testar comunicação
sudo minicom -D /dev/serial0 -b 9600
```

### Erro de Permissão
```bash
# Adicionar usuário ao grupo dialout
sudo usermod -a -G dialout $USER
```

### Tela Não Responde
```bash
# Verificar calibração touch
xinput --list
xinput --list-props "Device Name"
```

## 🤝 Contribuição

1. Fork do projeto
2. Criar branch para feature (`git checkout -b feature/AmazingFeature`)
3. Commit das mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

- **Issues**: Use o sistema de issues do GitHub
- **Documentação**: Wiki do projeto
- **Discussões**: Discussions do GitHub

---

**Desenvolvido para agricultura de precisão** 🌱

Sistema robusto e confiável para pulverização agrícola com navegação GPS precisa e interface moderna. 