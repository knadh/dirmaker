#!/bin/python

import argparse
import math
import os
import shutil
from copy import copy
import sys

from jinja2 import Template

import yaml


class Taxonomy:
    def __init__(self, name, slug, count):
        self.name = name
        self.slug = slug
        self.count = count

    def __str__(self):
        return self.name


class Category:
    def __init__(self, name, slug, count):
        self.name = name
        self.slug = slug
        self.count = count

    def __str__(self):
        return self.name


class Entry:
    def __init__(self, name, description, url, categories, taxonomies):
        self.name = name
        self.description = description
        self.url = url
        self.categories = categories

        # eg: {"tags": [...tags], "types": [...types]}
        self.taxonomies = taxonomies

    def __str__(self):
        return self.name


class Builder:
    template = Template("")
    outdir = ""
    config = {
        "base_url": "https://mysite.com",
        "per_page": 50,
        "taxonomies": ["tags"],
        "static_dir": "static",
        "site_name": "Directory site",
        "page_title": "{category}",
        "meta_description": "{category}",
    }

    entries = []
    all_categories = []
    all_taxonomies = []

    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = {**self.config, **yaml.load(f.read())}

    def build(self, outdir):
        # Create the output diretory.
        self.outdir = outdir
        self._create_dir(outdir)

        # For each category, render a page.
        for c in self.all_categories:
            self._render_page(
                cat=c,
                entries=self._filter_by_category(c, self.entries)
            )

        # Copy the first category as the index page.
        if len(self.all_categories) > 0:
            c = self.all_categories[0]
            shutil.copy(os.path.join(self.outdir, "{}.html".format(c.slug)),
                os.path.join(self.outdir, "index.html"))

    def load_data(self, infile):
        """Loads entries from the YAML data file."""
        entries = []
        with open(infile, "r") as f:
            items = yaml.load(f.read())
            if type(items) is not list or len(items) == 0:
                return []

            for i in items:
                entries.append(Entry(
                    name=i["name"],
                    description=i["description"],
                    url=i["url"],
                    categories=self._make_categories(i["categories"]),
                    taxonomies=self._make_taxonomies(i)
                ))

        self.entries = entries

        # Collate all unique tags and categories across all entries.
        self.all_categories = self._collate_categories(self.entries)
        self.all_taxonomies = self._collate_taxonomies(self.entries)


    def load_template(self, file):
        with open(file, "r") as f:
            self.template = Template(f.read())

    def _create_dir(self, dirname):
        # Clear the output directory.
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

        # Re-create the output directory.
        os.mkdir(dirname)

        # Copy the static directory into the output directory.
        for f in [self.config["static_dir"]]:
            target = os.path.join(self.outdir, f)
            if os.path.isfile(f):
                shutil.copyfile(f, target)
            else:
                shutil.copytree(f, target)

    def _make_taxonomies(self, item):
        """
        Make a dict of array of all taxonomy items on the entry.
        eg: {"tags": [...tags], "types": [...types]}
        """
        out = {}
        for tx in self.config["taxonomies"]:
            out[tx] = {}
            if tx not in item:
                continue

            # Iterate through each taxonomy array in the entry.
            for v in item[tx]:
                if v not in out[tx]:
                    id = v.lower()
                    out[tx][id] = Taxonomy(
                        name=v, slug=self._make_slug(v), count=0)
        for tx in self.config["taxonomies"]:
            out[tx] = sorted([out[tx][v]
                              for v in out[tx]], key=lambda k: k.name)

        return out

    def _collate_taxonomies(self, entries):
        """
        Return the unique list of all taxonomies across the given entries with counts.
        eg: {"tags": [...tags], "types": [...types]}
        """
        out = {}
        for e in entries:
            for tx in self.config["taxonomies"]:
                if tx not in out:
                    out[tx] = {}

                for t in e.taxonomies[tx]:
                    id = t.name.lower()
                    if id not in out[tx]:
                        out[tx][id] = copy(t)
                    out[tx][id].count += 1

        for tx in self.config["taxonomies"]:
            out[tx] = sorted([out[tx][v]
                              for v in out[tx]], key=lambda k: k.name)

        return out

    def _make_categories(self, cats):
        """Make a list of Categories out of the given string tags."""
        out = {}
        for c in cats:
            id = c.lower()
            if id not in out:
                out[id] = Category(name=c, slug=self._make_slug(c), count=0)

        return sorted([out[c] for c in out], key=lambda k: k.name)

    def _collate_categories(self, entries):
        """Return the unique list of all categories across the given entries with counts."""
        cats = {}
        for e in entries:
            for c in e.categories:
                id = c.name.lower()
                if id not in cats:
                    cats[id] = copy(c)
                cats[id].count += 1

        return sorted([cats[c] for c in cats], key=lambda k: k.name)

    def _filter_by_category(self, category, entries):
        out = []
        for e in entries:
            for c in e.categories:
                if c.slug == category.slug:
                    out.append(e)

        return sorted([e for e in out], key=lambda k: k.name.lower())

    def _make_slug(self, file):
        return file.replace(" ", "-").lower()

    def _render_page(self, cat, entries):
        total_pages = math.ceil(len(entries) / self.config["per_page"])
        page = 1

        for items in self._paginate(entries, self.config["per_page"]):
            html = self.template.render(
                config=self.config,
                pagination={"current": page, "total": total_pages},
                all_categories=self.all_categories,

                # Current category being rendered.
                category=cat,
                all_taxonomies=self.all_taxonomies,

                # Taxonomies of all the entries currently being rendered.
                taxonomies=self._collate_taxonomies(items),
                entries=items)

            fname = "{}{}.html".format(
                cat.slug, "-" + str(page) if page > 1 else "")
            with open(os.path.join(self.outdir, fname), "w") as f:
                f.write(html)

            page += 1

    def _paginate(self, entries, size):
        for start in range(0, len(entries), size):
            yield entries[start:start + size]


