from pb_portal import mem


def refresh():
    mem.flush_all()


if __name__ == '__main__':
    refresh()
