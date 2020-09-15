#!/usr/bin/python

from OpenSSL import SSL
from cryptography import x509
from cryptography.x509.oid import NameOID
import idna
import os
import csv
import datetime
import time
from socket import socket, AF_INET, SOCK_STREAM , SHUT_RDWR

from collections import namedtuple

class sslcheck :

    HostInfo = namedtuple(field_names='cert hostname peername', typename='HostInfo')
    certificados_exp = []
    retry = 3
    delay = 2
    timeout = 1
    days_before = 20
    def __init__(self):
        # Lectura de los host desde csv
        self.hosts = {}
        self.get_hosts()
        self.dic_hosts = {}

    def get_hosts (self):
        list_host =  self.read_csv()
        for host in list_host:
            host_port = {}
            host_port['dns'] = host
            host_port['http'] =  self.checkHost(host,80)
            host_port['https']= self.checkHost(host,443)  
            self.hosts[host]=host_port

    def read_csv(self):
        hosts = []
        with open('./csv/domains.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                hosts.append((row[0]))
        return hosts
    
    def isOpen(self, ip, port):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
                s.connect((ip, int(port)))
                s.shutdown(SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()
    def checkHost(self, ip, port):
        ipup = False
        for i in range(self.retry):
                if self.isOpen(ip, port):
                        ipup = True
                        break
                else:
                        time.sleep(self.delay)
        return ipup

    def verify_cert(self, cert, hostname):
        # verify notAfter/notBefore, CA trusted, servername/sni/hostname
        cert.has_expired()
        # service_identity.pyopenssl.verify_hostname(client_ssl, hostname)
        # issuer

    def get_certificate(self, hostname, port):
        try:
            hostname_idna = idna.encode(hostname)
            sock = socket()
            #print(hostname,port)
            sock.connect((hostname, port))
            peername = sock.getpeername()
            ctx = SSL.Context(SSL.SSLv23_METHOD) # most compatible
            ctx.check_hostname = False
            ctx.verify_mode = SSL.VERIFY_NONE

            sock_ssl = SSL.Connection(ctx, sock)
            sock_ssl.set_connect_state()
            sock_ssl.set_tlsext_host_name(hostname_idna)
            sock_ssl.do_handshake()
            cert = sock_ssl.get_peer_certificate()
            
            crypto_cert =cert.to_cryptography()
            # verifica si el servidor se ha vencido 
            if cert.has_expired():
                self.certificados_exp.append(self.get_common_name(crypto_cert))
            
            # Crear el diccionario con la fecha de vencimiento
            fecha = str(cert.get_notAfter())[2:10]
            if fecha in self.dic_hosts:
                self.dic_hosts[fecha].append(hostname)
            else :
                self.dic_hosts[fecha]= [hostname]
            
            sock_ssl.close()
            sock.close()
        except:
            print("Error ", hostname, port)
            return None

        return self.HostInfo(cert=crypto_cert, peername=peername, hostname=hostname)

    def get_alt_names(self, cert):
        try:
            ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            return ext.value.get_values_for_type(x509.DNSName)
        except x509.ExtensionNotFound:
            return None

    def get_common_name(self, cert):
        try:
            names = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
            return names[0].value
        except x509.ExtensionNotFound:
            return None

    def get_issuer(self, cert):
        try:
            names = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
            return names[0].value
        except x509.ExtensionNotFound:
            return None


    def print_basic_info(self, hostinfo):
        s = ''': {hostname} : ... {peername}
        \tcommonName: {commonname}
        \tSAN: {SAN}
        \tissuer: {issuer}
        \tnotBefore: {notbefore}
        \tnotAfter:  {notafter}
        '''.format(
                hostname=hostinfo.hostname,
                peername=hostinfo.peername,
                commonname=self.get_common_name(hostinfo.cert),
                SAN=self.get_alt_names(hostinfo.cert),
                issuer=self.get_issuer(hostinfo.cert),
                notbefore=hostinfo.cert.not_valid_before,
                notafter=hostinfo.cert.not_valid_after
        )
        return s
    def dic_basic_info(self, hostinfo):
        js = {}
        js['hostname']=hostinfo.hostname
        js['peername']=hostinfo.peername
        js['commonname']=self.get_common_name(hostinfo.cert)
        js['SAN']=self.get_alt_names(hostinfo.cert)
        js['issuer']=self.get_issuer(hostinfo.cert)
        js['notbefore']=hostinfo.cert.not_valid_before
        js['notafter']=hostinfo.cert.not_valid_after
        return js
    
    def slack_notification(self):
        # recorremos todos los dominios 
        for notAfter in self.dic_hosts:
            token =  "xoxb-228138875588-1026599970306-R3U91G42vXXGLukZYVqj3ZPG"
            x = datetime.datetime(int(notAfter[0:4]), int(notAfter[4:6]), int(notAfter[6:8]))            
            d = datetime.datetime.now()
            y = x - d
            if y.days <= 0:
                for cert in self.dic_hosts[notAfter]:
                    m = "\n Se ha vencido el certificado  del dominio\n "+cert
                    #m = 'curl -F token='+token+' -F channel=C010HHMV0B1 -F text=\"\n    '+m+'\n\" https://slack.com/api/chat.postMessage'
                    
                   # m = 'curl -F token=xoxb-228138875588-1026599970306-R3U91G42vXXGLukZYVqj3ZPG -F channel=C012V86D9AP -F text=\"\n Test  \n\" https://slack.com/api/chat.postMessage'
                    print(m)
                    m = 'curl -F token='+token+' -F channel=C012V86D9AP -F text=\"   '+m+' \" https://slack.com/api/chat.postMessage'

                    #os.system(m)
            elif y.days < 30:
                for cert in self.dic_hosts[notAfter]:
                    m = "En "+str(y.days)+"dias vencera el certificado del dominio:\n"+cert
                    #m = 'curl -F token='+token+' -F channel=C010HHMV0B1 -F text=\"\n    '+m+'\n\" https://slack.com/api/chat.postMessage'
                    print(m)
                    m = 'curl -F token='+token+' -F channel=C012V86D9AP -F text=\"   '+m+' \" https://slack.com/api/chat.postMessage'
                    #os.system(m)
    def dic_vencidos(self):
        # recorremos todos los dominios 
        list_cert = []
        for notAfter in self.dic_hosts:

            x = datetime.datetime(int(notAfter[0:4]), int(notAfter[4:6]), int(notAfter[6:8]))            
            y = x - datetime.datetime.now()
            if y.days <= 0:
                for hosts in self.dic_hosts[notAfter]:
                    cert = {}
                    cert['host']= hosts
                    cert['days']= str(y)
                    cert['estatus']='vencido'
                    list_cert.append(cert)

            elif y.days < self.days_before:
                for hosts in self.dic_hosts[notAfter]:
                    cert = {}
                    cert['host']= hosts
                    cert['days']= str(y)
                    cert['estatus']='renovacion' 
                    list_cert.append(cert)  
        return list_cert    

    def slack_expired_notification(self):
        token =  "xoxb-228138875588-1026599970306-R3U91G42vXXGLukZYVqj3ZPG"
        for expired in self.certificados_exp:
            #m = 'curl -F token='+token+' -F channel=C010HHMV0B1 -F text=\"ALERTA: El certicicado del dominio :\n'+expired+'\n ha expirado\" https://slack.com/api/chat.postMessage'
            #os.system(m)
            pass
    def check_it_out(self, hostname, port):
        hostinfo = self.get_certificate(hostname, port)
        self.print_basic_info(hostinfo)


    def main(self):
        list_cert  = []
        # recorre la lista de host
        for hostname in self.hosts:
            # Obtiene los certificados.
            host = self.hosts[hostname]
            if host['https']:
                certificate =  self.get_certificate(host['dns'],443)
                js = self.dic_basic_info(certificate)
                list_cert.append(js)
        return list_cert 
    def main_text(self):
        list_cert  = ''
        # recorre la lista de host
        for hostname in self.hosts:
            # Obtiene los certificados.
            host = self.hosts[hostname]
            if host['https']:
                certificate =  self.get_certificate(host['dns'],443)
                st = self.print_basic_info(certificate)
                list_cert = list_cert + st
        return list_cert  
        
if __name__ == "__main__":
    # Objeto y lectura de csv
    ssl = sslcheck()
    """
    ssl.main()
    ssl.slack_notification()
    d = datetime.datetime.now()
    print("se ha enviado correctamente la notificacion del dia "+str(d))
    """

