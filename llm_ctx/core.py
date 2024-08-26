# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['Sections', 'Project', 'parse_llm_txt', 'Doc', 'Section', 'mk_ctx', 'get_sizes', 'llms_txt2ctx']

# %% ../nbs/00_core.ipynb 2
from fastcore.utils import *
from fastcore.xml import *
from fastcore.script import *
import httpx

# %% ../nbs/00_core.ipynb 5
def _parse_links(content):
    link_pat = r'^\s*-\s*\[(.+?)\]\((.+?)\)(?:\s*:\s*(.*))?$'
    return [dict(zip(['title','url','info'], m.groups())) 
            for m in re.finditer(link_pat, content, re.M)]

def parse_llm_txt(md):
    "Parse fasthtml markdown into structured dict"
    title = re.findall(r'^# (.+)$', md, re.M)[0]
    summary = re.findall(r'^> (.+)$', md, re.M)[0]
    section_pat = r'^## (.+)$'
    sec_spl = re.split(section_pat, md, flags=re.MULTILINE)[1:]
    sections = {t.strip():_parse_links(c)
                for t,c in zip(sec_spl[::2], sec_spl[1::2])}
    return dict2obj(dict(title=title.strip(), summary=summary.strip(), sections=sections))

# %% ../nbs/00_core.ipynb 12
Sections = partial(ft, 'sections')
Project = partial(ft, 'project')

# %% ../nbs/00_core.ipynb 13
def Doc(url, **kw):
    "Create a `Doc` FT object with the text retrieved from `url` as the child, and `kw` as attrs."
    re_comment = re.compile('^<!--.*-->$', flags=re.MULTILINE)
    txt = [o for o in httpx.get(url).text.splitlines() if not re_comment.search(o)]
    return ft('doc', '\n'.join(txt), **kw)

# %% ../nbs/00_core.ipynb 14
def Section(nm, items):
    "Create a `Section` FT object containing a `Doc` object for each child."
    return ft(nm, *[Doc(**o) for o in items])

# %% ../nbs/00_core.ipynb 15
def mk_ctx(d, optional=True):
    "Create a `Project` with a `Section` for each H2 part in `d`, optionally skipping the 'optional' section."
    skip = '' if optional else 'Optional'
    sections = [Section(k, v) for k,v in d.sections.items() if k!=skip]
    return Project(title=d.title, summary=d.summary)(*sections)

# %% ../nbs/00_core.ipynb 19
def get_sizes(ctx):
    return {o.tag:{p.title:len(p.children[0]) for p in o.children} for o in ctx.children}

# %% ../nbs/00_core.ipynb 22
@call_parse
def llms_txt2ctx(
    fname:str, # File name to read
    optional:bool_arg=True # Skip 'optional' section?
):
    "Print a `Project` with a `Section` for each H2 part in file read from `fname`, optionally skipping the 'optional' section.."
    skip = '' if optional else 'Optional'
    sections = [Section(k, v) for k,v in d.sections.items() if k!=skip]
    ctx = Project(title=d.title, summary=d.summary)(*sections)
    print(to_xml(ctx))