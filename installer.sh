#!/bin/bash

# Menyalin direktori ke /usr/local/bin/
sudo cp -r markaswalet-stream /usr/local/bin/

# Menyalin file service ke /etc/systemd/system/
sudo cp markaswalet-stream.service /etc/systemd/system/

# Menginformasikan pengguna
echo "File dan direktori telah berhasil disalin."
echo "Enabling service"
sleep 2
sudo systemctl enable markaswalet-stream.service
sudo systemctl daemon-reload
echo "Starting service"
sleep 2
# sudo systemctl start markaswalet-stream.service
echo "Markaswalet - Techiro :: Installed :: Jangan Lupa untuk di start service nya"
