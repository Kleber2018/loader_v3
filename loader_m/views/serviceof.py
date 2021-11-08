import sqlite3
from views import service
from views import bdnew
import time
class ConfigFaixa:
 def __init__(P,b,j,l,u,Q,e):
  P.temp_min=b
  P.temp_max=j
  P.umid_ajuste=l
  P.etapa=u
  P.updated=Q
  P.expiration=e
class ConfigGeral:
 def __init__(P,i,l,y,p,f,u):
  P.intervalo_seconds=i
  P.umid_ajuste=l
  P.escala_temp=y
  P.alerta_desat=p 
  P.speaker=f
  P.etapa=u
def getLocalConfigFaixa(bd):
 try:
  w=sqlite3.connect(bd)
  t=w.cursor()
  t.execute("SELECT  temp_min, temp_max, umid_ajuste, etapa, updated, expiration FROM config WHERE status = 1")
  g=t.fetchall()
  if len(g)>0:
   w.close()
   return ConfigFaixa(float(g[0][0]),float(g[0][1]),int(g[0][2]),g[0][3],g[0][4],g[0][5])
  else:
   t.execute("SELECT  temp_min, temp_max, umid_ajuste, etapa, updated, expiration FROM config WHERE id_config = 5;")
   g=t.fetchall() 
   t.execute("UPDATE config SET status = 1 WHERE id_config = 5;")
   w.close()
   return ConfigFaixa(float(g[0][0]),float(g[0][1]),int(g[0][2]),g[0][3],g[0][4],g[0][5])
 except Exception as e:
  print('Erro consultar BD getLocalConfigFaixa',e)
  time.sleep(2)
  return False
def getLocalConfigGeral(bd):
 try:
  w=sqlite3.connect(bd)
  t=w.cursor()
  t.execute("SELECT  intervalo_seconds, umid_ajuste, escala_temp, alerta_desat, speaker, etapa FROM config WHERE etapa = 'Padrão'")
  g=t.fetchall()
  if len(g)>0:
   w.close()
   return ConfigGeral(int(g[0][0]),int(g[0][1]),g[0][2],g[0][3],g[0][4],g[0][5])
  else:
   t.execute("SELECT  intervalo_seconds, umid_ajuste, escala_temp, alerta_desat, speaker, etapa FROM config WHERE id_config = 5;")
   g=t.fetchall()
   t.execute("UPDATE config SET etapa = 'Padrão' WHERE id_config = 5;")
   w.close()
   return ConfigGeral(int(g[0][0]),int(g[0][1]),g[0][2],g[0][3],g[0][4],g[0][5])
 except Exception as e:
  print('Erro consultar BD getLocalConfigGeral',e)
  bdnew.criandoSQLite(bd)
  time.sleep(2)
  return False
def add_medicao(N,L,numoculto,c,bd):
 try:
  w=sqlite3.connect(bd)
  print('adicionando medição')
  t=w.cursor()
  t.execute("INSERT INTO medicoes (temperatura, umidade, oculto, alerta) VALUES (?, ?, ?, ?);",(N,L,numoculto,c))
  w.commit()
  w.close()
 except Exception as error:
  print(f"erro ao adicionar medicao: {error}")
def updt_medicao(N,L,c,bd):
 try:
  w=sqlite3.connect(bd)
  t=w.cursor()
  t.execute("UPDATE medicao SET temperatura = ?, umidade = ?, alerta = ?, updated = datetime('now', 'localtime') WHERE id_medicao = 1;",(N,L,c))
  w.commit()
  w.close()
 except Exception as error:
  print(f"erro ao atualizar medicao: {error}")
def verificarAlerta(N,L,config,bd_umid,configGeral):
 global r
 r=0
 if N>0:
  if N>config.temp_max:
   r=11
  elif N<config.temp_min:
   r=12
 try:
  w=sqlite3.connect(bd_umid)
  t=w.cursor()
  t.execute("SELECT umidade FROM umidade WHERE temperatura = ?",(int(N),))
  g=t.fetchall()
  w.close()
  if len(g)>0:
   if L<g[0][0]-(configGeral.umid_ajuste+1):
    r=r+36
   elif L>g[0][0]+(configGeral.umid_ajuste+1):
    r=r+33
  else:
   print('nenhum registro')
 except Exception as error:
  print('ERRO NA TABELA DE UMIDADE busca',error)
 return r
def getserial():
 n="0000000000000000"
 try:
  f=open('/proc/cpuinfo','r')
  for H in f:
   if H[0:6]=='Serial':
    n=H[10:26]
  f.close()
 except:
  n="ERROR000000000"
 return n
def get_cpu_temp():
 z=open("/sys/class/thermal/thermal_zone0/temp")
 V=z.read()
 z.close()
 return float(V)/1000
def add_system_monitor(bd_m):
 try:
  w=sqlite3.connect(bd_m)
  print('adicionando medição monitor')
  t=w.cursor()
  R=get_cpu_temp()
  ns=getserial()
  t.execute("INSERT INTO monitor (temperatura, serie) VALUES (?, ?);",(R,ns))
  w.commit()
  w.close()
 except Exception as error:
  print(f"erro ao adicionar monitor: {error}")
  bdnew.criandoSQLiteMonitorSys(bd_m)
# Created by pyminifier (https://github.com/liftoff/pyminifier)

