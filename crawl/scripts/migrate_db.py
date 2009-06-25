# -*- coding: utf-8 -*-

# Warning!  This file contains ugly code.  It should only need to be run once.

import MySQLdb as mysql
import psycopg2 as pg
import sys
sys.path.append("")

#open the file
from utils import helper
from utils.db import users
from utils.db import explore

OLD_DATABASE = "watershed"
HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()
con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD)
old_cur = con.cursor()
old_cur.execute("use %s"%(OLD_DATABASE,))
old_cur2 = con.cursor()
old_cur2.execute("use %s"%(OLD_DATABASE,))

ncon = pg.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
new_cur = ncon.cursor()

# migrate the distros, straight forward
print "migrate distros"
old_cur.execute("SELECT id, name, color, description FROM distros")
for row in old_cur:
	new_cur.execute("""INSERT INTO distros (id, name, color, description) VALUES (%s, %s, %s, %s)""",row)

new_cur.execute("SELECT MAX(id) FROM distros")
v = new_cur.fetchone()[0]+1
new_cur.execute("ALTER SEQUENCE distros_id_seq RESTART WITH %s", (v,))


# migrate the repos, trickier
print "migrate repos"
old_cur.execute("""SELECT DISTINCT distro_id, codename, component, architecture FROM repos""")
for row in old_cur:
	new_cur.execute("""INSERT INTO repos (distro_id, codename, component, architecture) VALUES (%s, %s, %s, %s)""", row)
	new_cur.execute("SELECT lastval()")
	repo_id = new_cur.fetchone()[0]
	old_cur2.execute("""SELECT branch, discovered FROM repos WHERE distro_id = %s AND codename = %s AND component = %s AND architecture = %s""", row)
	for row2 in old_cur2:
		new_cur.execute("""INSERT INTO branches (repo_id, branch, start) VALUES (%s, %s, %s)""", [repo_id] + list(row2))

new_cur.execute("SELECT MAX(id) FROM repos")
v = new_cur.fetchone()[0]+1
new_cur.execute("ALTER SEQUENCE repos_id_seq RESTART WITH %s", (v,))
new_cur.execute("SELECT MAX(id) FROM branches")
v = new_cur.fetchone()[0]+1
new_cur.execute("ALTER SEQUENCE branches_id_seq RESTART WITH %s", (v,))

# migrate packages
print "migrate packages"
old_cur.execute("""SELECT id, name, description FROM packages""")
for row in old_cur:
	new_cur.execute("INSERT INTO packages (id, name) VALUES (%s, %s)", (row[0], row[1]))
	if row[2] != None:
		new_cur.execute("INSERT INTO package_info (package_id, user_id, _when, description) VALUES (%s, 1, NOW(), %s)", (row[0], row[2]))

new_cur.execute("SELECT MAX(id) FROM packages")
v = new_cur.fetchone()[0]+1
new_cur.execute("ALTER SEQUENCE packages_id_seq RESTART WITH %s", (v,))

# migrate upstream releases
print "migrate upstream releases"
new_cur.execute("INSERT INTO usources (name, description, user_id) VALUES ('legacy_db2', 'import data from db2', 1)")
new_cur.execute("SELECT lastval()")
usource_id = new_cur.fetchone()[0]

old_cur.execute("""SELECT package_id, version, revision, released FROM releases WHERE repo_id IS NULL""")
for row in old_cur:
	row = list(row)
	if row[2]==None:
		row[2]='0'
	new_cur.execute("INSERT INTO ureleases (package_id, version, revision, released, usource_id) VALUES (%s, %s, %s, %s, %s)", row+[usource_id])

ncon.commit()
new_cur2 = ncon.cursor()

# migrate downstream releases
print "migrate downstream releases"
new_cur.execute("SELECT id, distro_id, codename, component, architecture FROM repos")
for row in new_cur:
	old_cur.execute("""SELECT package_id, version, revision, MIN(released) FROM releases, repos WHERE repo_id = repos.id AND repos.distro_id = %s AND repos.codename =  %s AND repos.component = %s AND repos.architecture = %s GROUP BY package_id, version, revision""", row[1:])
	for row2 in old_cur:
		new_cur2.execute("INSERT INTO dreleases (package_id, version, revision, released, repo_id) VALUES (%s, %s, %s, %s, %s)", list(row2)+[row[0]])

new_cur2.close()

# close all cursors
old_cur.close()
old_cur2.close()
new_cur.close()

con.close()

ncon.commit()
ncon.close()

# new old data
print "migrate multidepth sources"
												#start dir	#good pkgs	#bad pkgs #bad filename parts #bad versions #target depth #deadends
