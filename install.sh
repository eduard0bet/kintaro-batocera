#!/bin/bash
#                                      ▄▄= _╓_
#                                    ╓██▄▓██████▄_
#                                   j██████████████▄
#                                   ╫████████████▀"
#                                   ╫█████████╙
#                                 ,▄▓███████▓,
#                               ▄██████████████▄
#                              ª▀▀▀▀▀▀▀▀▀▀▀▀████H
#                         _,▄▄▓▓██████████▓▓████Ñ
#                     ,▄██████████████████████████▓▄_
#                  _▄█████████████████████████████████▄_
#                 ▄██████████████████████████████████████╓
#               ╓█████████████^╟██████████████████████████▓_
#              ╔█████████████  ▓████████████████████████████▄
#             ╔█████▀▀▀╙╙""`   ````""╙╙▀▀▀████████████╕'█████▄
#            ╓███,▄▄H                        └╙▀███████_▐█████╕
#            ██████▌  ▄▓▀▀▄╓          _╓▄▄▄▄╖_    ╙╙███▌ ██████_
#           ╫█████▌  ²╙  _ ╙▀       ▓▀╙"    '█H      _╙Ñ ▓█████▓
#          ▐██████      ▓██_ ,,        ▄█▌_  ``      ╟█▄|███████▒
#          ██████Ñ      `╙^_█╙╙▀▓▄    '███`          ╚███████████╕
#         ╟██████          `"    `                   [████████████
#        ╓██████▌     ▄▄▓█▓▀▀▀▀▀▀▓φ▄▄,_              [█████████████
#        ▓██████▌      ╟███▄╓,_____,,╠███▓▄▄▄        j██████████████
#       ║███████▌      '█████████████████▓           ▐███████████████╖
#      ╓█████████_      `████╙"]█▀╙"'╙██╜            ║█████████████████▄
#      ███████████_       ╙▓▄╓,╙`_,▄▓▀^              ╫█████████████```
#     ▓████████████_         '╙╙╙╙"                 _██████████████▌
#   _▓██████████████▄_     ª█      ,▄@            _▄████████████████H
#  »▓█████▀▀▀▀▀███████▌,    ╙▀▓▓▓▀▀╙`          _▄▓▀`╫████████▀╙▀▀▀▀██_
#              ╚█████▀╙╙▀▓▄,__           _,,▄▓▀▀"  ,██████▀"
# Copyright 2016 Kintaro Co.                                                                                                                                                     
# Copyright 2025 Eduardo Betancourt
# Kintaro Controller service script for batocera

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Kintaro Controller Installation for Batocera...${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root${NC}"
    echo "Try: sudo $0"
    exit 1
fi

# Check if it's a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo -e "${RED}This script only works on Raspberry Pi${NC}"
    exit 1
fi

# Create temporary directory
TMP_DIR=$(mktemp -d)
cd $TMP_DIR

# Download files
echo "Downloading files..."
curl -sSL https://raw.githubusercontent.com/eduard0bet/kintaro-batocera/refs/heads/main/kintaro.py -o kintaro.py
curl -sSL https://raw.githubusercontent.com/eduard0bet/kintaro-batocera/refs/heads/main/S31kintaro -o S31kintaro

if [ ! -f kintaro.py ] || [ ! -f S31kintaro ]; then
    echo -e "${RED}Error downloading files${NC}"
    exit 1
fi

# Create directory structure (Batocera-specific)
echo "Creating directories..."
mkdir -p /userdata/system/kintaro
mkdir -p /userdata/system/custom.sh.d

# Copy files (Batocera paths)
echo "Copying files..."
cp -f kintaro.py /userdata/system/kintaro/
cp -f S31kintaro /userdata/system/custom.sh.d/

# Set permissions
echo "Setting permissions..."
chmod 755 /userdata/system/kintaro/kintaro.py
chmod 755 /userdata/system/custom.sh.d/S31kintaro

# Configure autostart by adding to custom.sh
echo "Setting up autostart..."
if [ ! -f /userdata/system/custom.sh ]; then
    echo '#!/bin/bash' > /userdata/system/custom.sh
    chmod +x /userdata/system/custom.sh
fi

# Add our script to custom.sh if not already there
if ! grep -q "S31kintaro start" /userdata/system/custom.sh; then
    echo '/userdata/system/custom.sh.d/S31kintaro start' >> /userdata/system/custom.sh
    echo "Autostart configured"
else
    echo "Autostart already configured"
fi

# Clean temporary directory
echo "Cleaning temporary files..."
cd /
rm -rf $TMP_DIR

# Verify installation
if [ -f /userdata/system/kintaro/kintaro.py ] && [ -f /userdata/system/custom.sh.d/S31kintaro ]; then
    echo -e "${GREEN}                                                                      ${NC}"
    echo -e "${GREEN}    ░▒▒▒░      ░░░░░                                                  ${NC}"
    echo -e "${GREEN}    ░███▒     ░▒███░░           ░░░░                                  ${NC}"
    echo -e "${GREEN}    ░███▒      ░░▒░░            ▓██░                                  ${NC}"
    echo -e "${GREEN}    ░███▒░▒███░▒██▓░░████████▒░██████▒░▓██████░░ ███▓██░░▓█████▓░░    ${NC}"
    echo -e "${GREEN}    ░███▒███▒░ ▒██▓░░███▒░▒███░░▓██▒░░░░▒░░░▓██░░████▒░▒███░░▒███▒░   ${NC}"
    echo -e "${GREEN}    ░██████▓░░ ▒██▓░░███░ ░███░ ▓██░ ░░▓███████▒░███░  ▓██▒░ ░▒██▒░   ${NC}"
    echo -e "${GREEN}    ░███▒▓███░ ▒██▓░░███░ ░███░ ▒██▓░░███░░░███▒░███░  ▒███▒░▓███░░   ${NC}"
    echo -e "${GREEN}    ░▓██░░░███▒▒██▓░░███░ ░▓██░ ░▓███▒░▓███▓▓██▒░███░   ░▒█████▒░░    ${NC}"
    echo -e "${GREEN}                                                                      ${NC}"
    echo -e "${GREEN}eduardo@koudrs.com | www.koudrs.com${NC}"
    echo -e "${GREEN}Installation completed successfully${NC}"
    echo -e "${GREEN}System will reboot in 5 seconds...${NC}"
    sleep 5
    reboot
else
    echo -e "${RED}Installation failed${NC}"
    exit 1
fi