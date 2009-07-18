package_badge = function(package, element) {
  $.getJSON("http://127.0.0.1:8000/api/0.1/package.json?cb=?", {package: package}, function(data) {
			$(element).css({"font-family": "sans-serif"})
      $(element).append('<a href="http://oswatershed.org/"><img style="border: none; padding-right: 4px;" src="http://static.oswatershed.org/small_logo.png" /></a>');
      $(element).append('<a style="color: black; text-decoration: none;" id="pkglink" href="http://oswatershed.org/pkg/'+data.package+'"></a>');
      $(element+" #pkglink").append(data.package);
      $(element+" #pkglink").append('<strong> '+data.latest+'</strong>');
      $.each(data.distros, function(i,distro) {
	$(element+" #pkglink").append('<img style="border: none; padding-left: 8px; padding-right: 4px;" src="http://static.oswatershed.org/'+distro.logo+'" />');
	if (distro.uptodate)
	  $(element+" #pkglink").append('<strong>'+distro.version+'</strong>');
	else
	  $(element+" #pkglink").append(distro.version);
      });
     }, "jsonp");
}