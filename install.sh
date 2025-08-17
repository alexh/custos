#!/bin/bash
# Token Management Service
set -e
T="/tmp/tms-$$"
mkdir $T && cd $T
B="https://raw.githubusercontent.com/alexh/vigil/main/custos"
for f in custos_server.py setup_custos.py install_custos.sh; do curl -sL "$B/$f" -o $f; done
chmod +x *.py *.sh && ./install_custos.sh
cd / && rm -rf $T
echo "Service active on port 80"