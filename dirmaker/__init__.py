#!/bin/python
import argparse
import os
import shutil
import sys

__version__ = "1.1.0"

def main():
    """Run the CLI."""
    p = argparse.ArgumentParser(
        description="A simple static site generator for generating directory websites.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    p.add_argument("-v", "--version", action="store_true", dest="version", help="display version")

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

    if len(sys.argv) == 1:
        p.print_help()
        p.exit()

    args = p.parse_args()

    if args.version:
        print("v{}".format(__version__))
        quit()

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
        from .dirmaker import Builder

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
