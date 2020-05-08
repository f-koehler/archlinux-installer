from archinst.cmd import run_chroot


def add_group(name: str):
    run_chroot(["groupadd", name])


def add_normal_user(name: str):
    add_group(name)
    run_chroot(["useradd", "-m", "-g", name, name])
