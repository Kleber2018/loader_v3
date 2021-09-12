import time
time.sleep(1.0)
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import sqlite3
import sys

from flask_cors import CORS
import socket #https://wiki.python.org.br/SocketBasico
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

#bd = '/home/pi/estufa_banco.db'
bd = '/etc/loader/loader/loader_banco.db'
version = '3.1.0'


app.secret_key = 'flask'
#app.config.from_object('config')

from views import auth

class Usuario:
    def __init__(self, login, nome, telefone, email, privilegios, senha):
        self.login = login
        self.senha = senha
        self.nome = nome
        self.Telefone = telefone
        self.email = email
        self.privilegios = privilegios


class Medicao:
    def __init__(self, id_medicao, temperatura, umidade, alerta, data):
        self.id_medicao = id_medicao
        self.temperatura = temperatura
        self.umidade = umidade
        self.alerta = alerta
        self.data = data


class Config:
    def __init__(self, etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs):
        self.etapa = etapa
        self.intervalo_seconds = intervalo_seconds
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.umid_ajuste = umid_ajuste
        self.escala_temp = escala_temp
        self.alerta_desat = alerta_desat
        self.speaker = speaker
        self.updated = updated
        self.obs = obs



@app.route('/updatedatasistema', methods=['GET', ])
def updatedatasistema():
    try:
        datetime_request = request.args['datetime']
        return_token = auth.verify_autentication_api(request.args['token'])
        if 'autenticado' in return_token:
            print('autenticado')
        else:
            return jsonify({'erro': 'Necessario estar logado'})
    except:
        return jsonify({'erro': 'Necessario estar logado'})
    import os
    from datetime import datetime
    try:
        c = os.popen(f"sudo date -s '{datetime_request}'")
        c.read()
        c.close()
        now = datetime.now()
    except Exception:
        return jsonify({'datetime': f"{now}"})
    return jsonify({'datetime': f"{now}"})     # return jsonify({'retorno' : f"{request.remote_addr}"}) #ip do requisitante

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    from datetime import datetime
    try:
        active = auth.verify_key()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
        now = datetime.now()
        return jsonify(
            {'retorno': f"{IP}", 'datetime': f"{now}", 'nome': 'Estufa 1', 'a': f"{active}", 'version': f"{version}"})  # ip do raspberry
    except Exception as e:
        return jsonify({'erro': f"{e}"})

@app.route('/sis', methods=['POST'])
def sis():
    from datetime import datetime
    try:
        # mac = ''
        # fd = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        # fd.bind(('eth0', 9999))
        # mac = fd.getsockname()[-1]
        # print(mac)
        # # print(':'.join(['%02x' % ord(n) for n in mac]))
        #from uuid import getnode as get_mac
        #mac = get_mac()
        ns = auth.getserial()
        now = datetime.now()
        return jsonify({'retorno': f"{ns}", 'datetime': f"{now}", 'nome': 'Estufa 1'})  
    except Exception as e:
        print(f"Erro SIS: {e}")
        return jsonify({'retorno': f"erro", 'nome': 'Estufa 1'})      # return jsonify({'retorno' : f"{request.remote_addr}"}) #ip do requisitante


@app.route('/loader', methods=['POST'])
def loader():
    try:
        print(request.json['cod'])
        print(request.json['key'])
        if 'cod' in request.json:
            if 'key' in request.json:
                payload = {
                    'cod': request.json['cod'],
                    'key': request.json['key']
                }
                jwt_created = auth.create_jwt(payload)
                arquivo = open('/etc/loader/loader/load.conf', 'w')
                arquivo.write(jwt_created)
                arquivo.close()

                return jsonify({'token': f"{jwt_created}"})
            else:
                return jsonify({'erro': 'Key invalido!'})
        else:
            return jsonify({'erro': 'Cod invalida!'})
    except Exception as e:
        print(f"Erro Loader: {e}")
        return jsonify({'erro': f"Erro Loader: {e}"})


