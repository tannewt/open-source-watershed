try:
  from .utils import helper
  from .utils import parsers
except:
  import sys
  sys.path.append(".")
  from utils import helper
  from utils import parsers

NAME="single_dir"

SOURCES = {"ftp://pkg-shadow.alioth.debian.org/pub/pkg-shadow/": [["shadow"],[]],
           "ftp://ftp.cistron.nl/pub/people/miquels/sysvinit/": [["sysvinit"],[]],
           "http://www.infodrom.org/projects/sysklogd/download/": [["sysklogd"],[]],
           "ftp://ftp.astron.com/pub/file/" : [["file"],[]],
           "http://devresources.linux-foundation.org/dev/iproute2/download/": [["iproute2"],[]],
           "http://ftp.altlinux.org/pub/people/legion/kbd/": [["kbd"],["stable","testing"]],
           "http://www.kernel.org/pub/linux/docs/manpages/Archive/": [["man-pages"],[]],
           "http://mirror.sourceshare.org/savannah/man-db/": [["man-db"],[]],
           "http://www.kernel.org/pub/linux/utils/kernel/module-init-tools/": [["module-init-tools"],[]],
           "http://www.kernel.org/pub/linux/utils/kernel/hotplug/": [["udev"],[]],
           "http://ftp.vim.org/pub/vim/unix/": [["vim"],[]],
           "ftp://ftp.alsa-project.org/pub/lib/": [["alsa-lib"],[]],
           "ftp://ftp.alsa-project.org/pub/driver/": [["alsa-driver"],[]],
           "ftp://ftp.alsa-project.org/pub/utils/": [["alsa-utils"],[]],
           "http://apache.osuosl.org/apr/" : [["apr", "apr-util"],[]],
           "http://distfiles.atheme.org/" : [["audacious", "atheme", "atheme-services", "audacious-plugins", "charybdis", "conspire", "libmcs", "libmowgli", "mcs"],[]],
           "ftp://ftp.samba.org/pub/ccache/": [["ccache"],[]],
           "http://curl.smudge-it.co.uk/download/": [["curl"],[]],
           "http://www.freedesktop.org/software/desktop-file-utils/releases/": [["desktop-file-utils",],[]],
           "ftp://invisible-island.net/diffstat/": [["diffstat"],[]],
           "ftp://ftp.gnupg.org/gcrypt/dirmngr/": [["dirmngr"],[]],
           "http://www.daniel-baumann.ch/software/dosfstools/": [["dosfstools"],[]],
           "http://cairographics.org/releases/": [["cairo", "cairomm", "pixman", "pycairo", "rcairo"],[]],
           "http://fribidi.org/download/": [["fribidi"],[]],
           "http://members.dslextreme.com/users/billw/gkrellm/": [["gkrellm"],[]],
           "http://hal.freedesktop.org/releases/": [["hal","hal-info", "PolicyKit", "PolicyKit-gnome", "DeviceKit", "DeviceKit-disks", "DeviceKit-power"],[]],
           "http://freedesktop.org/software/icon-theme/releases/": [["hicolor-icon-theme"],[]],
           "http://tango.freedesktop.org/releases/": [["icon-naming-utils", "tango-icon-theme", "tango-icon-theme-extras"],[]],
           "ftp://ftp.imagemagick.org/pub/ImageMagick/": [["ImageMagick"],[]],
           "ftp://ftp.netfilter.org/pub/iptables/": [["iptables"],[]],
           "ftp://iptraf.seul.org/pub/iptraf/": [["iptraf"],["bin"]],
           "http://irssi.org/files/": [["irssi"],[]],
           "http://ftp.yars.free.net/pub/source/lftp/old": [["lftp"],[]],
           "http://ftp.yars.free.net/pub/source/lftp/": [["lftp"],[]],
           "http://downloads.xiph.org/releases/ao/": [["libao"],[]],
           "ftp://ftp.gnupg.org/gcrypt/libgpg-error/": [["libgpg-error"],[]],
           "ftp://ftp.gnupg.org/gcrypt/libksba/": [["libksba"],[]],
           "http://downloads.xiph.org/releases/ogg/": [["libogg"],[]],
           "http://downloads.xiph.org/releases/vorbis/": [["libvorbis", "vorbis-tools"],[]],
           "http://downloads.xiph.org/releases/theora/": [["libtheora"],[]],
           "http://liboil.freedesktop.org/download/": [["liboil"],[]],
           "http://www.linux1394.org/dl/": [["libraw1394", "libiec61883"],[]],
           "http://www.codon.org.uk/~mjg59/libx86/downloads/": [["libx86"],[]],
           "http://www.oberhumer.com/opensource/lzo/download/": [["lzo"],[]],
           "http://www.kernel.org/pub/linux/utils/raid/mdadm/": [["mdadm"],[]],
           "http://www.selenic.com/mercurial/release/": [["mercurial"],[]],
           "ftp://ftp.bitwizard.nl/mtr/": [["mtr"],[]],
           #"http://www.tazenda.demon.co.uk/phil/net-tools/": [["net-tools"],[]],
           "ftp://ftp.uk.linux.org/pub/linux/Networking/netkit-devel/": [["netkit-ftp", "netkit-rsh", "netkit-bootparamd", "netkit-ntalk", "netkit-routed", "netkit-rusers", "netkit-rwall", "netkit-rwho", "netkit-timed"],[]],
           "ftp://ftp.uk.linux.org/pub/linux/Networking/netkit/": [["netkit-ftp", "netkit-rsh", "netkit-bootparamd", "netkit-ntalk", "netkit-routed", "netkit-rusers", "netkit-rwall", "netkit-rwho", "netkit-timed"],[]],
           "http://nmap.org/dist/": [["nmap"],[]],
           "http://mirror.mcs.anl.gov/openssh/": [["openssh"],[]],
           "ftp://ftp.openssl.org/source/": [["openssl"],[]],
           "http://openvpn.net/release/": [["openvpn"],[]],
           "ftp://atrey.karlin.mff.cuni.cz/pub/linux/pci/": [["pciutils"],[]],
           "http://kernel.org/pub/linux/utils/kernel/pcmcia/": [["pcmciautils"],[]],
           "ftp://ftp.gnupg.org/gcrypt/pinentry/": [["pinentry"],[]],
           "http://pm-utils.freedesktop.org/releases/": [["pm-utils"],[]],
           "ftp://ftp.samba.org/pub/ppp/": [["ppp"],[]],
           "ftp://ftp.samba.org/pub/rsync/src//": [["rsync"],[]],
           "ftp://us1.samba.org/pub/samba/stable/": [["samba"],[]],
           "http://sg.danny.cz/sg/p/": [["sdparm"],[]],
           "http://freedesktop.org/software/shared-mime-info/": [["shared-mime-info"],[]],
           "ftp://www.stunnel.org/stunnel/src/": [["stunnel"],[]],
           "http://www.sudo.ws/sudo/dist/OLD/": [["sudo"],[]],
           "http://www.sudo.ws/sudo/dist/": [["sudo"],[]],
           "http://www.kernel.org/pub/linux/utils/boot/syslinux/Old/": [["syslinux"],[]],
           "http://www.kernel.org/pub/linux/utils/boot/syslinux/": [["syslinux"],[]],
           "ftp://sunsite.unc.edu/pub/Linux/libs/graphics/": [["t1lib"],[]],
           "http://developer.kde.org/~wheeler/files/src/": [["taglib"],[]],
           "http://www.tcpdump.org/release/": [["tcpdump"],[]],
           "ftp://ftp.astron.com/pub/tcsh/old/": [["tcsh"],[]],
           "ftp://ftp.astron.com/pub/tcsh/": [["tcsh"],[]],
           "ftp://ftp.tin.org/pub/news/clients/tin/stable/": [["tin"],["current"]],
           "ftp://ftp.tin.org/pub/news/clients/tin/unstable/": [["tin"],[]],
           "http://kernel.org/pub/software/scm/git/": [["git", "git-core", "git-htmldocs", "git-manpages"],[]]
          }

def get_releases(last_crawl=None):
  pkgs = []
  for source in SOURCES:
    info = helper.open_dir(source)
    if info==None:
      return []
    for d,fn,date in info:
      if not d and (last_crawl==None or date>last_crawl):
        rel = parsers.parse_filename(fn)
        # check version
        for bad_version in SOURCES[source][1]:
          if rel != None and bad_version in rel[2]:
            continue
        if rel != None and rel[0] in SOURCES[source][0]:
          rel[3] = date
          pkgs.append(rel)
  
  #name, epoch, version, date, extra
  #rel = ["subversion",0, None, None, None]

  return pkgs

if __name__=="__main__":
  pkgs = get_releases()
  for p in pkgs:
    print p[0], p[2]
