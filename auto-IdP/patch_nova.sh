# modify nova codebase
cd /opt/stack/nova
echo "adding moc remote repo"
git remote add moc git://github.com/CCI-MOC/nova
echo "fetch moc repo"
git fetch moc
echo "checkout moc-modified kilo branch"
git checkout moc/moc-modified

# modify python-novaclient
echo "clone the moc python-novaclient repo"
cd ~ && git clone https://github.com/CCI-MOC/python-novaclient.git
echo "uninstall original python-novaclient"
sudo pip uninstall -y python-novaclient
echo "install the modified python-novaclient"
cd python-novaclient && sudo python setup.py install

# modify nova.conf
echo "modify nova.conf"
cd /home/ubuntu/IdP && python modify_novaconf.py

# restart nova-api and nova-cpu
echo "restart keystone-api, nova-api, nova-cpu"
screen -p 2 -X stuff "^C^[OA\n" 
screen -p 7 -X stuff "^C^[OA\n" 
screen -p 13 -X stuff "^C^[OA\n" 
