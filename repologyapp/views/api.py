# Copyright (C) 2016-2017 Dmitry Marakasov <amdmi3@amdmi3.ru>
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

import json
from datetime import timedelta
from typing import Any

import flask

from repologyapp.config import config
from repologyapp.db import get_db
from repologyapp.metapackages import MetapackagesFilterInfo, packages_to_metapackages
from repologyapp.package import PackageDataDetailed, PackageFlags, PackageStatus
from repologyapp.view_registry import Response, ViewRegistrar


def api_v1_package_to_json(package: PackageDataDetailed) -> dict[str, Any]:
    output = {
        field: getattr(package, field) for field in (
            'repo',
            'subrepo',

            'srcname',
            'binname',
            'visiblename',

            'version',
            #'origversion',
            #'status',
            'maintainers',
            #'category',
            #'comment',
            #'homepage',
            'licenses',
        ) if getattr(package, field)
    }

    # XXX: these tweaks should be implemented in core
    if package.comment:
        output['summary'] = package.comment
    if package.category:
        output['categories'] = [package.category]
    if package.flags & PackageFlags.VULNERABLE:
        output['vulnerable'] = True

    output['status'] = PackageStatus.as_string(package.versionclass)
    output['origversion'] = package.rawversion if package.rawversion != package.version else None

    return output


def dump_json(data: Any) -> str:
    if config['PRETTY_JSON']:
        return json.dumps(data, indent=1, sort_keys=True)
    else:
        return json.dumps(data, separators=(',', ':'))


@ViewRegistrar('/api')
@ViewRegistrar('/api/v1')
def api_v1() -> Response:
    return flask.render_template('api.html', per_page=config['METAPACKAGES_PER_PAGE'])


@ViewRegistrar('/api/v1/projects/')
@ViewRegistrar('/api/v1/projects/<bound>/')
def api_v1_projects(bound: str | None = None) -> Response:
    filterinfo = MetapackagesFilterInfo()
    filterinfo.parse_flask_args()

    request = filterinfo.get_request()
    request.set_bound(bound)

    metapackages = get_db().query_metapackages(**request.__dict__, limit=config['METAPACKAGES_PER_PAGE'])

    metapackages = packages_to_metapackages(
        PackageDataDetailed(**item)
        for item in get_db().get_metapackages_packages(list(metapackages.keys()), detailed=True)

    )

    metapackages = {
        metapackage_name: [api_v1_package_to_json(package) for package in packageset]
        for metapackage_name, packageset in metapackages.items()
    }

    return (
        dump_json(metapackages),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/v1/project/<name>')
def api_v1_project(name: str) -> Response:
    return (
        dump_json(
            list(
                api_v1_package_to_json(PackageDataDetailed(**item))
                for item in get_db().get_metapackage_packages(name, detailed=True)
            )
        ),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/v1/repository/<repo>/problems')
def api_v1_repository_problems(repo: str) -> Response:
    return (
        dump_json(get_db().get_problems(repo)),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/v1/maintainer/<maintainer>/problems-for-repo/<repo>')
def api_v1_maintainer_problems(maintainer: str, repo: str) -> Response:
    return (
        dump_json(get_db().get_problems(repo, maintainer)),
        {'Content-type': 'application/json'}
    )


@ViewRegistrar('/api/experimental/distromap')
def api_experimental_distromap() -> Response:
    args = flask.request.args.to_dict()

    expand = bool(args.get('expand'))
    plaintext = args.get('format') == 'plaintext'

    distromap = None

    if expand:
        distromap = get_db().get_distromap_expanded(args.get('fromrepo'), args.get('torepo'))

        if plaintext:
            lines = ['\t'.join(pair) for pair in distromap]
            text = '\n'.join(lines + [''])
            return (text, {'Content-type': 'text/plain'})
    else:
        distromap = get_db().get_distromap(args.get('fromrepo'), args.get('torepo'))

        if plaintext:
            lines = [','.join(fromnames) + '\t' + ','.join(tonames) for fromnames, tonames in distromap]
            text = '\n'.join(lines + [''])
            return (text, {'Content-type': 'text/plain'})

    return (dump_json(distromap), {'Content-type': 'application/json'})


@ViewRegistrar('/api/experimental/updates')
def api_experimental_updates() -> Response:
    return (
        dump_json(
            get_db().get_latest_updates(
                timedelta(days=1),
                None
            )
        ),
        {'Content-type': 'application/json'}
    )


#@ViewRegistrar('/api/v1/history/repository/<repo>')
#def api_v1_maintainer_problems():
#    get_db().GetRepositoriesHistoryPeriod(seconds = 365
#    return (
#        dump_json(get_db().GetProblems(maintainer=maintainer)),
#        {'Content-type': 'application/json'}
#    )


#@ViewRegistrar('/api/v1/history/statistics')
#def api_v1_maintainer_problems(repo):
#    return (
#        dump_json(get_db().GetProblems(maintainer=maintainer)),
#        {'Content-type': 'application/json'}
#    )
