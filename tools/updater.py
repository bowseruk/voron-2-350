import json
import os
import shutil
import time
import subprocess


def update_katapult(name):
    # Check there is a config file
    if not os.path.exists(
        f"{os.path.expanduser('~')}/voron-2-300/config/katapult/{name}.config"
    ):
        return False
    # Clean up the klipper folder
    subprocess.run(
        [
            "make",
            "clean",
            f"KCONFIG_CONFIG={os.path.expanduser('~')}/voron-2-300/config/katapult/{name}.config",
        ],
        cwd=f"{os.path.expanduser('~')}/katapult",
    )
    # Make the binary that is in use
    subprocess.run(
        [
            "make",
            "-j4",
            f"KCONFIG_CONFIG={os.path.expanduser('~')}/voron-2-300/config/katapult/{name}.config",
        ],
        cwd=f"{os.path.expanduser('~')}/katapult",
    )
    # Move the file made out
    shutil.copyfile(
        f"{os.path.expanduser('~')}/katapult/out/deployer.bin",
        f"{os.path.expanduser('~')}/voron-2-300/binaries/katapult/{name}_deployer.bin",
    )
    shutil.copyfile(
        f"{os.path.expanduser('~')}/katapult/out/katapult.bin",
        f"{os.path.expanduser('~')}/voron-2-300/binaries/katapult/{name}.bin",
    )
    return True


def update_klipper(name):
    # Check there is a config file
    if not os.path.exists(
        f"{os.path.expanduser('~')}/voron-2-300/config/klipper/{name}.config"
    ):
        return False
    # Clean up the klipper folder
    subprocess.run(
        [
            "make",
            "clean",
            f"KCONFIG_CONFIG={os.path.expanduser('~')}/voron-2-300/config/klipper/{name}.config",
        ],
        cwd=f"{os.path.expanduser('~')}/klipper",
    )
    # Make the binary that is in use
    subprocess.run(
        [
            "make",
            "-j4",
            f"KCONFIG_CONFIG={os.path.expanduser('~')}/voron-2-300/config/klipper/{name}.config",
        ],
        cwd=f"{os.path.expanduser('~')}/klipper",
    )
    # Move the file made out
    shutil.copyfile(
        f"{os.path.expanduser('~')}/klipper/out/klipper.bin",
        f"{os.path.expanduser('~')}/voron-2-300/binaries/klipper/{name}.bin",
    )
    return True


def flash_device(uuid, payload, connection, maxTries=10):
    if connection == "canbus":
        flash_canbus(uuid, payload)
    elif connection == "usb":
        flash_usb(uuid, payload)
    elif connection == "canbridge":
        flash_canbridge(uuid, payload, maxTries)


def flash_canbridge(uuid, payload, maxTries=10):
    # Check for exisitting serial devices
    if os.path.exists("/dev/serial/by-id/"):
        startingDevices = set(os.listdir("/dev/serial/by-id/"))
    else:
        startingDevices = set()
    # Enter bootloader
    canbus_reset_to_bootloader(uuid)
    # retry looking for device until timeout
    for i in range(maxTries):
        if os.path.exists("/dev/serial/by-id/"):
            currentDevices = set(os.listdir("/dev/serial/by-id/"))
            if not (currentDevices - startingDevices):
                continue
            for device in currentDevices - startingDevices:
                flash_usb(f"/dev/serial/by-id/{device}", payload)
            break
        else:
            # Sleep and then retry to see if bridge comes up
            time.sleep(10)


def flash_usb(uuid, payload):
    print(f"USB flash device at {uuid} with {payload}")
    subprocess.run(
        [
            "python3",
            f"{os.path.expanduser('~')}/katapult/scripts/flashtool.py",
            "-f",
            payload,
            "-d",
            uuid,
        ]
    )


# This command flashes a device via canbus
def flash_canbus(uuid, payload):
    # Flash canbus module
    print(f"canbus flash device at {uuid} with {payload}")
    subprocess.run(
        [
            "python3",
            f"{os.path.expanduser('~')}/katapult/scripts/flashtool.py",
            "-i",
            "can0",
            "-f",
            payload,
            "-u",
            uuid,
        ]
    )
    return


# This command flashes a device via canbus
def canbus_reset_to_bootloader(uuid):
    # Flash canbus module
    print(f"Canbus message sent to enter bootloader to {uuid}")
    subprocess.run(
        [
            "python3",
            f"{os.path.expanduser('~')}/katapult/scripts/flashtool.py",
            "-i",
            "can0",
            "-r",
            "-u",
            uuid,
        ]
    )
    return


## This function opens a json
def main(klipper=False, katapult=False):
    with open(f"{os.path.expanduser('~')}/voron-2-300/config/printer.json") as f:
        data = json.load(f)

    for device in data:
        if katapult:
            update_katapult(device["name"])
            if device["auto_update_katapult"]:
                flash_device(
                    device["canbus_uuid"],
                    f"{os.path.expanduser('~')}/voron-2-300/binaries/katapult/{device['name']}_deployer.bin",
                    device["connection"],
                    10,
                )
        if klipper:
            update_klipper(device["name"])
            if device["auto_update_klipper"]:
                flash_device(
                    device["canbus_uuid"],
                    f"{os.path.expanduser('~')}/voron-2-300/binaries/klipper/{device['name']}.bin",
                    device["connection"],
                    10,
                )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--katapult", help="Update Katapult", action="store_true")
    parser.add_argument("-k", "--klipper", help="Update Klipper", action="store_true")
    args = parser.parse_args()
    klipper, katapult = False, False
    if args.klipper:
        klipper = True
    if args.katapult:
        katapult = True
    main(klipper, katapult)
