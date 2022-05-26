# essential info/util

- https://raw.githubusercontent.com/wiki/LSTS/dune/Workshops/Workshop-2014-11-17.pdf

- https://autonaut.itk.ntnu.no/lib/exe/fetch.php?media=lsts_paper.pdf

- https://github.com/oysstu/imcpy



* * *


# [Neptus](https://github.com/LSTS/neptus) 

- Neptus is the command and control software used by human operators to interact with networked vehicle systems (Dias el al. 2006)). Neptus supports different phases of a mission’s life cycle: planning, simulation, execution, revision and dissemination (Pinto et al. (2006)). Concurrent multi-vehicle operation is possible through specialized graphical interfaces, which evolved through the years according to the requirements provided by end-users.

  - [Dias et al. 2006](https://ieeexplore.ieee.org/document/1642192)

  - [Pinto et al. (2006)](https://repositorio-aberto.up.pt/bitstream/10216/71611/2/65254.pdf)


0.     java log    

           (java 8 or 11)

1.     git clone https://github.com/LSTS/neptus.git && cd neptus && ./gradlew

            (...)
            Buildfile: /home/user/neptus/build.gradle
            Check the BUILD.md for details.
            (...)
            BUILD SUCCESSFUL in 1m 40s
            307 actionable tasks: 307 executed

2.     ./neptus


***
# [IMC](https://github.com/LSTS/imc) 

- The Inter-Module Communication (IMC) protocol, a message-oriented protocol designed and implemented for communication among heterogeneous vehicles, sensors and human operators. DUNE itself uses IMC for in-vehicle communication (Martins et al. (2009)).

  - [Martins et al. (2009)](https://www.dcc.fc.up.pt/~edrdo/publications/papers/oceans09.pdf)

  - [IMC-docs](https://www.lsts.pt/docs/imc/master/) 


* * *


# [DUNE](https://github.com/LSTS/dune) & [MINI-ASV](https://github.com/jorgef1299/Mini-ASV)
 

- DUNE: Unified Navigational Environment is the runtime environment for vehicle on-board software. It is used to write generic embedded software at the heart of the vehicle, e.g. code for control, navigation, communication,sensor and actuator access, etc. It provides an operating system and architecture independent platform abstraction layer, written in C++, enhancing portability among different CPU architectures and operating systems.


3.     mkdir dune && cd dune
4.     git clone https://github.com/LSTS/dune.git && git clone https://github.com/jorgef1299/Mini-ASV.git
5. change *dune/Mini-ASV* folder name to *private*
6.     cd .. && mkdir build
7. expected folder tree:

       dune/ [ build(empty) + dune(source)/private(mini-asv) ]

8.     cd build && cmake ../dune && make
            cmake : search for libraries
            make : compiles 

9. change *private/etc/mini-asv.ini*
        
        (all Require lines must be like this)
        [Require ../../etc/(.....)]
        [Require ../../etc/(.....)]
        ...
        [General]
        Vehicle  = caravela #mini-asv
        ...

10.     cd build && ./dune -c ../private/etc/mini-asv -p Simulation

            -c : path relative to dune/etc
            -p : Simulation or Hardware


***


# [GLUED](https://github.com/LSTS/glued)

*Lightweight Linux Distribution*: GLUED contains only the necessary packages to run on an embedded system, making it a light and fast distribution.

*Cross Compilation Ready* : Designed with cross compilation in mind, it is easy to get GLUED ready for your target system.

*Easy to Configure* : By editing simple text files and running short commands, you will be able to configure and cross compile GLUED for the target system.

*Compiled and Tested Against Many Platforms* : GLUED has been tested and compiled against Intel x86, Sun SPARC, ARM, PowerPC and MIPS.

  ***
  *everything below is done in personal machine*

11. ## get **GLUED** OS ready 4 pi 

    [Compile glued for a specific system/arch, our case rpi4](https://github.com/LSTS/glued/wiki/Compile-GLUED-for-a-system)

        git clone https://github.com/LSTS/glued.git
        cd glued && cd docker
        make && make shell DNS=8.8.4.4  (tried with quad9 , 9.9.9.9)

      generate system's configuration 
    
        ./mkconfig.bash test-rpi-eth0  : from .conf to .bash

            test-rpi-eth0.conf : 
              cfg_hostname='test-rpi'
              cfg_eth_ext_ip='10.0.200.52'
              cfg_services1=''
              cfg_packages='dropbear rsync busybox e2fsprogs dosfstools ptpd rpcbind 
                            rpi-boot-firmware linux/rpi exiftool libusb'
              cfg_services0='network dropbear storage upgrade syslog ptpd'
              cfg_modules="$cfg_modules ftdi_sio"
              cfg_terminal='tty1'
              cfg_ptpd_interface='eth0'
      
      compile packages & chill

        ./mksystem.bash lctr-rpi/test-rpi-eth0.bash
      
      generate rootfs 

        ./pkrootfs.bash lctr-rpi/test-rpi-eth0.bash   : from bash to .tar.bz2

    now you have a compatible glued OS for the pi
  
    ***

12. ## flash GLUED 2 **SD card**
      
        ./mkdisk.bash lctr-rpi/test-rpi-eth0.bash /dev/sdb   
        
      we changed root0/etc/config  (sudo chmod 644 config)
        
        before
          cfg_eth_ext_gw=10.0.0.1
          cfg_eth_ext_ip=10.0.200.52
          cfg_eth_ext_mk=255.255.0.0
        after
          cfg_eth_ext_gw=192.168.1.254
          cfg_eth_ext_ip=192.168.1.5
          cfg_eth_ext_mk=255.255.255.0

    ***

  13. ## get **DUNE** ready 4 pi

      by indicating the respective compilers of our system at

      /glued/lctr-rpi/toolchain/bin/armv7-lsts-linux-gnueabihf- 
    
      DUNE is cross-compiled

          cd dune/build
          cmake ../dune -DCROSS=/home/engsolar/infernoup/ES/glued/lctr-rpi/toolchain/bin/armv7-lsts-linux-gnueabihf-
          make package -j8

      *dune-2022.04.0-armv7-32bit-linux-glibc-gcc4x.tar.bz2* generated
      
      **this tar goes into /opt/lsts/**
    
***
  
# raspbian

  - ## headless from boot
  
      place files inside */boot* so when booted it overwrites atual settings 

    - **network**: *wpa_supplicant.conf*

          ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
          country=PT
          update_config=1

          network={
          ssid="fodafone"
          psk="f1"
          }
      after boot is placed in /etc/

          nmap -sn 192.168.1.0/24    : scan networks

    - **ssh**: *ssh*

      empty or not , doesnt matter
    
    - **user**: *userconf.txt*

      single line of text

            username:password
            
            password ->  echo 'mypassword' | openssl passwd -6 -stdin
    
    ***

  - ## w/ monitor

        sudo rapi-config          
  
***

# [nav1.mp4](https://send.vis.ee/download/4ca61c7c116eefb3/#AljB3xMDsp8WCmRkZxjPkQ)

- 00:00 neptus
- 05:00 imc autonomamente: [imcpy](https://github.com/oysstu/imcpy) / sh / neptus plugin em java
- 07:30 dune definition
- 08:00 toolchain overview
- 16:30 mini-asv HW
  - [MPU9250](https://invensense.tdk.com/wp-content/uploads/2015/02/PS-MPU-9250A-01-v1.1.pdf) : [wiki IMU](https://en.wikipedia.org/wiki/Inertial_measurement_unit)
  - [QMC5883L](https://www.filipeflop.com/img/files/download/Datasheet-QMC5883L-1.0%20.pdf) 
  - RPI4 : [datasheet](https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-datasheet.pdf) & [documentation](https://www.raspberrypi.com/documentation/computers/)
- 18:40 imc messages overview 
- 20:46 imc communication in code@mini-asv
- 24:05 
    - set gps start position inside neptus without modify (...).ini
    - 24:50 flash glues os rpi4@caravela + check if "mini-asv" appears in neptus / http:10.0.10.40:8080 @ caravela ip-port

- ## plano
    1. fazer passos 11 e 12 ( glued )
    2. configurar/verificar ligacao com neptus/ip-port

***
# SD files original
  
  - [*pi.zip*](https://send.vis.ee/download/dbfa6fb7d60bf84a/#IU361zq4tGEGbS6KJOJrKw) : home folder ( bando de opencv ) 
  
  - [*miniasv-sd-orig.img.gz*](https://send.vis.ee/download/1ae4b783e9ff5c56/#4lSzAGuY8ck_7esYGQxGjQ)  : shrinked + compressed sd card ( boot + rootfs )
      
      1. to restore into original shrinked state .img (11gb) aka uncompress

        sudo gunzip miniasv-sd-orig2.img.gz    ~ deletes the .gz file afterwards
        sudo gzip -dk miniasv-sd-orig2.img.gz  ~ keeps it
      
      2. to double click miniasv-sd-orig.img to mount in your system aka get acess to the files
 
