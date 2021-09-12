Unless the paths on the web server match the filesystem paths, the expectation is to use sed:

    python main.py ~/MSUCC\ page/ "Michigan State University Children's Choir" | sed 's/\/home\/steve\/MSUCC page\/Michigan State University Children’s Choir/\/msucc/' > index.html
