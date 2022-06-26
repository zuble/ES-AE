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

9. change *private/etc/mini-asv.ini* into
        
        (all Require lines must be like this)
        [Require ../../etc/(.....)]
        [Require ../../etc/(.....)]
        ...
        [General]
        Vehicle  = caravela #mini-asv
        ...

      
10.     mv mini-asv.ini dune/etc/

11.     cd build && ./dune -c mini-asv -p Simulation

            -c : path relative to dune/etc
            -p : Simulation or Hardware


***


# [GLUED](https://github.com/LSTS/glued)

  ***
  *everything below is done in personal machine*

11. ## get pi4 compilers

    [Compile glued for a specific system/arch](https://github.com/LSTS/glued/wiki/Compile-GLUED-for-a-system)

        git clone https://github.com/LSTS/glued.git
        cd glued && cd docker
        make && make shell DNS=8.8.4.4  (tried with quad9 , 9.9.9.9)

      generate system's configuration from git branch feature/new-master
    
        ./mkconfig.bash rpi4-template : from .conf to .bash
    
      compile packages & chill

        ./mksystem.bash lctr-rpi4/rpi4-template
      
      located at */glued/lctr-rpi4/toolchain/bin/*

    ***

12. ### GLUED 2 **SD card**

      generate rootfs 

        ./pkrootfs.bash lctr-rpi4/rpi4-template.bash   : from bash to .tar.bz2
      
      flash it 

        ./mkdisk.bash lctr-rpi4/test-rpi-eth0.bash /dev/sdb   

    ***

13. ## get **DUNE** cross compiled to rpi
  
          cd dune/build
          cmake ../dune -DCROSS=/home/engsolar/es/glued/lctr-rpi4/toolchain/bin/armv7-lsts-linux-gnueabihf-
          make package -j8  :uses 8 cores to get tar.bz2

      *dune-2022.04.0-armv7-32bit-linux-glibc-gcc4x.tar.bz2* generated
      
      **this tar goes into /opt/lsts/**

      or its possible to compile inside pi following the 3-10 steps.

  14. ## START **DUNE**

          cd /opt/lsts/dune/build/ && sudo su
          ./dune -c mini-asv -p Hardware
  
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

***
# SD files original
  
  - [*pi.zip*](https://send.vis.ee/download/dbfa6fb7d60bf84a/#IU361zq4tGEGbS6KJOJrKw) : home folder ( bando de opencv ) 
  
  - [*miniasv-sd-orig.img.gz*](https://send.vis.ee/download/1ae4b783e9ff5c56/#4lSzAGuY8ck_7esYGQxGjQ)  : shrinked + compressed sd card ( boot + rootfs )
      
      1. to restore into original shrinked state .img (11gb) aka uncompress

        sudo gunzip miniasv-sd-orig2.img.gz    ~ deletes the .gz file afterwards
        sudo gzip -dk miniasv-sd-orig2.img.gz  ~ keeps it
        
        sudo tar -xvjf foo.tar.bz2             ~ extract and umcompress

      2. to double click miniasv-sd-orig.img to mount in your system aka get acess to the files
 
***

# to do

  - lighten current sd size 
    - criar raspbian headless 32b + flashar com config miniasv+p30
    - scp /es/dune/build/dune.tar.bz2 para pi OR simple sudo su && cp ...

  - IMC 
    - read (plan supervision + maneuvering) messages
      https://www.lsts.pt/docs/imc/master/ 
    
  
***

    sudo nano ~/.bashrc
    alias cddunebuild="sudo su && cd /opt/lsts"
    exec bash

***

# essential info/util

- https://raw.githubusercontent.com/wiki/LSTS/dune/Workshops/Workshop-2014-11-17.pdf

- https://autonaut.itk.ntnu.no/lib/exe/fetch.php?media=lsts_paper.pdf

- https://github.com/oysstu/imcpy

