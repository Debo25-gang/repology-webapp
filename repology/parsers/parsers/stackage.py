# Copyright (C) 2017-2018 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of repology
#
# repology is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# repology is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with repology.  If not, see <http://www.gnu.org/licenses/>.

import lxml.html

from repology.parsers import Parser


class StackageHTMLParser(Parser):
    def iter_parse(self, path, factory):
        for row in lxml.html.parse(path).getroot().xpath('.//div[@class="packages"]/table/tbody/tr'):
            pkg = factory.begin()

            pkg.set_name_and_version(row.xpath('./td[1]/a')[0].text)
            pkg.set_summary((row.xpath('./td[2]')[0].text or '').replace('\n', ' '))

            yield pkg
