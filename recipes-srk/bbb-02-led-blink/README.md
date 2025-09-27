# BBB LED Blink Recipe

This recipe provides a simple LED blinking application for the BeagleBone Black that demonstrates GPIO control through the sysfs interface.

## What it does

The `bbb-02-led-blink` program blinks all 4 user LEDs on the BeagleBone Black in sequence:
- LED0 (USR0) - Green
- LED1 (USR1) - Green
- LED2 (USR2) - Green
- LED3 (USR3) - Green

Each LED turns on for 1 second, then the next LED in sequence turns on, creating a chasing light effect that repeats continuously.

## Building the Recipe

The recipe is named `bbb-02-led-blink.bb` and follows the BBB example naming convention.

To build just this recipe:

```bash
bitbake bbb-02-led-blink
```

## Including in the Image

The recipe is automatically included in the `core-image-tiny-initramfs-srk-11-bbb-examples` image. To build the complete image:

```bash
bitbake core-image-tiny-initramfs-srk-11-bbb-examples
```

## Running on the Target

After booting the BeagleBone Black with the initramfs image:

1. The program will be installed at `/usr/bin/bbb-02-led-blink`
2. Run it with:
   ```bash
   bbb-02-led-blink
   ```

3. You should see all 4 user LEDs blinking in sequence
4. Press `Ctrl+C` to stop the program

## Technical Details

- **LED Control**: Uses sysfs interface at `/sys/class/leds/beaglebone:green:usrX/`
- **Trigger**: Sets LED trigger to "none" for manual control
- **Brightness**: Controls LED state via brightness file (0=off, 1=on)
- **Timing**: 1 second delay between LED state changes

## Dependencies

- Linux kernel with LED sysfs support
- BeagleBone Black hardware with user LEDs

## Troubleshooting

If LEDs don't blink:

1. Check that you're running on actual BeagleBone Black hardware
2. Verify the LED sysfs paths exist: `ls /sys/class/leds/`
3. Ensure the program has permission to write to sysfs files

## Files

- `bbb-02-led-blink.bb` - The recipe file
- `files/bbb-led-blink.c` - Main C program (compiled to bbb-02-led-blink)
- `files/Makefile` - Build configuration
