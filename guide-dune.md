# dune + mini-asv

https://github.com/LSTS/dune
https://github.com/jorgef1299/Mini-ASV


1.      mkdir dune && cd dune && git clone https://github.com/LSTS/dune.git
2.      cd .. && git clone https://github.com/jorgef1299/Mini-ASV.git
3. name *Mini-ASV* folder to *private*
4. mkdir dune/build
5. folder tree:

        dune/ [ private(mini-asv) + build(empty) + dune(source) ]

6. copy *dune/private/etc/mini-asv.ini* to *dune/dune/etc/*
7. change *mini-asv.ini*
        
        ...
        [General]
        Vehicle  = caravela #mini-asv
        ...

8.      cd build && cmake ../dune && make
            cmake : search for libraries
            make : compiles


# neptus

https://github.com/LSTS/neptus

0.      java log    
            java 8 or 11

1.      git clone https://github.com/LSTS/neptus.git && cd neptus && ./gradlew

            (...)
            Buildfile: /home/user/neptus/build.gradle
            Check the BUILD.md for details.
            (...)
            BUILD SUCCESSFUL in 1m 40s
            307 actionable tasks: 307 executed

2.      ./neptus


# dune

10.     cd build && ./dune -c mini-asv -p Simulation



