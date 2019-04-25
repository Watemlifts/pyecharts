# coding=utf-8
import re

from jinja2 import Environment

from pyecharts.commons.types import Any, Optional

from ..commons.utils import write_utf8_html_file
from ..datasets import EXTRA, FILENAMES
from ..globals import CurrentConfig


class RenderEngine:
    def __init__(self, env: Optional[Environment] = None):
        self.env = env or CurrentConfig.GLOBAL_ENV

    @staticmethod
    def generate_js_link(chart: Any) -> Any:
        if not chart.js_host:
            chart.js_host = CurrentConfig.ONLINE_HOST
        links = []
        for dep in chart.js_dependencies.items:
            # TODO: if?
            if dep in FILENAMES:
                f, ext = FILENAMES[dep]
                links.append("{}{}.{}".format(chart.js_host, f, ext))
            else:
                for url, files in EXTRA.items():
                    if dep in files:
                        f, ext = files[dep]
                        links.append("{}{}.{}".format(url, f, ext))
                        break
        chart.dependencies = links
        return chart

    def render_chart_to_file(self, template_name: str, chart: Any, path: str):
        """
        Render a chart or page to local html files.

        :param chart: A Chart or Page object
        :param path: The destination file which the html code write to
        :param template_name: The name of template file.
        """
        tpl = self.env.get_template(template_name)
        html = tpl.render(chart=self.generate_js_link(chart))
        write_utf8_html_file(path, self._reg_replace(html))

    def render_chart_to_template(self, template_name: str, chart: Any):
        tpl = self.env.get_template(template_name)
        html = tpl.render(chart=self.generate_js_link(chart))
        return self._reg_replace(html)

    def render_chart_to_notebook(self, template_name: str, **kwargs) -> str:
        tpl = self.env.get_template(template_name)
        html = tpl.render(**kwargs)
        return self._reg_replace(html)

    @staticmethod
    def _reg_replace(html):
        return re.sub(r'\\n|\\t|"?__-o-__"?', "", html)
