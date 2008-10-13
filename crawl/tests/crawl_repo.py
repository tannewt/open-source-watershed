import distros.fedora

repos = distros.fedora.get_repos()

for r in repos[-2:]:
  print r
  print map(lambda x: x[:-1],distros.fedora.crawl_repo(r))[:5]
