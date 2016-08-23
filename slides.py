#!/usr/bin/env python3

# Requirements:
#  System:
#   - wkhtmltopdf
#   - pdftk
#  Python 3:
#   - Python Markdown
#   - Beautiful Soup 4

import os
import sys

import re
import json
import copy
import pdfkit
import shutil

import bs4

import markdown
import markdown.extensions.codehilite


BS4_PARSER = "lxml"

ENABLE_DEBUG_INFO = False

def log_info(message):
    print("(info) %s" % message)

def log_warning(message):
    print("(warn) %s" % message)

def log_error(message):
    print("(error) %s" % message)

def DEBUG(message):
    global ENABLE_DEBUG_INFO

    if ENABLE_DEBUG_INFO:
        print("(DEBUG) %s" % message)


def merge_map(dest, src):
    for key, value in src.items():
        dest[key] = value


# Mathjax Extension
class MathJaxPattern(markdown.inlinepatterns.Pattern):

    def __init__(self):
        markdown.inlinepatterns.Pattern.__init__(
            self,
            r'(?<!\\)(\$\$?)(.+?)\2'
        )

    def handleMatch(self, m):
        node = markdown.util.etree.Element('mathjax')
        node.text = markdown.util.AtomicString(
            m.group(2) + m.group(3) + m.group(2))
        return node


class MathJaxExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        # Needs to come before escape matching because \ is pretty important in
        # LaTeX
        md.inlinePatterns.add('mathjax', MathJaxPattern(), '<escape')


def latex_friendly(configs=[]):
    return MathJaxExtension(configs)


# Markdown parser
class MarkdownParser(object):
    """Parse markdown content to HTML content"""
    def __init__(self, extensions, config):
        super(MarkdownParser, self).__init__()

        self.parser = markdown.Markdown(
            extensions = extensions,
            extension_configs = config
        )

    def from_string(self, content):
        result = self.parser.convert(content)

        return (result, self.parser.Meta)

    def from_fileobj(self, reader):
        result = self.parser.convert(reader.read())

        return (result, self.parser.Meta)

    def from_file(self, filepath):
        with open(filepath) as reader:
            result = self.parser.convert(reader.read())

        return (result, self.parser.Meta)


def get_markdown(extensions, config):
    extensions += [
        "markdown.extensions.meta",
        latex_friendly()
    ]

    return MarkdownParser(extensions, config)


# HTML parser
class HTMLParser(object):
    """Parse HTML code to pdf document"""
    def __init__(self, options):
        super(HTMLParser, self).__init__()
        self.options = options
    
    def from_string(self, content, output):
        pdfkit.from_string(
            content, output,
            options = self.options
        )

    def from_fileobj(self, reader, output):
        pdfkit.from_string(
            reader.read(), output,
            options = self.options
        )

    def from_file(self, filepath, output):
            pdfkit.from_file(
                filepath, output,
                options = self.options
            )


def get_html(options):
    _options = {
        "page-size": "A4",
        "orientation": "Landscape",
        "margin-top": "0.0px",
        "margin-right": "0.0px",
        "margin-bottom": "0.0px",
        "margin-left": "0.0px",
        "encoding": "UTF-8"
    }

    merge_map(_options, options)
    return HTMLParser(_options)


# Markdown spliter
class MarkdownSpliter(object):
    """Split markdown source into seperate pages"""
    def __init__(self, work_folder):
        super(MarkdownSpliter, self).__init__()
        self.work_folder = work_folder

    def _title_matcher(self, content):
        content = content.lstrip()
        return content.startswith("#") and not content.startswith("##")

    def _seperator_matcher(self, content):
        content = content.strip()
        return len(content) >= 3 and content.strip("-=") == ""

    def _codeblock_matcher(self, content):
        return content.lstrip().startswith("```")

    def from_string(self, content):
        lines = content.split("\n")
        DEBUG(lines)
        meta = []
        result = []
        pos = 0

        # Skip meta info
        while pos < len(lines):
            line = lines[pos]
            pos += 1

            if self._title_matcher(line):
                DEBUG("At #%s matched title." % pos)
                result.append([line])
                break
            else:
                meta.append(line)

        # Seperate markdown source
        quiet = False
        while pos < len(lines):
            line = lines[pos]
            pos += 1

            if self._codeblock_matcher(line):
                DEBUG("At #%s matched codeblock." % pos)
                quiet = not quiet
                result[-1].append(line)

            elif quiet:
                result[-1].append(line)
                continue

            elif self._title_matcher(line):
                DEBUG("At #%s matched title." % pos)
                result.append([line])

            elif self._seperator_matcher(line):
                DEBUG("At #%s matched seperator." % pos)
                result.append(copy.copy(result[-1]))

                # Skip next emtpy line
                if pos < len(lines) and lines[pos].strip() == "":
                    pos += 1

            else:
                result[-1].append(line)

        return (
            "%s" % "\n".join(meta),
            ["\n".join(x) for x in result]
        )

    def from_file(self, filepath):
        base = os.path.basename(filepath)

        with open(filepath) as reader:
            meta, contents = self.from_string(reader.read())

        idx = 0
        for content in contents:
            with open(os.path.join(self.work_folder, "%s.%s" % (base, idx)), "w") as writer:
                writer.write(meta)
                writer.write("\n")
                writer.write(content)

            idx += 1

        return (base, idx)