@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    logado = 1
    medicoes = []
    temperaturas = []
    umidades = []
    dias = []
    alertas = []
    a = auth.verify_key()
    conf = getLocalConfigGeral()
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_medicao, temperatura, umidade, strftime('(%d) %H:%M',created) FROM medicoes"
            " WHERE oculto = '0' or oculto = '2' ORDER BY id_medicao DESC LIMIT 50")
        for id_medicao, temperatura, umidade, data in cur:
            temp = round(temperatura, 1)
            if conf.escala_temp == 'C':
                temp = round(((temperatura - 32) * 5/9), 1)
            medicoes.append(
                {'id': id_medicao, 'temperatura': float(temp),
                 'umidade': float(umidade),
                 'data': f"{data}"})
            temperaturas.insert(0, float(temp))
            umidades.insert(0, float(umidade))
            dias.insert(0, f"{data}")
        cur.execute(
            "SELECT id_medicao, temperatura, umidade, alerta, strftime('(%d) %H:%M',created) FROM medicoes"
            " WHERE alerta = 1 and oculto < 9 ORDER BY created DESC LIMIT 25")
        for id_medicao, temperatura, umidade, alerta, created in cur:
            descricao = ''
            if alerta == 1:
                descricao == f"Temperatura: {temperatura} está fora"
            elif alerta == 3:
                descricao == f"Umidade: {umidade} está fora"
            elif alerta == 4:
                descricao == f"Umidade: {umidade} e Temperatura: {temperatura} estão fora"
            alertas.append(
                {'id': id_medicao,
                 'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'descricao': descricao,
                 'created': f"{created}"})
        cur.execute("SELECT temperatura, umidade, alerta, strftime('(%d) %H:%M',updated) "
                    "FROM medicao WHERE id_medicao = 1")
        rows = cur.fetchall()

        medicao = {'temp': 0, 'umid': 0, 'alert': 0, 'upd': 'erro'}
        if len(rows) > 0:
            tm = round(rows[0][0], 1)
            if conf.escala_temp == 'C':
                tm = round(((round(rows[0][0], 1) - 32) * 5/9), 1)
            medicao = {'temp': tm, 'umid': round(rows[0][1], 1), 'alert': rows[0][2], 'upd': rows[0][3], 'escala': conf.escala_temp}
        cur.close()
        conn.close()
        if 'usuario_logado' not in session or session['usuario_logado'] == None:
            logado = 0
    except Exception as e:
        print(f"Erro SQLite: {e}")
    return render_template('lista.html', titulo='Medições', medicoes=medicoes, temperaturas=temperaturas,
                           umidades=umidades, dias=dias, alertas=alertas, a=a, logado=logado, medicao=medicao )


def verificaAlerta(alerta):
    retorno = {'tem_alert': '', 'temp_umid': ''}
    if alerta == 11 or alerta == 44 or alerta == 47:
        retorno.tem_alert = 'alta'
    elif alerta == 12 or alerta == 45 or alerta == 48:
        retorno.tem_alert = 'baixo'
    else: 
         retorno.tem_alert = ''
    if alerta == 33 or alerta == 44 or alerta == 45:
        retorno.temp_umid = 'alta'
    elif alerta == 36 or alerta == 47 or alerta == 48:
        retorno.temp_umid = 'baixo'
    else: 
        retorno.temp_umid = ''

@app.route('/medicao', methods=['GET'])
def medicao():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("SELECT temperatura, umidade, alerta, updated "
                    "FROM medicao WHERE id_medicao = 1")
        retornoBD = []
        for temperatura, umidade, alerta, updated in cur:
            retornoBD.append(
                {'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'alerta': alerta,
                 'updated': f"{updated}"})
        cur.close()
        conn.close()
        return jsonify(retornoBD)
    except Exception as error:
        print(f"Erro Medição SQLITE: {error}")
        return jsonify({'erro': f"{error}"})


@app.route('/medicoes', methods=['GET'])
def medicoes():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        print(request.args['oculto'])
        ocultopesq = request.args['oculto'].split(',')
        if len(ocultopesq) != 4:
            ocultopesq = [0, 1, 2, 3]
        cur.execute("SELECT id_medicao, temperatura, umidade, alerta, created FROM medicoes"
                    " WHERE created >= ? and created <= ? and (oculto = ? or oculto = ? or oculto = ? or oculto = ?) ORDER BY id_medicao DESC LIMIT 60",
                    (request.args['datainicial'], request.args['datafinal'], ocultopesq[0], ocultopesq[1], ocultopesq[2], ocultopesq[3]))
        retornoBD = []
        for id_medicao, temperatura, umidade, alerta, created in cur:
            retornoBD.append(
                {'id': id_medicao,
                 'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'alerta': alerta,
                 'data': f"{created}"})
        cur.close()
        conn.close()
        return jsonify(retornoBD)
    except Exception as e:
        print(f"Erro SQLite: {e}")
        #sys.exit(1)
        return jsonify({'erro': f"{e}"})



