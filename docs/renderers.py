from quartodoc import MdRenderer
from griffe import dataclasses as dc
from griffe.docstrings import dataclasses as ds
from plum import dispatch
from tabulate import tabulate
from typing import *
from griffe.expressions import Name, Expression
from quartodoc.renderers import *

_UNHANDLED = []

## NOTE: CAREFUL! DISPATCH DEFINITION ORDER MATTERS HERE!
class MdRendererNumpyStyle(MdRenderer):
  style = "markdown_numpy"
  
  def _fetch_object_dispname(self, el: "dc.Alias | dc.Object"):
    if self.display_name == "parent":
      return el.parent.name + "." + el.name
    else: 
      return super(MdRendererNumpyStyle, self).render(el)
  
  # Keep admonition at the top here ----
  @dispatch
  def render(self, el: ds.DocstringSectionAdmonition) -> str:
    _UNHANDLED.append(el)
    return "UNHANDLED ADMONITION"

  @dispatch
  def render(self, el: Union[dc.Object, dc.Alias]):
    return super(MdRendererNumpyStyle, self).render(el)

  # Parameters ----
  @dispatch
  def render(self, el: ds.DocstringSectionParameters) -> str:
    params_str = []
    for ds_param in el.value:
      d = ds_param.as_dict()
      pn, pa, pd = [d.get(k) for k in ("name", "annotation", "description")]
      sec_md = f"**{pn}** : "
      if isinstance(pa, Name) or isinstance(pa, Expression):
        sec_md += f"<span class='type_annotation'> {pa.full}, </span>"
      else: 
        sec_md += "" if pa is None or len(str(pa)) == 0 else str(pa)+", "
      sec_md += f"optional (default={ d.get('value') })" if "value" in d.keys() else "required"
      sec_md += f"<p> {pd} </p>" 
      params_str.append(sec_md)
    return "\n\n".join(params_str)

  @dispatch
  def render(self, el: dc.Parameters):
    return super(MdRendererNumpyStyle, self).render(el)

  @dispatch
  def render(self, el: dc.Parameter):
    return super(MdRendererNumpyStyle, self).render(el)

  # returns ----
  @dispatch
  def render(self, el: Union[ds.DocstringSectionReturns, ds.DocstringSectionRaises]) -> str:
    params_str = []
    for ds_param in el.value:
      d = ds_param.as_dict()
      pn, pa, pd = [d.get(k) for k in ("name", "annotation", "description")]
      sec_md = f"**{pn}** : "
      if isinstance(pa, Name) or isinstance(pa, Expression):
        sec_md += f"<span class='type_annotation'> {pa.full}, </span>"
      else: 
        sec_md += "" if pa is None or len(str(pa)) == 0 else str(pa)+", "
      sec_md += f"<p> {pd} </p>" #style='margin-top: 10px;margin-left: 2.5em;
      params_str.append(sec_md)
    return "\n\n".join(params_str)

  ## This shouldn't be triggered 
  @dispatch
  def render(self, el: Union[ds.DocstringReturn, ds.DocstringRaise]):
    _UNHANDLED.append(el)
    return "UNHANDLED RETURN"

  # --- Attributes
  @dispatch
  def render(self, el: ds.DocstringAttribute) -> str :
    _UNHANDLED.append(el)
    d = ds_attr.as_dict()
    pn, pa, pd = [d.get(k) for k in ("name", "annotation", "description")]
    # return [pn, self._render_annotation(pa), pd]
    return "UNHANDLED ATTRIBUTE" 

  @dispatch
  def render(self, el: ds.DocstringSectionAttributes):
    header = ["Name", "Type", "Description"]
    rows = []
    for ds_attr in el.value:
      d = ds_attr.as_dict()
      pn, pa, pd = [d.get(k) for k in ("name", "annotation", "description")]
      rows.append([pn, self._render_annotation(pa), pd])
    return tabulate(rows, header, tablefmt="github")

  ## examples ----
  @dispatch
  def render(self, el: ds.DocstringSectionExamples) -> str:
    return super(MdRendererNumpyStyle, self).render(el)
  
  @dispatch
  def render(self, el: ExampleCode) -> str:
    return super(MdRendererNumpyStyle, self).render(el)

  ## Sections ---   
  @dispatch
  def render(self, el: ds.DocstringSectionText):
    return super(MdRendererNumpyStyle, self).render(el)

  @dispatch
  def render(self, el: ds.DocstringSection):
    _UNHANDLED.append(el)
    return "UNHANDLED SECTION"

  @dispatch
  def render(self, el: ExampleText):
    return "```{python}\n" + el.value + "\n```"

  @dispatch
  def render(self, el) -> str:
    #raise NotImplementedError(f"Unsupported type of: {type(el)}")
    _UNHANDLED.append(el)
    import warnings
    warnings.warn(f"Unsupported type of: {type(el)}")
    return ""

