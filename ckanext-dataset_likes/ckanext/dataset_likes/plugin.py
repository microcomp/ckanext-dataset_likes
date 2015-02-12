import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import like
import ckan.logic
import ckan.model as model
from ckan.common import _, c
import logging

class DatasetLikesPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=False)

    controller = 'ckanext.dataset_likes.like:LikesController'
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
    def before_map(self, map):
        map.connect('like_dataset', '/dataset/like', action='LikeDataset', controller=self.controller)
        map.connect('dislike_dataset', '/dataset/dislike', action='DisLikeDataset', controller=self.controller)
        return map
    def get_helpers(self):
    	return {'sum': like.summary,
                'liked': like.liked}
