import sys, fileinput, re
idp_ip = sys.argv[1]

def modify_sp_keyconf(idp_ip):  
    fh=fileinput.input('/etc/keystone/keystone.conf',inplace=True)  
    for line in fh:  
        repl_saml=line + 'certfile=/etc/keystone/ssl/certs/ca.pem\n' + 'keyfile=/etc/keystone/ssl/private/cakey.pem\n' + 'idp_entity_id=http://' + idp_ip + ':5000/v3/OS-FEDERATION/saml2/idp\n' + 'idp_sso_endpoint=http://' + idp_ip + ':5000/v3/OS-FEDERATION/saml2/sso\n' + 'idp_metadata_path=/etc/keystone/keystone_idp_metadata.xml'
        line=re.sub('\[saml\]', repl_saml, line)
        sys.stdout.write(line) 
    fh.close()  

modify_sp_keyconf(idp_ip)