@app.route('/alertas', methods=['GET'])
def alertas():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_medicao, temperatura, umidade, alerta, created FROM medicoes"
            " WHERE alerta = 1 ORDER BY id_medicao DESC LIMIT 25")
        retornoBD = []
        for id_medicao, temperatura, umidade, alerta, created in cur:
            retornoBD.append(
                {'id': id_medicao,
                 'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'alerta': alerta,
                 'data': f"{created}"})
        cur.close()
        conn.close()
        return jsonify(retornoBD)
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return jsonify({'erro': f"{e}"})


@app.route('/alertasperiodo', methods=['GET'])
def alertasperiodo():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_medicao, temperatura, umidade, alerta, created FROM medicoes"
            " WHERE  created >= ? and created <= ? and alerta > 0 ORDER BY id_medicao DESC LIMIT 50",
            (request.args['datainicial'], request.args['datafinal']))
        retornoBD = []
        for id_medicao, temperatura, umidade, alerta, created in cur:
            retornoBD.append(
                {'id': id_medicao,
                 'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'alerta': alerta,
                 'data': f"{created}"})
        cur.close()
        conn.close()
        return jsonify(retornoBD)
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return jsonify({'erro': f"{e}"})

@app.route('/apiconfig', methods=['GET'])
def apiconfig():
    try:
        configui = configRetorno()
        return jsonify(configui)
    except Exception as e:
        return jsonify({'erro': f"{e}"})

def configRetorno():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "SELECT etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs "
            "FROM config WHERE id_config = 5")
        configs = []
        for etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs in cur:
            configs.append(
                {'etapa': etapa,
                 'intervalo_seconds': int(intervalo_seconds),
                 'temp_min': float(temp_min),
                 'temp_max': float(temp_max),
                 'umid_ajuste': umid_ajuste,
                 'escala_temp': escala_temp,
                 'alerta_desat': alerta_desat,
                 'speaker': speaker,
                 'updated': f"{updated}",
                 'obs': obs})
        cur.close()
        conn.close()
        return configs[0]
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return {'erro': f"{e}"}


def getLocalConfigGeral():
    try:
        con = sqlite3.connect(bd)
        cursor = con.cursor()
        cursor.execute(
            "SELECT etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs FROM config WHERE id_config = 5;")
        rows = cursor.fetchall()
        if len(rows) > 0:
            con.close()
            return Config(rows[0][0], int(rows[0][1]), int(rows[0][2]), int(rows[0][3]), int(rows[0][4]), rows[0][5], rows[0][6], rows[0][7], rows[0][8], rows[0][9])
        else:
            cursor.execute(
                "SELECT etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs FROM config WHERE id_config = 5;")
            rows = cursor.fetchall()
            cursor.execute("UPDATE config SET etapa = 'Padrão' WHERE id_config = 5;")
            con.close()
            return Config(rows[0][0], int(rows[0][1]), int(rows[0][2]), int(rows[0][3]), int(rows[0][4]), rows[0][5], rows[0][6], rows[0][7], rows[0][8], rows[0][9])
    except Exception as e:
        print('Erro consultar BD getLocalConfigGeral', e)
        return {'erro': f"{e}"}

@app.route('/novo')
def novo():
    usuarios = []
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("SELECT login, nome, telefone, email, privilegios FROM usuario")
        for login, nome, telefone, email, privilegios in cur:
            usuarios.append(Usuario(login, nome, telefone, email, privilegios, ' '))
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro SQLite: {e}")
        if conn:
            conn.close()
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    else:
        return render_template('novo.html', titulo='Novo Usuario', usuarios=usuarios)


