#!/bin/bash -x

#source ./imroot
set -e
function trackme 
{
    #echo "$@" >> ./$$.cmd.log
    $@
    local EXIT_CODE=$?
    return $EXIT_CODE
}

if [ $# == 0 ]; then
  echo "you must tell me which nic you use: $0 eth0 or $0 wlan0"
  exit -1
fi

export INTERFACE=$1
source ./addrc

echo ${HOSTADDR:?"empty host addr"}
echo ${MASKADDR:?"empty mask addr"}
echo ${GATEWAY:?"empty gateway"}
echo ${NETWORK:?"empty network"}

export X7WORKDIR=`pwd`
CONFDIR=$X7WORKDIR/conf
CURWD=$X7WORKDIR
MYID=`whoami`

# ntp server
sudo apt-get install -y ntp
grep "server 127.127.1.0" /etc/ntp.conf > /dev/null && true
if [ "$?" -ne "0" ]; then
  sudo sed -i 's/server ntp.ubuntu.com/serverntp.ubuntu.com\nserver 127.127.1.0\nfudge 127.127.1.0 stratum 10/g' /etc/ntp.conf
fi
sudo service ntp restart

# prepare for pxe installation
sudo apt-get install -y --assume-yes fai-quickstart

# dhcp config
cp -f $CONFDIR/etc/dhcp/dhcpd.conf.template $CONFDIR/etc/dhcp/dhcpd.conf
sed -i "s|%NETADDR%|$NETWORK|g" $CONFDIR/etc/dhcp/dhcpd.conf
sed -i "s|%MASKADDR%|$MASKADDR|g" $CONFDIR/etc/dhcp/dhcpd.conf
sed -i "s|%GATEWAY%|$GATEWAY|g" $CONFDIR/etc/dhcp/dhcpd.conf
sed -i "s|%HOSTADDR%|$HOSTADDR|g" $CONFDIR/etc/dhcp/dhcpd.conf
sudo cp -f $CONFDIR/etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf
sudo /etc/init.d/isc-dhcp-server restart


# dns setup/config

# tftp config
cp -f $CONFDIR/etc/default/tftpd-hpa.template  $CONFDIR/etc/default/tftpd-hpa
sudo cp -f $CONFDIR/etc/default/tftpd-hpa /etc/default/tftpd-hpa
sudo /etc/init.d/tftpd-hpa restart

cp -f $CONFDIR/srv/tftp/vai/ubuntu-installer/amd64/boot-screens/txt.cfg.template $CONFDIR/srv/tftp/vai/ubuntu-installer/amd64/boot-screens/txt.cfg
sed -i "s|%HOSTADDR%|$HOSTADDR|g" $CONFDIR/srv/tftp/vai/ubuntu-installer/amd64/boot-screens/txt.cfg
sudo cp -rf $CONFDIR/srv/tftp/vai /srv/tftp/

# preseed
cp -f $CURWD/www/preseed.cfg.template $CURWD/www/preseed.cfg
sed -i "s|%HOSTADDR%|$HOSTADDR|g" $CURWD/www/preseed.cfg


# hosts config
cp $CONFDIR/etc/hosts.template $CONFDIR/etc/hosts
sed -i "s|%HOSTADDR%|$HOSTADDR|g" $CONFDIR/etc/hosts
sed -i "s|%HOSTNAME%|$HOSTNAME|g" $CONFDIR/etc/hosts

# nfs path prepare
sudo mkdir -p /srv/instances
sudo chmod 777 /srv/instances
grep "/srv/instances $HOSTADDR/24" /etc/exports > /dev/null  && true
if [ "$?" -ne "0" ]; then
    echo "/srv/instances $HOSTADDR/24(async,rw,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports > /dev/null
    echo "/srv/instances 127.0.0.1(async,rw,no_subtree_check,no_root_squash)" | sudo tee -a  /etc/exports > /dev/null
else
    echo ""
fi
sudo /etc/init.d/nfs-kernel-server restart

mkdir -p $CURWD/www/ubuntu/
if [ -f $CURWD/ubuntu-11.10-alternate-amd64.iso ]; then
  sudo mount -o loop $CURWD/ubuntu-11.10-alternate-amd64.iso $CURWD/www/ubuntu/
else
  echo "please manually mount ubuntu 11.10 alternate image to $CURWD/www/ubuntu/ firsy if you want to net-install compute node"
fi

cd $CURWD/www/
python -m SimpleHTTPServer 8888 &

#devstack & openstack packages
mkdir -p $CURWD/cache
if [ ! -f $CURWD/cache/devstack.tar.gz ]; then
  wget https://github.com/downloads/zz7a5pe4/x7_start/devstack.tar.gz -O $CURWD/cache/devstack.tar.gz
fi
rm -rf $CURWD/devstack
tar xzf $CURWD/cache/devstack.tar.gz -C $CURWD/
#wget https://github.com/downloads/zz7a5pe4/x7_start/stack.tar.gz -O $CURWD/cache/stack.tar.gz


if [ ! -d  $CURWD/stack ]; then
  git clone git://github.com/zz7a5pe4/x7_dep.git $CURWD/stack
  rm -f $CURWD/cache/stack.tar.gz
  cd $CURWD
  tar czf $CURWD/cache/stack.tar.gz --exclude .git stack
fi
sudo rm -rf /opt/stack
sudo cp -rf $CURWD/stack /opt
sudo chown -R $MYID:$MYID /opt/stack
cd /opt/stack/x7_dashboard 
sudo python setup.py develop

# clone x7 stack from github
#git clone git://github.com/zz7a5pe4/x7.git || true 
#cd x7
#git fetch git://github.com/zz7a5pe4/x7.git demo_mig
#git checkout demo_mig
#cd ..
# clone x7 fai from github
#git clone git://github.com/zz7a5pe4/x7_fai.git || true

# create id_rsa for current user
#rm -f ~/.ssh/id_rsa || true
#ssh-keygen -P "" -f ~/.ssh/id_rsa || true
#eval `ssh-agent` 
#ssh-add   ~/.ssh/id_rsa

# cache for server/client installation
PACKAGES="apache2 apache2-mpm-worker apache2-utils apache2.2-bin apache2.2-common blt bridge-utils cloud-utils cpu-checker curl dnsmasq-utils   ebtables erlang-asn1 erlang-base erlang-corba erlang-crypto erlang-dev erlang-docbuilder erlang-edoc erlang-erl-docgen erlang-eunit   erlang-ic erlang-inets erlang-inviso erlang-mnesia erlang-nox erlang-odbc erlang-os-mon erlang-parsetools erlang-percept erlang-public-key   erlang-runtime-tools erlang-snmp erlang-ssh erlang-ssl erlang-syntax-tools erlang-tools erlang-webtool erlang-xmerl euca2ools gawk   git-core javascript-common kpartx kvm libaio1 libapache2-mod-wsgi libapparmor1 libapr1 libaprutil1 libaprutil1-dbd-sqlite3   libaprutil1-ldap libblas3gf libconfig-general-perl libcurl3 libdbd-mysql-perl libdbi-perl libexpat1-dev libgfortran3 libhtml-template-perl   libibverbs1 libjs-jquery-metadata libjs-jquery-tablesorter libjs-sphinxdoc libjs-underscore liblapack3gf libldap2-dev libnet-daemon-perl   libplrpc-perl libpython2.6 librdmacm1 libreadline5 libruby1.8 libsasl2-dev libsctp1 libsigsegv2 libssl-dev libssl-doc libtidy-0.99-0   libvirt-bin libvirt0 libxenstore3.0 libxml2-utils libxss1 libyaml-0-2 lksctp-tools locate lvm2 memcached msr-tools mysql-client-5.1   mysql-client-core-5.1 mysql-server mysql-server-5.1 mysql-server-core-5.1 odbcinst odbcinst1debian2 open-iscsi open-iscsi-utils   openssh-server  qemu-common qemu-kvm rabbitmq-server screen seabios sg3-utils socat   sqlite3 ssh-import-id tcl8.5 tgt tk8.5 unixodbc vgabios vim-nox vim-runtime vlan watershed wwwconfig-common xfsprogs zlib1g-dev build-essential dpkg-dev fakeroot g++ g++-4.6 libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libdpkg-perl libstdc++6-4.6-dev libtimedate-perl libldap-2.4-2 libssl1.0.0  dnsmasq-base git-core iputils-arping   libasound2 libasyncns0 libdevmapper-event1.02.1   libflac8   libfontenc1   libgl1-mesa-dri   libgl1-mesa-glx libglapi-mesa   libibverbs1   libice6 libjpeg62 libjson0 liblcms1   libldap2-dev   libllvm2.9   liblua5.1-0   libmysqlclient16   libogg0 libpaper-utils libpaper1 libperl5.12   libpulse0 libsdl1.2debian   libsdl1.2debian-alsa   libsgutils2-2 libsm6   libsndfile1   libsysfs2 libtidy-0.99-0   libutempter0   libvorbis0a   libvorbisenc2   libxaw7   libxcb-shape0   libxcomposite1 libxdamage1   libxfixes3 libxft2 libxi6   libxinerama1   libxmu6   libxpm4   libxslt1.1   libxt6   libxtst6   libxv1   libxxf86dga1 libxxf86vm1 msr-tools   mysql-common  unzip x11-common   x11-utils   xbitmaps   xterm libltdl7 libcap2 libavahi-client3 libavahi-common3 libavahi-common-data git git-man liberror-perl binutils build-essential cpp cpp-4.6 dpkg-dev fakeroot g++ g++-4.6 gcc gcc-4.6 libalgorithm-diff-perl libalgorithm-diff-xs-perl libalgorithm-merge-perl libc-dev-bin libc6-dev libdpkg-perl libgomp1 libmpc2 libmpfr4 libquadmath0 libstdc++6-4.6-dev linux-libc-dev make manpages-dev libc-bin libc6 "

PYDEP="pep8 python-libxml2 python-prettytable pylint python-amqplib python-anyjson python-argparse python-bcrypt python-boto python-carrot python-cheetah   python-cherrypy3 python-cloudfiles python-configobj python-coverage python-decorator python-dev python-dingus python-django   python-django-mailer python-django-nose python-django-registration python-docutils python-eventlet python-feedparser python-formencode   python-gflags python-greenlet python-iso8601 python-jinja2 python-kombu python-libvirt python-lockfile python-logilab-astng   python-logilab-common python-lxml python-m2crypto python-markupsafe python-migrate python-mox python-mysqldb python-netaddr   python-netifaces python-nose python-numpy python-openid python-paramiko python-paste python-pastedeploy python-pastescript python-pip   python-pygments python-pysqlite2 python-roman python-routes python-scgi python-setuptools python-sphinx python-sqlalchemy   python-sqlalchemy-ext python-stompy python-suds python-tempita python-tk python-unittest2 python-utidylib python-virtualenv python-webob   python-xattr python-yaml python2.6 python2.6-minimal python2.7-dev python-dateutil   python-django   python-egenix-mxdatetime python-egenix-mxtools   python-imaging python-libxml2   python-logilab-common   python-lxml python-support python-pkg-resources python-httplib2"

mkdir -p $CURWD/cache/apt
mkdir -p $CURWD/cache/img
mkdir -p $CURWD/cache/pip

# apt deb
cd $CURWD/cache/apt
apt-get download $PACKAGES
sudo apt-get install --force-yes -y $PYDEP

# image and pip
if [ -d /media/x7_usb/ ]; then
  cp /media/x7_usb/x7_cache/cirros-0.3.0-x86_64-uec.tar.gz $CURWD/cache/img/cirros-0.3.0-x86_64-uec.tar.gz
  tar xzf /media/x7_usb/x7_cache/pika-0.9.5.tar.gz -C $CURWD/cache/pip/
  tar xzf /media/x7_usb/x7_cache/passlib-1.5.3.tar.gz -C $CURWD/cache/pip/
  tar xzf /media/x7_usb/x7_cache/django-nose-selenium-0.7.3.tar.gz -C $CURWD/cache/pip/
else
  #[ -f $CURWD/cache/img/cirros-0.3.0-x86_64-uec.tar.gz ] || wget http://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-uec.tar.gz -O $CURWD/cache/img/cirros-0.3.0-x86_64-uec.tar.gz
  [ -f $CURWD/cache/pip/pika-0.9.5.tar.gz ] || wget https://github.com/downloads/jkerng/x7/pika-0.9.5.tar.gz -O $CURWD/cache/pip/pika-0.9.5.tar.gz
  [ -f $CURWD/cache/pip/passlib-1.5.3.tar.gz ] || wget https://github.com/downloads/jkerng/x7/passlib-1.5.3.tar.gz -O $CURWD/cache/pip/passlib-1.5.3.tar.gz
  [ -f $CURWD/cache/pip/django-nose-selenium-0.7.3.tar.gz ] || wget https://github.com/downloads/jkerng/x7/django-nose-selenium-0.7.3.tar.gz -O $CURWD/cache/pip/django-nose-selenium-0.7.3.tar.gz
  [ -f $CURWD/cache/pip/pam-0.1.4.tar.gz ] || wget https://github.com/downloads/jkerng/x7/pam-0.1.4.tar.gz -O $CURWD/cache/pip/pam-0.1.4.tar.gz
  [ -f $CURWD/cache/pip/pycrypto-2.3.tar.gz ] || wget https://github.com/downloads/jkerng/x7/pycrypto-2.3.tar.gz -O $CURWD/cache/pip/pycrypto-2.3.tar.gz
fi

tar xzf $CURWD/cache/pip/pika-0.9.5.tar.gz -C $CURWD/cache/pip/
tar xzf $CURWD/cache/pip/passlib-1.5.3.tar.gz -C $CURWD/cache/pip/
tar xzf $CURWD/cache/pip/django-nose-selenium-0.7.3.tar.gz -C $CURWD/cache/pip/
tar xzf $CURWD/cache/pip/pam-0.1.4.tar.gz -C $CURWD/cache/pip/
tar xzf $CURWD/cache/pip/pycrypto-2.3.tar.gz -C $CURWD/cache/pip/
chmod -R +r $CURWD/cache/pip || true


if [ -d $CURWD/cache/pip ];then
  pippackages=`ls $CURWD/cache/pip`
  for package in ${pippackages}; do
    cd $CURWD/cache/pip/$package && sudo python setup.py install
    echo "$CURWD/cache/pip/$package"
  done
fi

cd $CURWD/cache 
tar czf $CURWD/cache/pip.tar.gz --exclude "*.tar.gz" pip


mkdir -p $CURWD/log/
cp -f $CURWD/localrc_server_template $CURWD/devstack/localrc

cd $CURWD/devstack
sed -i "s|%HOSTADDR%|$HOSTADDR|g" localrc
sed -i "s|%INTERFACE%|$INTERFACE|g" localrc
sed -i "s|%BRDADDR%|$BRDADDR|g" localrc

grep "add_nova_opt \"logdir=$CURWD/log\"" stack.sh > /dev/null && true
# "0" => found
if [ "$?" -ne "0" ]; then
  sed -i "s,add_nova_opt \"verbose=True\",add_nova_opt \"verbose=True\"\nadd_nova_opt \"logdir=$CURWD/log\",g" stack.sh
fi
./stack.sh
sudo mount -t nfs 127.0.0.1:/srv/instances /opt/stack/nova/instances
cp -f $CURWD/localrc_compute_template $CURWD/localrc_compute
sed -i "s|%SERVERADDR%|$HOSTADDR|g" $CURWD/localrc_compute

exit 0