def main():
    """Run the CLI."""
    p = argparse.ArgumentParser(
        description="A simple static site generator for generating directory websites.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    n = p.add_argument_group("new")
    n.add_argument("-n", "--new", action="store_true",
                   dest="new", help="initialize a new site")
    n.add_argument("-p", "--path", action="store", type=str, default="example",
                   dest="exampledir", help="path to create the example site")

    b = p.add_argument_group("build")
    b.add_argument("-b", "--build", action="store_true",
                   dest="build", help="build a static site")
    b.add_argument("-c", "--config", action="store", type=str, default="config.yml",
                   dest="config", help="path to the config file")
    b.add_argument("-t", "--template", action="store", type=str, default="template.html",
                   dest="template", help="path to the template file")
    b.add_argument("-d", "--data", action="store", type=str, default="data.yml",
                   dest="data", help="path to the data file")
    b.add_argument("-o", "--output", action="store", type=str, default="site",
                   dest="output", help="path to the output directory")
    args = p.parse_args()

    if args.new:
        exdir = os.path.join(os.path.dirname(__file__), "example")
        if not os.path.isdir(exdir):
            print("unable to find bundled example directory")
            sys.exit(1)

        try:
            shutil.copytree(exdir, args.exampledir)
        except FileExistsError:
            print("the directory '{}' already exists".format(args.exampledir))
            sys.exit(1)
        except:
            raise

    if args.build:
        print("building site from: {}".format(args.data))

        bu = Builder(args.config)
        bu.load_template(args.template)
        bu.load_data(args.data)
        bu.build(args.output)

        print("processed {} entries, {} categories, {} taxonomies".format(len(bu.entries), len(bu.all_categories), len(bu.all_taxonomies)))

        if len(bu.entries) > 0:
            print("published to directory: {}".format(args.output))
        else:
            print("no data to build site")
