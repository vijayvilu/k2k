import sys, fileinput, re

def modify_novaconf():  
    keystone_section = "[keystone_authtoken]"
    cinder_section = "[cinder]"
    search_text = "auth_uri"
    repl_text = ""
    found_keystone = False
    fh=fileinput.input('/etc/nova/nova.conf',inplace=True)  
    for line in fh:  
        if keystone_section in line:
            found_keystone = True

        if search_text in line and found_keystone: 
            repl_text = line
        
        if repl_text != "":
            if cinder_section in line:
                line = line + repl_text
        sys.stdout.write(line) 
    fh.close()  

modify_novaconf()
