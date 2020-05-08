from cmd import run_chroot


def mkinitcpio():
    run_chroot(["mkinitcpio", "-v", "-P"])
