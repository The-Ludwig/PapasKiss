# [Papa's Kiss](https://the-ludwig.github.io/cook/)

Webpage: [https://the-ludwig.github.io/cook/](https://the-ludwig.github.io/cook/)


My recipes in the [cooklang](https://cooklang.org/) format.
Most of them are inspired by, or even just copied from [Joshua Weissman](https://joshuaweissman.com).
Please do yourself a favor and check out his [YouTube videos](https://www.youtube.com/c/JoshuaWeissman).

### Creating the Webpage

I wrote a small python script to render the recipes as a webpage, using the templates in the template folder.
It uses the `cooklang` python module. 

If you have [python `poetry`](https://python-poetry.org/) installed, just use
```sh
> poetry install
> poetry run python build.py
```
and the webpages can be found in `build/`. 

Please feel free to improve on this, and please let me know if you do :-).