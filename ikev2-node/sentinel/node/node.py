# coding=utf-8
import json
from urllib.request import urlopen

from speedtest_cli import Speedtest

from ..config import CONFIG_DATA_PATH
from ..db import db


class Node(object):
    def __init__(self, config):
        self.speed_test = Speedtest()
        self.ip = None
        self.location = None
        self.net_speed = {
            'best_server': {
                'host': None,
                'latency': None
            },
            'download': None,
            'upload': None
        }
        self.config = {
            'account_addr': None,
            'price_per_gb': None,
            'token': None,
            'moniker': '',
            'description': '',
        }
        self.version = '0.0.2-alpha'

        if config is not None:
            self.config['account_addr'] = str(
                config['account_addr']).lower() if 'account_addr' in config else None
            self.config['price_per_gb'] = float(
                config['price_per_gb']) if 'price_per_gb' in config else None
            self.config['token'] = str(
                config['token']) if 'token' in config else None
            self.config['moniker'] = str(
                config['moniker']) if 'moniker' in config else ''
            self.config['description'] = str(
                config['description']) if 'description' in config else ''

        self.update_node_info({'type': 'location'})
        self.update_node_info({'type': 'net_speed'})
        self.save_to_db()

    def save_to_db(self):
        db.node.update({
            'account_addr': self.config['account_addr']
        }, {
            '$set': {
                'ip': self.ip,
                'location': self.location,
                'net_speed': self.net_speed,
                'price_per_gb': self.config['price_per_gb'],
                'token': self.config['token'],
                'moniker': self.config['moniker'],
                'description': self.config['description'],
            }
        }, upsert=True)

    def save_config_data(self):
        data_file = open(CONFIG_DATA_PATH, 'w')
        data = json.dumps(self.config)
        data_file.writelines(data)
        data_file.close()

    def update_node_info(self, info=None):
        if info['type'] == 'location':
            web_url = 'http://ip-api.com/json'
            response = json.load(urlopen(web_url))
            self.ip = str(response['query'])
            self.location = {
                'city': str(response['city']),
                'country': str(response['country']),
                'latitude': float(response['lat']),
                'longitude': float(response['lon'])
            }
        elif info['type'] == 'net_speed':
            self.speed_test.get_best_server()
            self.net_speed['best_server'] = {
                'host': self.speed_test.best['host'],
                'latency': self.speed_test.best['latency']
            }
            self.net_speed['download'] = self.speed_test.download()
            self.net_speed['upload'] = self.speed_test.upload()
        elif info['type'] == 'config':
            if ('account_addr' in info) and (info['account_addr'] is not None):
                self.config['account_addr'] = info['account_addr']
            if ('token' in info) and (info['token'] is not None):
                self.config['token'] = info['token']
            if ('moniker' in info) and (info['moniker' is not None]):
                self.config['moniker'] = info['moniker']
            if ('description' in info) and (info['description' is not None]):
                self.config['description'] = info['description']
            self.save_config_data()
        self.save_to_db()
