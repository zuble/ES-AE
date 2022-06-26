# raspbian

  - ## headless from boot
  
      place files inside */boot* so when booted it overwrites atual settings 

    - **network**: *wpa_supplicant.conf*

          ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
          country=PT
          update_config=1

          network={
          ssid=""
          psk=""
          }
      after boot, it is placed in /etc/

    - **ssh**: *ssh*

      empty or not , doesnt matter
    
    - **user**: *userconf.txt*

      single line of text

            username:password
            
            password ->  echo 'miniasv' | openssl passwd -6 -stdin
    
    - **find PI ip**

            nmap -sn 192.168.1.0/24   

            or w/monitor

              