<h1>Satisfactory Factory Planner</h1>

<h2>Important!</h2>
<h3>About</h3>
<p>This project is currently being used for me to learn and expand my knowledge on new libraries, languages and tools (sush as Flask, GitHub, HTML, CSS, SQLAlchemy, webscraping, etc.), alternatives sites exist should be used instead.</p>
<p>This project aims to mainly work with python as much as possible, and only interact with other languages when neccessary, and is a side project/hobby. It is not in a finished state.</p>
<h3>Use Instructions</h3>
<p>The only way to run it, currently, is to host it locally by running the app.py file, this should also run webscraping and database population functions if those directories are empty (note that not all poetry dependencies have been added to the <a href="pypoject.toml">pypoject.toml</a> yet, so will need to be manually installed).</p>

<h2>Screenshots</h2>

<h3 id='form'>Form:</h3>
<p>The form can be interacted with to offer the selection of items that are accessed via the database, and offer two other options. The Items/min offers a scaleable amount to be calculate from the base results, and the recursive option allows for the graph to be repeated along branches until exhuasted.</p>
<div align="center">
  <img src="screenshots\recursive_network_form_item_list.png">
</div>

<h3>Results:</h3>
<p>Resulting graph of using the form (in the <a href='#form'>image above</a>) with the options 'Adaptive Control Unit' for the output, 4 items/min, and recursive set to yes.</p>
<div align="center">
  <img src="screenshots\recursive_network_example.png">
</div>

<h3>Data:</h3>
<p>This page displays basic information that was webscraped and stored in the database, for each image, there are 3 links: the link to the image, via the image itself; the link to the wiki.gg page, via the 'wiki' text on each item; and finally a link to the non-recurssive graph generated from the database, accessed and generated upon clicking the name of the item.</p>
<div align="center">
  <img src="screenshots\data_page.png"></img>
</div>

<h3>Changelog:</h3>
<p>This has yet to be implemented yet, but an automatic changelog will be generated from the git commits, and will be displayed on its own page in order to update users with project progress/fixes.</p>
<p>A temporary, manually done, changelog can be found <a href="CHANGELOG.md">here</a>.</p>

<h2>Similar Community Tools</h2>
<p>This project is very similar to two popular community tools used for visualisations of production lines in the game.</p>
<p>These are:</p>
<ul>
  <li><a href="https://www.satisfactorytools.com/1.0/">Satisfactory Tools</a></li>
  <li><a href="https://satisfactory-calculator.com/">Satisfactory Calculator</a></li>
</ul>