@app.route('/criar', methods=['POST', ])
def criar():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("INSERT INTO Usuario(login, senha, nome, telefone, email, privilegios) VALUES (?, ?, ?, ?, ?, ?);",
                    (
                        request.form['login'].lower(),
                        request.form['Senha'].lower(),
                        request.form['Nome'],
                        request.form['Telefone'],
                        request.form['Email'],
                        'adm'
                    ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Erro SQLite: {e}")
        if conn:
            conn.close()
        return redirect(url_for('novo'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST', ])
def autenticar():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        login = request.form['login'],
        senha = request.form['senha'],
        print(login, senha)
        cur.execute("SELECT login, senha, nome, telefone, email, privilegios FROM usuario "
                    "WHERE login = ? and senha = ?", (login[0].lower(), senha[0].lower(),))
        usuario = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro SQLite: {e}")
        flash(f"Erro SQLite: {e}")
        return redirect(url_for('login'))
    if len(usuario) == 1:
        session['usuario_logado'] = usuario[0][0]
        flash(usuario[0][2] + ' acesso permitido!')
        proxima_pagina = request.form['proxima']
        return redirect(proxima_pagina)
    else:
        flash('Acesso negado, digite novamente!')
        return redirect(url_for('login'))


@app.route('/loginapi', methods=['POST', ])
def loginapi():
    try:
        if 'senha' in request.json:
            if 'user' in request.json:
                login_retorno = auth.autentication_api(request.json['user'], request.json['senha'])
                retornoj = jsonify(login_retorno)
                if 'erro' in retornoj.json:
                    print("verificar se existe")
                    try:
                        arquivo = open('/etc/loader/loader/login_livre.conf', 'r')
                        horario = arquivo.readline()
                        arquivo.close()
                        hora_login_livre = datetime.fromisoformat(horario)
                        agora = datetime.now()
                        print(agora, hora_login_livre, agora+timedelta(minutes = 10))
                        print(agora > hora_login_livre, hora_login_livre+timedelta(minutes = 10) > agora)
                        if agora > hora_login_livre and hora_login_livre+timedelta(minutes = 10) > agora:
                            try:
                                conn = sqlite3.connect(bd)
                                cur = conn.cursor()
                                cur.execute("INSERT INTO Usuario(login, senha, nome, telefone, email, privilegios) VALUES (?, ?, 'auto', '', '', 'adm');",
                                            (
                                                request.json['user'].lower(),
                                                request.json['senha'].lower()
                                            ))
                                conn.commit()
                                cur.close()
                                conn.close()
                            except Exception as e:
                                print(f"Erro SQLite: {e}")
                                return jsonify({'erro': e}) 
                            login_retorno = auth.autentication_api(request.json['user'], request.json['senha'])
                            return jsonify(login_retorno)
                        else:
                            return jsonify(login_retorno)
                    except Exception as e:
                        print('erro ao criar arquivo', e)
                        return jsonify({'erro': e})
                else:
                    return jsonify(login_retorno)
            else:
                return jsonify({'erro': 'Usuario invalido!'})
        else:
            return jsonify({'erro': 'Senha invalida!'})
    except:
        return jsonify({'erro': 'Erro na requisicao'})

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Usuário deslogado')
    return redirect(url_for('index'))

@app.route('/resetarkey', methods=['GET', ])
def resetarkey():
    try:
        return_token = auth.verify_autentication_api(request.args['token'])
        if 'autenticado' in return_token:
            print('autenticado 491')
        else:
            return jsonify({'erro': 'Necessario estar logado'})
    except:
        return jsonify({'erro': 'Necessario estar logado'})
    try:
        arquivo = open('/etc/loader/loader/key.conf', 'w')
        arquivo.write(f'{datetime.now()}')
        arquivo.close()
        return jsonify({'retorno': 'Resetado todos os acessos com sucesso'})
    except Exception as e:
        print('erro ao criar arquivo', e)
        return jsonify({'erro': e})


@app.route('/config')
def config():
    config = ''
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "SELECT etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs "
            "FROM config WHERE id_config = 5")
        for etapa, intervalo_seconds, temp_min, temp_max, umid_ajuste, escala_temp, alerta_desat, speaker, updated, obs in cur:
            config = Config(etapa, int(intervalo_seconds), float(temp_min), float(temp_max), int(umid_ajuste), str(escala_temp),
                            int(alerta_desat), int(speaker), str(updated), obs)
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Erro SQLite: {e}")
        if conn:
            conn.close()
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    else:
        return render_template('config.html', titulo='Configuração', config=config)

@app.route('/excluiruser', methods=['POST', ])
def excluiruser():
    try:
        if 'usuario_logado' not in session or session['usuario_logado'] == None:
            return redirect(url_for('login', proxima=url_for('novo')))
        print(((f"{request.form['login']}"),))
        flash('Tem certeza que deseja excluir o usuário?')
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("DELETE FROM usuario WHERE login = ?;", ((request.form['login']),))
        #conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('novo'))
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return redirect(url_for('novo'))


@app.route('/salvarconfig', methods=['POST', ])
def salvarconfig():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        intervalo = request.form['intervalo']
        print("intervalo", intervalo)
        if int(intervalo) < 60:
            intervalo = 60
        print((
                request.form['etapa'],
                intervalo,
                request.form['umidAjuste'],
                request.form['escalaTemp'],
                request.form['alertaDesat'],
                request.form['speaker'],
                request.form['obs']
            ))
        cur.execute(
            "UPDATE Config SET etapa = ?, intervalo_seconds= ?, umid_ajuste = ?, escala_temp = ?, alerta_desat = ?, speaker = ?, updated = datetime('now'), obs = ? WHERE id_config = 5;",
            (
                request.form['etapa'],
                intervalo,
                request.form['umidAjuste'],
                request.form['escalaTemp'],
                request.form['alertaDesat'],
                request.form['speaker'],
                request.form['obs']
            ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return redirect(url_for('config'))



@app.route('/apisalvarconfig', methods=['POST', ])
def apisalvarconfig():
    try:
        if 'token' in request.json:
            return_token = auth.verify_autentication_api(request.json['token'])
            if 'autenticado' in return_token:
                print('autenticado')
            else:
                return jsonify({'erro': 'Necessario estar logado!'})
        else:
            return jsonify({'erro': 'Necessario estar logado!'})
        if request.json['config']['intervalo_seconds'] < 60:
            intervalo = 60
        else:
            intervalo = request.json['config']['intervalo_seconds']
        temp_min = request.json['config']['temp_min']
        temp_max = request.json['config']['temp_max']
        umid_ajuste = request.json['config']['umid_ajuste']
        escala_temp = request.json['config']['escala_temp']
        alerta_desat = 0
        speaker = 0
        id = 5
        try: 
            speaker = request.json['config']['speaker']
            alerta_desat = request.json['config']['alerta_desat']
            id = request.json['config']['id']
        except:
            alerta_desat = 0
            speaker = 0
            id=5
        obs = request.json['config']['obs']
        etapa = request.json['config']['etapa']

    except Exception as e:
        print(f"Erro SQLite 585: {e}")
        return jsonify({'retorno': f"{e}"})
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute(
            "UPDATE config SET etapa = ?, intervalo_seconds= ?, temp_min = ?, temp_max = ?, umid_ajuste = ?, escala_temp = ?, alerta_desat = ?, speaker = ?, updated = datetime('now'), obs = ? WHERE id_config = ?;",
            (
                etapa,
                intervalo,
                temp_min,
                temp_max,
                umid_ajuste,
                escala_temp,
                alerta_desat,
                speaker,
                obs,
                id
            ))
        conn.commit()
        cur.close()
        conn.close()
        print('salvo')
        return jsonify({'retorno': f"salvo"})
    except Exception as e:
        print(f"Erro SQLite: {e}")
        return jsonify({'retorno': f"{e}"})


@app.route('/silenciaralertas')
def silenciaralertas():
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("UPDATE medicoes SET alerta = 1 WHERE alerta = 2;;")
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Erro SQLite: {e}")
        if conn:
            conn.close()
        return redirect(url_for('index'))


@app.route('/silenciaralertasapi', methods=['GET'])
def silenciaralertasapi():
    try:
        return_token = auth.verify_autentication_api(request.args['token'])
        if 'autenticado' in return_token:
            print('autenticado')
        else:
            return jsonify({'erro': 'Necessario estar logado'})
    except:
        return jsonify({'erro': '´Parametros invalidos'})
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        cur.execute("UPDATE medicoes SET alerta = 1 WHERE alerta = 2;")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'retorno': f"ok"})
    except Exception as e:
        print(f"Erro SQLite: {e}")
        if conn:
            conn.close()
        #flash(e)
        return jsonify({'retorno': f"{e}"})


@app.route('/apiocultarmedicoes', methods=['GET', ])
def apiocultarmedicoes():
    try:
        if 'token' in request.json:
            return_token = auth.verify_autentication_api(request.json['token'])
            if 'autenticado' in return_token:
                print('autenticado')
            else:
                return jsonify({'erro': 'Necessario estar logado!'})
        else:
            return jsonify({'erro': 'Necessario estar logado!'})
        id = request.args['id']
    except:
        return jsonify({'erro': '´Parametros invalidos'})
    try:
        conn = sqlite3.connect(bd)
        cur = conn.cursor()
        print(f"VALOR DE N: {id}")
        cur.execute(
            "UPDATE medicoes SET oculto = ? WHERE id_medicao = ?;",
            (
                '9',
                id
            ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'retorno': f"alterado"})
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({'retorno': f"Erro ao alterar", 'erro': f"{e}"})


if __name__ == "__main__":
    debug = True 
    app.run(host='0.0.0.0', port=5000, debug=debug)
