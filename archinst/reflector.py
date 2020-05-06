from archinst.cmd import run


def run_reflector(chroot: bool = False, country: str = "Germany"):
    run([
        "reflector", "--age", "12", "--country", country, "--protocol",
        "https", "--sort", "rate", "--save", "/mnt/etc/pacman.d/mirrorlist"
        if chroot else "/etc/pacman.d/mirrorlist"
    ])
