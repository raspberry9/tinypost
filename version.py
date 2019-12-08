# MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION, BUILD_VERSION
VERSION = [0, 0, 0, 1]

def get_version(verbose=False):
    return "%s %s" % ("ver" if verbose else "", ".".join(map(str, VERSION)))
