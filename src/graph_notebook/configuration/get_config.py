"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
"""

import json

from graph_notebook.configuration.generate_config import DEFAULT_CONFIG_LOCATION, Configuration, AuthModeEnum, \
    SparqlSection, GremlinSection, Neo4JSection
from graph_notebook.neptune.client import NEPTUNE_CONFIG_HOST_IDENTIFIERS, is_allowed_neptune_host


def get_config_from_dict(data: dict, neptune_hosts: list = NEPTUNE_CONFIG_HOST_IDENTIFIERS) -> Configuration:

    sparql_section = SparqlSection(**data['sparql']) if 'sparql' in data else SparqlSection('')
    gremlin_section = GremlinSection(**data['gremlin']) if 'gremlin' in data else GremlinSection('')
    neo4j_section = Neo4JSection(**data['neo4j']) if 'neo4j' in data else Neo4JSection('', '', True)
    proxy_host = str(data['proxy_host']) if 'proxy_host' in data else ''
    proxy_port = int(data['proxy_port']) if 'proxy_port' in data else 8182

    is_neptune_host = is_allowed_neptune_host(hostname=data["host"], host_allowlist=neptune_hosts)

    if is_neptune_host:
        if gremlin_section.to_dict()['traversal_source'] != 'g':
            print('Ignoring custom traversal source, Amazon Neptune does not support this functionality.\n')
        if neo4j_section.to_dict()['username'] != 'neo4j' or neo4j_section.to_dict()['password'] != 'password':
            print('Ignoring Neo4J custom authentication, Amazon Neptune does not support this functionality.\n')
        config = Configuration(host=data['host'], port=data['port'], auth_mode=AuthModeEnum(data['auth_mode']),
                               ssl=data['ssl'], load_from_s3_arn=data['load_from_s3_arn'],
                               aws_region=data['aws_region'], sparql_section=sparql_section,
                               gremlin_section=gremlin_section, neo4j_section=neo4j_section,
                               neptune_hosts=neptune_hosts)
    else:
        config = Configuration(host=data['host'], port=data['port'], ssl=data['ssl'], sparql_section=sparql_section,
                               gremlin_section=gremlin_section, neo4j_section=neo4j_section, proxy_host=proxy_host,
                               proxy_port=proxy_port)
    return config


def get_config(path: str = DEFAULT_CONFIG_LOCATION,
               neptune_hosts: list = NEPTUNE_CONFIG_HOST_IDENTIFIERS) -> Configuration:
    with open(path) as config_file:
        data = json.load(config_file)
        return get_config_from_dict(data=data, neptune_hosts=neptune_hosts)
