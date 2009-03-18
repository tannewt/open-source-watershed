<?php
	include "db.php";
	include "gen/data.php";
?>
<html>
<head>
	<title>Open Source Watershed - Home</title>
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
		}
		
		.page_header #title {
			text-align: left;
			font-size: x-large;
			font-weight: bold;
			font-family: sans-serif;
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
		}
		
		.graph {
			background-color: #ffffff;
			height: 300px;
		}
		
		.section {
			width: 800px;
			height: 300px;
			padding-top: 3px;
			margin-left: auto;
			margin-right: auto;
		}
		
		.small .header {
			background-color: #008000;
			font-family: sans-serif;
			font-weight: bold;
			color: white;
			padding: 5px 5px 5px 5px;
		}
		
		.section .small {
			background-color: #ddffdd;
			height: 100%;
			vertical-align: top;
			font-family: sans-serif;
		}
		
		.section .small a {
			color: #254d96;
			text-decoration: none;
			font-weight: bold;
			font-family: monospace;
			font-size: large;
		}
		
		.section .small a:visited {
			color: #7891bf;
			font-weight: bold;
		}
		
		.section .text {
			background-color: #e9eff9;
			vertical-align: top;
			height: 100%;
		}
		
		.text .header {
			font-weight: bold;
			font-family: sans-serif;
			padding: 5px;
		}
		
		.footer {
			margin-left: auto;
			margin-right:auto;
			font-family: sans-serif;
			color: #4b4b4b;
			width: 800px;
			text-align: center;
		}
		
		.small .content {
			padding-top:4px;
			padding-left:6px;
		}
		
		.content .distro {
		  font-weight: bold;
		}
	</style>
</head>
<body>
	<table class="page_header">
		<tr>
			<td class="left" id="title_box">
				<div id="title">Open Source Watershed</div>
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
	
	<table class="section">
		<tr>
			<td class="big left graph">
				<img src="gen/overview.png">
			</td>
			<td class="small right">
				<div class="header">Fresh Distros</div>
				<div class="content">
				<?php
					foreach ($distro_data as $name => $distro) {
						echo "<span class=\"distro\"><img src=\"img/" . $distro["name"] . ".png\" /> <span style=\"color: ".$distro["color"]."\">" . $distro["name"] . "</span></span>\t" . $distro["age"] . "<br>\n";
					}
				?>
				</div>
				<div>
				  lag: time since the oldest new release
				</div>
			</td>
		</tr>
	</table>
	
	<table class="section">
		<tr>
			<td class="small left">
				<div class="header">Fresh Software</div>
				<div class="content">
				<?php
					$result = mysql_query("SELECT packages.name,releases.version,releases.released FROM packages, releases WHERE packages.id = releases.package_id AND releases.repo_id IS NULL ORDER BY releases.released DESC LIMIT 13") or die('query failed: ' . mysql_error());
					while ($line = mysql_fetch_array($result, MYSQL_ASSOC)) {
						echo "<a href=\"package.php?pkg=" . $line['name'] . "\">" . $line['name'] . "</a> - " . "<a href=\"package.php?pkg=" . $line['name'] . "&v=". $line['version'] . "\">". $line['version'] . "</a><br>\n";
					}
					mysql_free_result($result);
				?>
				</div>
			</td>
			<td class="big right text">
				<div class="header">Latest News</div>
				<div class="header">About</div>
				<p>OS Watershed is a research project by Scott Shawcroft at the University of Washington in Seattle.  Twice a day data is collected from various distributions and upstream projects.  Then it is normalized and aggregated here.
			</td>
	</tr>
	</table>
	
	<div class="footer">
		<?php
					$result = mysql_query("SELECT time FROM crawls ORDER BY time DESC LIMIT 1") or die('query failed: ' . mysql_error());
					$line = mysql_fetch_array($result, MYSQL_ASSOC);
					echo "Last Crawl: " . $line["time"];
					mysql_free_result($result);
		?>
	</div>
<?php
	mysql_close($db);
?>
</body>
</html>
