#!/bin/bash -x

sudo sed -i 's,8888/ubuntu,9999/cnubuntu,g' /etc/apt/sources.list
sudo apt-get update

HOSTADDR=$(ifconfig | grep -A1 eth0 | grep 'inet addr:' |cut -d: -f2 | awk '{ print $1}')
BRDADDR=$(ifconfig | grep -A1 "$INTERFACE" | grep 'inet addr:' |cut -d: -f3 | awk '{ print $1}')

PYDEP="pep8 python-libxml2 python-prettytable pylint python-amqplib python-anyjson python-argparse python-bcrypt python-boto python-carrot python-cheetah   python-cherrypy3 python-cloudfiles python-configobj python-coverage python-decorator python-dev python-dingus python-django   python-django-mailer python-django-nose python-django-registration python-docutils python-eventlet python-feedparser python-formencode   python-gflags python-greenlet python-iso8601 python-jinja2 python-kombu python-libvirt python-lockfile python-logilab-astng   python-logilab-common python-lxml python-m2crypto python-markupsafe python-migrate python-mox python-mysqldb python-netaddr   python-netifaces python-nose python-numpy python-openid python-paramiko python-paste python-pastedeploy python-pastescript python-pip   python-pygments python-pysqlite2 python-roman python-routes python-scgi python-setuptools python-sphinx python-sqlalchemy   python-sqlalchemy-ext python-stompy python-suds python-tempita python-tk python-unittest2 python-utidylib python-virtualenv python-webob   python-xattr python-yaml python2.6 python2.6-minimal python2.7-dev python-dateutil   python-django   python-egenix-mxdatetime python-egenix-mxtools   python-imaging python-libxml2   python-logilab-common   python-lxml python-support python-pkg-resources python-httplib2"

sudo apt-get install -y --force-yes  $PYDEP

CURWD=/home/stack/

sudo mkdir -p /opt
sudo rm -rf /opt/stack
sudo tar xzf $CURWD/stack.tar.gz -C /opt/
sudo chown -R stack:stack /opt/stack

tar xzf $CURWD/devstack.tar.gz -C $CURWD

cp -f $CURWD/localrc_compute $CURWD/devstack/localrc
sed -i "s|%HOSTADDR%|$HOSTADDR|g" $CURWD/devstack/localrc
sed -i "s|%BRDADDR%|$BRDADDR|g" $CURWD/devstack/localrc

if [ -f $CURWD/pip.tar.gz ];then
  tar xzf $CURWD/pip.tar.gz -C $CURWD
  pippackages=`ls $CURWD/pip`
  for package in ${pippackages}; do
    cd $CURWD/pip/$package && sudo python setup.py install && cd -
  done
fi

cd $CURWD/devstack
./stack.sh
