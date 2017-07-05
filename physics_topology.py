#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
models
"""

import time
from mongoengine import (
    Document, StringField, BooleanField, IntField,
    DateTimeField, ReferenceField, CASCADE, FloatField
)


class PhysicsTopologyNode(Document):
    """
    docstring for PhysicsTopologyNode
    """
    x = FloatField()
    y = FloatField()

    name = StringField()        # 节点名称（主机名称，交换机名称)
    host_id = StringField()     # 节点的host_id
    node_ip = StringField()     # node deploy ip
    node_type = StringField()   # host_type的8位字典

    linked  = StringField()    # be single node
    weight = IntField(default=10)   # default 10, 10-100
    # timestamp = DateTimeField()
    version = IntField()
    # author = StringField()

    server_date = IntField(required=True, default=int(time.time() * 1000))
    public_date = IntField(required=True, default=int(time.time() * 1000))
    latest_date = IntField(required=True, default=int(time.time() * 1000))

    meta = {
        'collection' : 'phytopology_node',
        'ordering': ['-timestamp'],

        'indexes': [
            'host_id'
        ]
    }


class PhysicsTopologyLink(Document):
    """
    docstring for PhysicsTopologyLink
    """

    source = ReferenceField(PhysicsTopologyNode, required=True, reverse_delete_rule=CASCADE)
    source_node_id = StringField()
    source_node_ip = StringField()
    source_node_if_id = StringField()
    source_node_ifname = StringField()
    source_node_ifspeed = IntField(default=-1)
    source_node_ifstatus = StringField(default="down")

    target = ReferenceField(PhysicsTopologyNode, required=True, reverse_delete_rule=CASCADE)
    target_node_id = StringField()
    target_node_ip = StringField()
    target_node_if_id = StringField()
    target_node_ifname = StringField()
    target_node_ifspeed = IntField(default=-1)
    target_node_ifstatus = StringField(default="down")
    target_node_ifip = StringField()
    target_node_ifmac = StringField()

    # timestamp = DateTimeField()
    version = IntField()
    # author = StringField(default='')

    server_date = IntField(required=True, default=int(time.time() * 1000))
    public_date = IntField(required=True, default=int(time.time() * 1000))
    latest_date = IntField(required=True, default=int(time.time() * 1000))

    meta = {
        'collection' : 'phytopology_link',
        'ordering': ['-timestamp'],

        'indexes': [
            ('source_node_id', 'source_node_if_id', 'target_node_id', 'target_node_if_id')
        ]
    }
