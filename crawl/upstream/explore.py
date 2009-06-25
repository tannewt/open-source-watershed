# -*- coding: utf-8 -*-
import sys
sys.path.append(".")

from utils import helper
from utils import parsers

NAME="explore"
												#start dir	#good pkgs	#bad pkgs #bad version parts #target depth #deadends
SOURCES =	{"abiword": ["http://www.abisource.com/downloads/abiword/", ["abiword", "abiword-docs", "abiword-extra", "abiword-plugins"], None, [], [],								2,						["Windows/", "qnx/", "Fedora/", "MacOSX/", "RedHat/", "Linux/"]],
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

def contains(s, parts):
	for p in parts:
		if p in s:
			return True
	return False

def explore(last_crawl, url, good, bad, fn_remove, badv, depth, dead):
	print url
	pkgs = []
	info = helper.open_dir(url)
	
	if depth!=None and depth>0:
		new_depth = depth - 1
	elif depth==None:
		new_depth = None
	
	if info==None:
		return []
	for d,name,date in info:
		if last_crawl!=None and date!=None and depth<2 and date<last_crawl:
			continue
		
		if d and name not in dead and (depth==None or depth>0):
			if not name.endswith("/"):
				name += "/"
			
			pkgs += explore(last_crawl, url+name, good, bad, fn_remove, badv, new_depth, dead)
		elif not d:
			for token in fn_remove:
				if token in name:
					name = name.replace(token, "")
			rel = parsers.parse_filename(name)
			
			if rel!=None and ((good != None and rel.package in good and bad==None) or (good == None and bad != None and rel.package not in bad)) and not contains(rel.version, badv):
				rel.released = date
				print "*",rel
				pkgs.append(rel)
			elif rel != None:
				print rel
	return pkgs
	
def get_releases(last_crawl=None):
	rels = []
	for key in SOURCES:
		print "exploring",key
		rels += explore(last_crawl, *SOURCES[key])
	return rels

if __name__=="__main__":
	if len(sys.argv)<2:
		pkgs = get_releases()
	else:
		pkgs = []
		for p in sys.argv[1:]:
			pkgs += explore(None, *SOURCES[p])
	
	#for p in pkgs:
	#	#print p