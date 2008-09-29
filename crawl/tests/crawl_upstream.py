from .upstream import subversion

print map(lambda x: x[:-1], subversion.get_releases())
