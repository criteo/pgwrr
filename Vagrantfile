#!/usr/bin/env ruby
# ^syntax detection

Vagrant.configure(2) do |config|
  config.vm.box = 'bento/centos-6.7'
  config.vm.provision 'shell', inline: <<-SHELL
    wget http://dl.marmotte.net/rpms/redhat/el6/x86_64/libmaxminddb-1.0.4-1.el6/libmaxminddb-1.0.4-1.el6.x86_64.rpm
    wget http://dl.marmotte.net/rpms/redhat/el6/x86_64/libmaxminddb-1.0.4-1.el6/libmaxminddb-devel-1.0.4-1.el6.x86_64.rpm
    wget http://dl.marmotte.net/rpms/redhat/el6/x86_64/python-maxminddb-1.2.0-2.el6/python-maxminddb-1.2.0-2.el6.x86_64.rpm
    wget http://dl.marmotte.net/rpms/redhat/el6/x86_64/python-geoip2-2.1.0-1.el6/python-geoip2-2.1.0-1.el6.x86_64.rpm
    sudo yum -y localinstall *
    cp -r /vagrant project
    cd project
    sudo yum -y install python-setuptools rpm-build
    python setup.py bdist --format=rpm
    sudo yum -y localinstall dist/*.noarch.rpm
  SHELL
end
