import MySQLdb as mysql
from .utils import helper

HOST, USER, PASSWORD, DATABASE = helper.mysql_settings()

con = mysql.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE)

cur = con.cursor()

def execute(query,o=[]):
  cur.execute(query,o)

def print_rows():
  for row in cur:
    print row
  print

def print_versions(pkg):
  print pkg
  execute("SELECT releases.version, releases.revision FROM releases, packages WHERE packages.name=%s AND packages.id=releases.package_id",(pkg,))
  print_rows()

def print_releases(pkg):
  print pkg
  execute("SELECT releases.version, releases.revision, packages.name, distros.name, repos.codename FROM releases, packages, distros, repos WHERE packages.name=%s AND distros.id=repos.distro_id AND repos.id=releases.repo_id AND packages.id=releases.package_id",(pkg,))
  print_rows()

print_versions('linux')

print_releases('gcc')
print_releases('inkscape')
print_releases('bash')
print_releases('linux')
print_releases('subversion')

con.close()
