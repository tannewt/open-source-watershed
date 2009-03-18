<?php
	include "db.php";
	
	$result = mysql_query("SELECT * FROM packages WHERE name = '".mysql_real_escape_string($_GET["pkg"])."'") or die('query failed: ' . mysql_error());
	$pkg = mysql_fetch_array($result, MYSQL_ASSOC) or die('unknown package!' . mysql_error());
	
	mysql_free_result($result);
	$history = mysql_query("SELECT releases.version, DATE(MIN(releases.released)) as date FROM releases, packages WHERE releases.package_id = packages.id AND packages.name='".$pkg["name"]."' AND releases.version!='9999' AND releases.repo_id IS NULL GROUP BY releases.version ORDER BY MIN(releases.released) DESC") or die('query failed: ' . mysql_error());
	$approx = false;
	if (mysql_num_rows($history)==0) {	
		mysql_free_result($history);
		$approx = true;
		$history = mysql_query("SELECT releases.version, DATE(MIN(releases.released)) as date FROM releases, packages WHERE releases.package_id = packages.id AND packages.name='".$pkg["name"]."' AND releases.version!='9999' GROUP BY releases.version ORDER BY MIN(releases.released) DESC") or die('query failed: ' . mysql_error());
	}
	
	$current = array();
	$result = mysql_query("SELECT distros.name, repos.branch, MAX(releases.version) as version FROM distros, releases, repos WHERE releases.repo_id=repos.id AND repos.distro_id=distros.id AND releases.package_id=".$pkg["id"]." GROUP BY distros.name, repos.branch;") or die('query failed: ' . mysql_error());
	while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
		if (!array_key_exists($line["version"],$current)) {
			$current[$line["version"]] = array();
		}
		$current[$line["version"]][] = $line['name'].":".$line['branch'];
	}
	mysql_free_result($result);
	
	$img = array(
		"debian:current" => "img/debian.png",
		"debian:future" => "img/debian_bw.png",
		"gentoo:current" => "img/gentoo.png",
		"gentoo:future" => "img/gentoo_bw.png",
		"ubuntu:current" => "img/ubuntu.png",
		"ubuntu:future" => "img/ubuntu_bw.png",
		"sabayon:current" => "img/sabayon.png",
		"sabayon:future" => "img/sabayon_bw.png",
		"fedora:current" => "img/fedora.png",
		"fedora:future" => "img/fedora_bw.png",
		"slackware:current" => "img/slackware.png",
		"slackware:future" => "img/slackware_bw.png",
		"arch:current" => "img/arch.png",
		"arch:future" => "img/arch_bw.png",
		"opensuse:current" => "img/opensuse.png",
		"opensuse:future" => "img/opensuse_bw.png");
