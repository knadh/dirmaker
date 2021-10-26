#!/bin/python

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
            self.config = {**self.config, **yaml.load(f.read(), Loader=yaml.FullLoader)}

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
            items = yaml.load(f.read(), Loader=yaml.FullLoader)
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
                    id = v.strip().lower()
                    if id == "":
                        continue

                    out[tx][id] = Taxonomy(
                        name=v, slug=self._make_slug(v), count=0)

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
                    id = t.name.strip().lower()
                    if id == "":
                        continue

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