# Template manager
class TemplateManager(object):
    """Manage the required templates"""
    def __init__(self, work_folder, content_folder):
        super(TemplateManager, self).__init__()
        self.work_folder = work_folder
        self.content_folder = content_folder
        self.templates = {}
        self.stylesheets = set()

    def load(self, template):
        if template in self.templates:
            return

        with open(os.path.join(self.content_folder, template)) as reader:
            self.templates[template] = reader.read()

        document = bs4.BeautifulSoup(self.templates[template], BS4_PARSER)
        for x in document.find_all("link", attrs = {"rel": "stylesheet"}):
            css = x["href"]
            if not css in self.stylesheets:
                self.stylesheets.add(css)
                shutil.copy(
                    os.path.join(self.content_folder, css),
                    os.path.join(self.work_folder, css)
                )

    def get(self, template):
        return self.templates[template]


def main():
    global ENABLE_DEBUG_INFO

    if "--debug" in sys.argv:
        log_warning("Debug mode enabled.")
        ENABLE_DEBUG_INFO = True
        sys.argv.remove("--debug")

    if len(sys.argv) < 2:
        print("Usage: %s [SLIDES FOLDER] [--debug]" % (sys.argv[0]))
        exit(-1)

    name = sys.argv[1]
    log_info("Processing %s..." % name)

    log_info("Reading configuration...")
    if not os.path.exists("{0}/{0}.json".format(name)):
        log_error("No configuration file: %s" % "{0}/{0}.json".format(name))
        exit(-1)

    config = None
    with open("{0}/{0}.json".format(name)) as reader:
        config = json.load(reader)

    temporary = "%s/.build/" % name
    log_info("Set temporary folder to %s" % temporary)
    if not os.path.exists("%s" % temporary):
        log_info("Folder not created. Create a new one.")
        os.mkdir("%s" % temporary)

    log_info("Spliting files...")
    spliter = MarkdownSpliter(temporary)
    worklist = []
    for file in config["input"]:
        log_info("Spliting '%s'..." % file)
        data = spliter.from_file("%s/%s" % (name, file))
        worklist.append(data)

    log_info("Parsing pages...")
    markdown_parser = get_markdown(
        config["markdown_extensions"],
        config["markdown_config"]
    )
    htmllist = []
    for filename, count in worklist:
        for idx in range(0, count):
            target = os.path.join(temporary, filename) + "." + str(idx)
            log_info("Parsing %s..." % target)
            data = markdown_parser.from_file(target)

            htmllist.append(data)

    DEBUG(htmllist)

    log_info("Preparing files and folders...")
    for file in config["prepare_files"]:
        src = os.path.join(name, file)
        dest = os.path.join(temporary, file)

        if os.path.exists(dest):
            os.remove(dest)

        shutil.copy(src, dest)

    for folder in config["prepare_folders"]:
        src = os.path.join(name, folder)
        dest = os.path.join(temporary, folder)

        if os.path.exists(dest):
            shutil.rmtree(dest)

        shutil.copytree(src, dest)

    log_info("Printing pages...")
    manager = TemplateManager(temporary, name)
    pagelist = []
    idx = 0
    for content, metainfo in htmllist:
        temp_config = copy.copy(config["options"])

        # Because mathjax is too slow...
        if config["no_mathjax_auto_delay"] > 0 and not "<mathjax>" in content:
            log_info("'no_mathjax_auto_delay' enabled.")
            temp_config["javascript-delay"] = config["no_mathjax_auto_delay"]

        html_parser = get_html(temp_config)

        log_info("Printing... [%s / %s]" % (idx + 1, len(htmllist)))

        # Extract HTML info
        document = bs4.BeautifulSoup(content, BS4_PARSER)
        title = document.h1.text  # Each slide has only one h1 header

        # Each slide must have a template
        if not "template" in metainfo:
            log_error("Each slide must have a template")
            exit(-1)
        template = metainfo["template"][0]
        manager.load(template)  # Only select the first one

        content = manager.get(template).format(
            title = title,
            content = content
        )

        target_html = os.path.join(temporary, "%s.html" % idx)
        with open(target_html, "w") as writer:
            writer.write(content)

        target = os.path.join(temporary, "%s.pdf" % idx)
        html_parser.from_file(target_html, target)
        pagelist.append(target)

        idx += 1

    log_info("Connecting printed pages...")
    os.system(
        "pdftk %s cat output %s" % (
            " ".join(pagelist),
            os.path.join(temporary, config["output"])
        )
    )

    log_info("Copy the result to the work folder.")
    shutil.copy(
        os.path.join(temporary, config["output"]),
        os.path.join(name, config["output"])
    )

    log_info("slides.py exited.")


if __name__ == "__main__":
    main()