?>
<html>
<head>
	<title>Open Source Watershed - Inkscape</title>
	<style type="text/css">
		.page_header {
			width: 800px;
			clear: both;
			padding-bottom: 5px;
			margin-left: auto;
			margin-right: auto;
		}
		
		td, table, tr {
			padding: 0px 0px 0px 0px;
			margin: 0px 0px 0px 0px;
			border-width: 0px;
		}
		
		.big {
			width: 500px;
		}
		
		.small {
			width: 300px;
		}
		
		.page_header #subtext {
			font-size: small;
			font-family: serif;
		}
		
		.page_header #title {
			text-align: left;
		}
		
		.page_header #title a {
			font-size: x-large;
			font-weight: bold;
			font-family: sans-serif;
			color: black;
			text-decoration: none;
		}
		
		.page_header #subtext {
			text-align: right;
			font-style: italic;
		}
		
		.page_header #search {
			padding: 0px 0px 0px 0px;
			position-bottom: 0px;
			text-align: right;
			height: 100%;
		}
		
		.page_header #search form {
			height: 100%;
		}
		
		.page_header #search input {
			padding: 0px 0px 0px 0px;
			vertical-align: bottom;
		}
		
		body {
			background-color: #d0dceb;
			font-family: sans-serif;
		}
		
		.info .title {
			background-color: #7891bf;
		}
		
		.desc {
			background-color: #e9eff9;
			height: 100%;
		}
		
		.history {
			background-color: #e9eff9;
			width: 800px;
			margin-left: auto;
			margin-right: auto;
		}
		
		.aliases {
			background-color: #ddffdd;
			color: #008000;
			width: 300px;
			height: 200px;
		}
		
		.details {
			width: 500px;
		}
		
		.info {
			margin-left: auto;
			margin-right: auto;
		}
		
		.history .title {
			color: #254d96;
			font-weight: bold;
			font-size: large;
			padding-left: 4px;
			padding-top: 4px;
		}
		
		.title #title {
			font-weight: bolder;
			font-size: x-large;
			color: #ffffff;
			padding-left: 32px;
			padding-top: 2px;
			padding-bottom: 2px;
		}
		
		.title #website {
			color: white;
			font-size: small;
			font-weight: bold;
			padding-left: 20px;
		}
		
		.history .date {
			color: #848884;
			font-size: small;
			vertical-align: center;
			padding-left: 6px;
		}
		
		.history .version {
			font-size: large;
			font-weight: bold;
			padding-left: 5px;
		}
		
		.history .new {
			font-size: x-large;
		}
		
		.subtitle {
			font-weight: bold;
			text-align: right;
			bottom: 0px;
			position: absolute;
		}
		
		.alias {
			text-align: center;
			bottom: 40%
		}
		
		.history img {
			padding-left: 8px;
			vertical-align: center;
		}
	</style>
</head>
<body>
	<table class="page_header">
		<tr>
			<td class="left" id="title_box">
				<div id="title"><a href="/">Open Source Watershed</a></div>
				<div id="subtext">"watching software flow downstream"</div>
			</td>
			<td class="small right" id="search" width=200 style="float: right">
				<form>
					<input type="text" name="search">
					<input type="submit" value="Search">
				</form>
			</td>
		</tr>
	</table>
	<table class="info">
		<tr>
			<td class="details">
				<div class="title">
					<span id="title"><?php echo $pkg["name"];?></span><span id="website"><?php echo $pkg["website"]; ?></span>
				</div>
				<div class="desc">
					no description
				</div>
			</td>
			<td class="aliases">
				<div>
					<?php
						$links = mysql_query("SELECT packages.name, links.strength, link_sources.description FROM packages, links, link_sources WHERE packages.id = links.package_id2 AND links.package_id1=".$pkg["id"]." AND link_sources.id = links.link_source_id") or die('query failed: ' . mysql_error());
						while ($line = mysql_fetch_array($links, MYSQL_ASSOC)) {
							$strength = "weak";
							if ($line["strength"] >= 200) {
								$strength = "strong";
							} else if ($line["strength"] >= 100) {
								$strength = "marginal";
							}
					 		echo "<span class=\"alias $strength\" title=\"".$line["strength"].": ".$line["description"]."\">".$line["name"]."</span>\n";
						};
						mysql_free_result($links);
					?>
				</div>
			</td>
		</tr>
	</table>
	<div class="history">
		<span class="title">History <?php if ($approx) { echo "*";} ?></span>
		<?php
			$first = " new";
			while ($line = mysql_fetch_array($history, MYSQL_ASSOC)) {
		 		echo "<div><span class=\"date\">".$line["date"]."</span><span class=\"version$first\">".$line["version"]."</span>";
		 		if (array_key_exists($line["version"],$current)) {
		 			foreach ($current[$line["version"]] as $v) {
		 				if (array_key_exists($v, $img)) {
		 					echo "<img src=\"".$img[$v]."\">";
		 				}
		 			}
		 		}
		 		$first = "";
		 		echo "</div>\n";
			};
			mysql_free_result($history);
		?>
	</div>
<?php
	mysql_close($db);
?>
</body>
</html>
