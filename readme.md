# Kintaro Super Kuma 9000 Controller for Batocera

This repository contains the controller software for the Kintaro Super Kuma 9000 case, specifically adapted for Batocera Linux.

## Features

- Power button control (safe shutdown)
- Reset button functionality
- LED power indicator
- Temperature-controlled fan (if connected)
- Compatible with Batocera 40+ Linux on Raspberry Pi 3/3B/3B+

## Installation

### Quick Install (Recommended)

1. Connect to your Raspberry Pi via SSH:
```bash
ssh root@[your-pi-ip-address]
```

2. Run the installation command:
```bash
curl -sSL https://raw.githubusercontent.com/eduard0bet/kintaro-batocera/release/install.sh | bash
```

The script will automatically:
- Install all necessary files
- Set up proper permissions
- Configure autostart
- Restart your system to apply changes

### Manual Installation

If you prefer to install manually, follow these steps:

1. Connect to your Raspberry Pi via SSH:
```bash
ssh root@[your-pi-ip-address]
```

2. Create the necessary directories:
```bash
mkdir -p /userdata/system/kintaro
mkdir -p /userdata/system/custom.sh.d
```

3. Download the files:
```bash
curl -o /userdata/system/kintaro/kintaro.py https://raw.githubusercontent.com/eduard0bet/kintaro-batocera/release/kintaro.py
curl -o /userdata/system/custom.sh.d/S31kintaro https://raw.githubusercontent.com/eduard0bet/kintaro-batocera/release/S31kintaro
```

4. Set proper permissions:
```bash
chmod 755 /userdata/system/kintaro/kintaro.py
chmod 755 /userdata/system/custom.sh.d/S31kintaro
```

5. Configure autostart:
```bash
if [ ! -f /userdata/system/custom.sh ]; then
    echo '#!/bin/bash' > /userdata/system/custom.sh
    chmod +x /userdata/system/custom.sh
fi

echo '/userdata/system/custom.sh.d/S31kintaro start' >> /userdata/system/custom.sh
```

6. Reboot your system:
```bash
reboot
```

## Usage

Once installed, the controller will automatically:
- Start on system boot
- Control the case fan based on temperature (if connected)
- Handle power and reset button functions
- Manage the power LED

### Button Functions

- **Power Button**: Safely shuts down your Raspberry Pi
- **Reset Button**: Safely restarts your Raspberry Pi

## Troubleshooting

### Service Management

Check the status of the controller:
```bash
/userdata/system/custom.sh.d/S31kintaro status
```

View the log file:
```bash
/userdata/system/custom.sh.d/S31kintaro logs
```

Restart the controller:
```bash
/userdata/system/custom.sh.d/S31kintaro restart
```

### Common Issues

**LED doesn't turn on:**
- The LED will turn on after the system has fully booted
- Check if the service is running: `/userdata/system/custom.sh.d/S31kintaro status`

**Buttons not working:**
- Make sure the case is properly connected
- Try restarting the service: `/userdata/system/custom.sh.d/S31kintaro restart`

## Uninstallation

To uninstall the controller:

```bash
# Stop the service
/userdata/system/custom.sh.d/S31kintaro stop

# Remove the files
rm -f /userdata/system/custom.sh.d/S31kintaro
rm -rf /userdata/system/kintaro

# Remove the autostart entry
sed -i '/S31kintaro start/d' /userdata/system/custom.sh

# Reboot to apply changes
reboot
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the original Kintaro Super Kuma 9000 case controller
- Modified and adapted for Batocera Linux

## Support

For issues, questions, or suggestions, please open an issue in this repository or contact: eduardo@koudrs.com | www.koudrs.com