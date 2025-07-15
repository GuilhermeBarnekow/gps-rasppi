import sqlite3
from datetime import datetime

def criar_banco():
    conn = sqlite3.connect('pulverizacao.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS pontos (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            hectares REAL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS fazenda (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            largura_implemento REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_ponto(lat, lon, hectares):
    conn = sqlite3.connect('pulverizacao.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO pontos(timestamp, latitude, longitude, hectares) VALUES(?,?,?,?)',
                (datetime.utcnow().isoformat(), lat, lon, hectares))
    conn.commit()
    conn.close()

def salvar_fazenda(nome, largura_implemento):
    conn = sqlite3.connect('pulverizacao.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM fazenda')  # Apenas um registro de fazenda
    cur.execute('INSERT INTO fazenda(nome, largura_implemento) VALUES(?, ?)', (nome, largura_implemento))
    conn.commit()
    conn.close()

def obter_fazenda():
    conn = sqlite3.connect('pulverizacao.db')
    cur = conn.cursor()
    cur.execute('SELECT nome, largura_implemento FROM fazenda LIMIT 1')
    row = cur.fetchone()
    conn.close()
    if row:
        return {'nome': row[0], 'largura_implemento': row[1]}
    return None
