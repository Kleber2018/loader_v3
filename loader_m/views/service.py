import sqlite3
from views import service
from views import bdnew
import time
class ConfigFaixa:
 def __init__(Y,v,K,j,q,X,H):
  Y.temp_min=v
  Y.temp_max=K
  Y.umid_ajuste=j
  Y.etapa=q
  Y.updated=X
  Y.expiration=H
class ConfigGeral:
 def __init__(Y,a,j,p,Q,T,q):
  Y.intervalo_seconds=a
  Y.umid_ajuste=j
  Y.escala_temp=p
  Y.alerta_desat=Q 
  Y.speaker=T
  Y.etapa=q
def getLocalConfigFaixa(bd):
 try:
  c=sqlite3.connect(bd)
  R=c.cursor()
  R.execute("SELECT  temp_min, temp_max, umid_ajuste, etapa, updated, expiration FROM config WHERE status = 1")
  G=R.fetchall()
  if len(G)>0:
   c.close()
   return ConfigFaixa(float(G[0][0]),float(G[0][1]),int(G[0][2]),G[0][3],G[0][4],G[0][5])
  else:
   R.execute("SELECT  temp_min, temp_max, umid_ajuste, etapa, updated, expiration FROM config WHERE id_config = 5;")
   G=R.fetchall() 
   R.execute("UPDATE config SET status = 1 WHERE id_config = 5;")
   c.close()
   return ConfigFaixa(float(G[0][0]),float(G[0][1]),int(G[0][2]),G[0][3],G[0][4],G[0][5])
 except Exception as e:
  print('Erro consultar BD getLocalConfigFaixa',e)
  time.sleep(2)
  return False
def getLocalConfigGeral(bd):
 try:
  c=sqlite3.connect(bd)
  R=c.cursor()
  R.execute("SELECT  intervalo_seconds, umid_ajuste, escala_temp, alerta_desat, speaker, etapa FROM config WHERE etapa = 'Padrão'")
  G=R.fetchall()
  if len(G)>0:
   c.close()
   return ConfigGeral(int(G[0][0]),int(G[0][1]),G[0][2],G[0][3],G[0][4],G[0][5])
  else:
   R.execute("SELECT  intervalo_seconds, umid_ajuste, escala_temp, alerta_desat, speaker, etapa FROM config WHERE id_config = 5;")
   G=R.fetchall()
   R.execute("UPDATE config SET etapa = 'Padrão' WHERE id_config = 5;")
   c.close()
   return ConfigGeral(int(G[0][0]),int(G[0][1]),G[0][2],G[0][3],G[0][4],G[0][5])
 except Exception as e:
  print('Erro consultar BD getLocalConfigGeral',e)
  bdnew.criandoSQLiteConf(bd)
  time.sleep(2)
  return False
def add_medicao(V,t,L,numoculto,x,bd):
 try:
  c=sqlite3.connect(bd)
  print('adicionando medição')
  R=c.cursor()
  R.execute("INSERT INTO medicoes (temperatura, temperatura2, umidade, oculto, alerta, status) VALUES (?, ?, ?, ?, ?, 0);",(V,t,L,numoculto,x))
  c.commit()
  c.close()
 except Exception as error:
  print(f"erro ao adicionar medicao em medições: {error}")
  bdnew.criandoSQLiteMedicao(bd)
def updt_medicao(V,t,L,x,bd):
 try:
  c=sqlite3.connect(bd)
  R=c.cursor()
  R.execute("UPDATE medicao SET temperatura = ?, temperatura2 = ?, umidade = ?, alerta = ?, updated = datetime('now', 'localtime') WHERE id_medicao = 1;",(V,t,L,x))
  c.commit()
  c.close()
 except Exception as error:
  print(f"erro ao atualizar medicao: {error}")
  bdnew.criandoSQLiteMedicao(bd)
def verificarAlerta(V,L,config,bd_umid,configGeral):
 global r
 r=0
 if V>0:
  if V>config.temp_max:
   r=11
  elif V<config.temp_min:
   r=12
 try:
  c=sqlite3.connect(bd_umid)
  R=c.cursor()
  R.execute("SELECT umidade FROM umidade WHERE temperatura = ?",(int(V),))
  G=R.fetchall()
  c.close()
  if len(G)>0:
   if L<G[0][0]-(configGeral.umid_ajuste+1):
    r=r+36
   elif L>G[0][0]+(configGeral.umid_ajuste+1):
    r=r+33
  else:
   print('nenhum registro')
 except Exception as error:
  print('ERRO NA TABELA DE UMIDADE busca',error)
 return r
def getserial():
 i="0000000000000000"
 try:
  f=open('/proc/cpuinfo','r')
  for w in f:
   if w[0:6]=='Serial':
    i=w[10:26]
  f.close()
 except:
  i="ERROR000000000"
 return i
def get_cpu_temp():
 u=open("/sys/class/thermal/thermal_zone0/temp")
 s=u.read()
 u.close()
 return float(s)/1000
def add_system_monitor(bd_m):
 try:
  c=sqlite3.connect(bd_m)
  print('adicionando medição monitor')
  R=c.cursor()
  E=get_cpu_temp()
  ns=getserial()
  R.execute("INSERT INTO monitor (temperatura, serie) VALUES (?, ?);",(E,ns))
  c.commit()
  c.close()
 except Exception as error:
  print(f"erro ao adicionar monitor: {error}")
  bdnew.criandoSQLiteMonitorSys(bd_m)
# Created by pyminifier (https://github.com/liftoff/pyminifier)