EXPLORE_SOURCES =	{"abiword": ["http://www.abisource.com/downloads/abiword/", ["abiword", "abiword-docs", "abiword-extra", "abiword-plugins"], None, [], [],								2,						["Windows/", "qnx/", "Fedora/", "MacOSX/", "RedHat/", "Linux/"]],
						"mysql":	 ["http://mirror.services.wisc.edu/mirrors/mysql/Downloads/", ["mysql"], None, [], ["solaris", "freebsd", "hpux", "osx"], 1, []],
						"ntp":		 ["ftp://ftp.udel.edu/pub/ntp/ntp4/", ["ntp"], None, [], [], 1, []],
						"ruby":		["ftp://ftp.ruby-lang.org/pub/ruby/", ["ruby"], None, [], [], 1, []],
						"sane":		["ftp://ftp.sane-project.org/pub/sane/", ["xsane", "sane", "sane-backends", "sane-frontends"], None, [], [], 2, []],
						"seamonkey":["http://ftp.mozilla.org/pub/mozilla.org/mozilla.org/seamonkey/releases/", ["seamonkey"], None, [".source"], [], 1, []],
						"util-linux-ng":["http://www.kernel.org/pub/linux/utils/util-linux-ng/", ["util-linux-ng"], None, [], [], 1, []],
						"util-linux":   ["http://www.kernel.org/pub/linux/utils/util-linux/", ["util-linux"], None, [], [], 1, []],
						"x11": ["http://xorg.freedesktop.org/releases/", None, ["contrib", "xc", "xorg", "tog", "XFree86", "xts", "xorg-x11", "autoconf", "scripts"], [], [], None, ["unsupported/", "extras/", "util/"]],
						"thunderbird": ["http://ftp.mozilla.org/pub/mozilla.org/mozilla.org/thunderbird/releases/", ["thunderbird"], None, [], [], 3, ["mac/", "win32/", "linux-i686/", "contrib/", "contrib-localized/", "mac-ppc/", "linux-i686-gtk2+xft/"]],
						"python": ["http://www.python.org/ftp/python/", ["Python", "python"], None, ["-linux", "-qnx4"], [], 2, ["2.0/", "doc/"]],
						"postfix": ["http://www.tigertech.net/mirrors/postfix-release/official/", None, [], [], [], 0, []],
						"linux": ["http://www.kernel.org/pub/linux/kernel/", ["linux"], None, [], [], None, ["people/", "ports/"]],
						"kde": ["http://mirror.cc.columbia.edu/pub/software/kde/", None, ["amarok-mac", "kolourpaint-1.2.2_kde3", "kssh-rc", "kfocus_1.1.0", "-RC"], [".src", ".i386"], [], None, ["snapshots/", "FreeBSD/", "Mandrake/", "RedHat/", "SuSE/", "contrib/", "Conectiva/", "Mandriva/", "kubuntu/", "AIX/", "ArkLinux/", "Slamd64/", "Pardus/", "Slackware/", "windows/", "win32/", "Debian/", "Turbo/", "Mandrakelinux/", "adm/", "devel/", "doc/", "events/", "packages/", "printing/", "Pardus/", "mac/", "security_patches/", "kolab/", "icons/"]],
						"gnu": ["http://ftp.gnu.org/gnu/", None, ["crypto-build", "bpel2owfn-mac-universal", "bpel2owfn-linux-gnu", "bpel2owfn-sparc" ,"bpel2owfn", "emacs-lisp-intro", "win-gerwin", "gcl_2.6.0cvs", "gcl-beta.sparc-solaris-binary", "git", "GNotary", "sdljump-osx"], ["-JDK1.2", "-linux", "-info+texi", "-latest", "-pkg", "-cvs", "-module", "-wish", ".SPARC.2.8.pkg"], [], None, ["windows/","packages/","gnu-0.2/","Doc/", "clisp/", "ddd/", "binaries/"]],
						"alpha_gnu": ["http://alpha.gnu.org/gnu/", None, ["grub-pc", "pspp-0.6.1+libtool", "solfege-easybuild"], [], [], None, ["windows/","packages/","gnu-0.2/","Doc/", "a2ps/", "edma/", "gnuradio/", "marcus/"]],
						"gimp": ["http://ftp.esat.net/mirrors/ftp.gimp.org/pub/gimp/", ["gimp"], None, [], [], None, ["contrib/","extras/","fonts/","help/","historical/","net-fu/","plug-ins/","plugin-template/","stable/", "v0.99.pre11/"]],
						"gnome": ["http://ftp.gnome.org/pub/gnome/sources/", None, ["chronojump-Linux-Install"], [], [], 2, []],
						"firefox": ["http://ftp.mozilla.org/pub/mozilla.org/mozilla.org/firefox/releases/", ["firefox"], None, [], [], None, ["0.8/", "0.9.1/", "0.9.2/", "0.9.3/", "0.9/", "0.9rc/", "0.10.1/", "0.10/", "0.10rc/", "1.0.1/" , "mac/", "win32/", "linux-i686/", "contrib/", "contrib-localized/", "mac-ppc/", "linux-i686-gtk2+xft/", "unimac/", "complete/", "granparadiso/", "partners/"]],
						#"apache": ["http://archive.apache.org/dist/", ["apache", "mod_python", "activemq-cpp", "apr", "apr-iconv", "apr-util", "cocoon", "hadoop", "lucene", "nutch", "maven", "mina", "mod_perl", "Mail-SpamAssassin", "tapestry"], None, [], [], None, []],
						"db": ["http://download-west.oracle.com/berkeley-db/", ["db"], None, [], [], None, []] #not working, wrong url
						}
for k in EXPLORE_SOURCES:
	v = EXPLORE_SOURCES[k]
	explore.add_explore_target(k, v[0], v[5], v[1], v[2], v[3], v[4], v[6])

print "migrate single directory sources"
SINGLE_SOURCES = {"ftp://pkg-shadow.alioth.debian.org/pub/pkg-shadow/": [["shadow"],[]],
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
           "http://kernel.org/pub/software/scm/git/": [["git", "git-core", "git-htmldocs", "git-manpages"],[]],
           "ftp://invisible-island.net/xterm/": [["xterm"],[]],
					 "ftp://download.nvidia.com/XFree86/nvidia-settings/": [["nvidia-settings"],[]],
					 "http://quassel-irc.org/pub/": [["quassel"],[]],
					 "http://elinks.or.cz/download/": [["elinks"],[]],
					 "http://releases.0x539.de/gobby/": [["gobby"],["stable", "latest"]]
          }
for k in SINGLE_SOURCES:
	v = SINGLE_SOURCES[k]
	explore.add_explore_target(v[0][0], k, 0, v[0], None, [], v[1], [])