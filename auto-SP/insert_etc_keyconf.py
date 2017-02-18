import sys, fileinput, re

def modify_sp_keyconf():  
    fh=fileinput.input('/etc/keystone/keystone.conf',inplace=True)  
    for line in fh:  
        repl_auth=line + 'methods = external,password,token,oauth1,saml2' + '\n' + 'saml2 = keystone.auth.plugins.mapped.Mapped'  
        line=re.sub('\[auth\]', repl_auth, line)  
        sys.stdout.write(line) 
    fh.close()  

modify_sp_keyconf()

