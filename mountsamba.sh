# sudo apt install cifs-utils
# run as sudo
mkdir -p images
sudo mount -t cifs //192.168.2.1/gl-samba ./images -o guest,vers=1.0
