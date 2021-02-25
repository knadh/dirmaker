![logo](https://user-images.githubusercontent.com/547147/109163952-e4610100-779f-11eb-9aa6-2236f06d3022.png)

dirmaker is a simple, opinionated static site generator for publishing directory websites like [Indic.page](https://indic.page). It takes entries from a YAML file and generates a categorised, paginated directory website.

--------------
Example site:

[![image](https://user-images.githubusercontent.com/547147/109164159-1eca9e00-77a0-11eb-9382-4f9d35aef72a.png)](https://indic.page)


## Usage

### Install 
`pip3 install dirmaker`

### Build a site
```shell
# Generate an example site in the `example` directory.
dirmaker --new

cd example

# Edit config.yml and add data to data.yml
# Customize static files and the template if necessary.

# Build the static site into a directory called `site`.
dirmaker --build
```

Licensed under the MIT license.
