#! /bin/sh

USER_ID=$(grep "USER ID" /home/ubuntu/admin | awk -F' = ' '{print $2}')
PROJECT_ID=$(grep "Tenant ID" /home/ubuntu/admin | awk -F' = ' '{print $2}')

sed -i "/USER ID/a export OS_USER_ID=${USER_ID}" /home/ubuntu/admin
sed -i "/Tenant ID/a export OS_PROJECT_ID=${PROJECT_ID}" /home/ubuntu/admin
sed -i -e 's/v2.0/v3/g' /home/ubuntu/admin

