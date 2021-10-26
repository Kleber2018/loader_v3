# Código Python Estufa Monitoramento

Versão: 16/09/21 - 20:49
### Loader_m
Loop para coleta e informações no visor

### Loader_s

Socket
### Loader_a
Servidor Flask

####################################################################
### Configurando o Raspberry SO 03/07/21

**Instalando bibliotecas:**
```
sudo apt-get install git
sudo apt install python3-pip
sudo apt-get install python-pip
sudo apt-get install python3-venv
```


**Entrar no diretório:**

```
cd /etc
```

**Clonar o projeto:**
```
sudo git clone ….
```
**Compartilhar a pasta loader na rede para facilitar o desenvolvimento:**
https://www.vivaolinux.com.br/dica/Compartilhamento-simples-e-rapido-de-diretorio-para-outros-computadores

**bibliotecas necessárias para o projeto:**

**para main.py**
```
sudo pip3 install adafruit-blinka
pip3 install raspberrypi-tm1637
sudo pip3 install adafruit-circuitpython-sht31d
pip3 install python-socketio
```
**para appsocket.py**
```
pip3 install eventlet
```
**para app.py**
```
pip install Flask
pip3 install -U flask-cors
```


**atribuindo permissão para pasta e subpasta**
```
chmod -R 777 loader
```


## Configurando Inicialização: SystemD
**Instalar SystemD:** https://wiki.debian.org/pt_BR/systemd
```
apt-get update
apt-get install systemd
```
 
Copia script bach para a pasta do systemD: 
```
sudo cp /etc/loader/loader/SYSTEMD/loader_m.service /lib/systemd/system/ 
sudo cp /etc/loader/loader/SYSTEMD/loader_s.service /lib/systemd/system/ 
sudo cp /etc/loader/loader/SYSTEMD/loader_a.service /lib/systemd/system/ 
sudo cp /etc/loader/loader/SYSTEMD/loader_c.service /lib/systemd/system/ 
```

Habilita o script no SystemD: 
```
sudo systemctl enable loader_a.service
sudo systemctl enable loader_s.service
sudo systemctl enable loader_m.service
sudo systemctl enable loader_c.service
```

Lista inicializaçõs do SystemD:
``` 
ls /lib/systemd/system/
```
Privilégios do arquivo:
```
sudo chmod 644 /lib/systemd/system/loader_a.service 
sudo chmod 644 /lib/systemd/system/loader_s.service 
sudo chmod 644 /lib/systemd/system/loader_m.service 
sudo chmod 644 /lib/systemd/system/loader_c.service 
 ```
Privilégios do arquivo: 
```
sudo chmod +x /etc/loader/loader/main.py 
sudo chmod +x /etc/loader/loader/app.py 
sudo chmod +x /etc/loader/loader/appsocket.py 
sudo chmod +x /etc/loader/loader/appcloud.py 
 ```
 
Verificar log de inicialização:
```
sudo systemctl status loader_a
sudo systemctl status loader_m
sudo systemctl status loader_s
 ```
Log de inicialização completo:
```
journalctl
```


# ERROS

## impossibilidade de acessar ssh
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
```
ssh-keygen -R hostname
```


## Tabela de erros display

**Display Umidade**
```
err1: 
err2: Erro ao iniciar Sensor de humidade, Exception em iniciaSHT()
err3: 
err4:
err5: Erro no sensor de umidade, RuntimeError ao coletar umidade do sensor no loop
err6: Erro no sensor de umidade, Exception ao coletar umidade do sensor no loop
err7:
err8:
err9:
err0:
SOKT: servidor socket não inciado. Aguarda um tempo e então inica sem o servidor socket
er26: Erro ao iniciar Sensor de humidade, RuntimeError em iniciaSHT()
er25: Erro ao iniciar Sensor de humidade, Exception retorno da função iniciaSHT()
er27: Erro na inicialização do sensor de umidade no verificador do loop. Exception no if not sensor

```
**Display Temperatura**
```
err1: 
err2: Erro ao iniciar sensor de temperatura, Exception em iniciaSensorTemp()
err3: Erro no sensor de temperatura, Exception ao coletar temperatura do sensor na inicialização
err4: Erro no sensor de temperatura, RuntimeError ao coletar temperatura do sensor na inicialização
err5: Erro no sensor de temperatura, RuntimeError ao coletar temperatura do sensor no loop
err6: Erro no sensor de temperatura, Exception ao coletar temperatura do sensor no loop
err7:
err8:
err9:
err0:
er21: Erro ao iniciar sensor de temperatura, RuntimeError em iniciaSensorTemp()
er22:  Erro ao iniciar sensor de temperatura, Exception retorno da função iniciaSensorTemp()
er23: Erro na inicialização do sensor de temperatura no verificador do loop. Exception no if not DS18B20status
```
