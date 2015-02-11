# coding=utf-8
import urllib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import ckan.model as model
import ckan.logic as logic
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as df
import ckan.plugins as p
from ckan.common import _, c, g
#import ckan.lib.app_globals.Globals as g
import ckan.plugins.toolkit as toolkit

import time
import uuid
import likes_db
import logging
import ckan.logic
import __builtin__

def create_dataset_likes_table(context):
    if likes_db.dataset_likes_table is None:
        likes_db.init_db(context['model'])

@ckan.logic.side_effect_free
def in_like_db(context, data_dict):
    create_dataset_likes_table(context)
    res = likes_db.DatasetLikes.getAll(**data_dict)
    if res:
    	for i in res:
    		if i.user_id == data_dict['user_id']:
        		return {'is':True, 'type':res[0].type}

    return {'is':False, 'type':''}

@ckan.logic.side_effect_free
def mod_like(context, data_dict):
    create_dataset_likes_table(context)
    res = likes_db.DatasetLikes.getAll(**data_dict)
    if res[0].type == 'like':
        res[0].type = 'dislike'
    else:
        res[0].type = 'like'
    res[0].save()
    session = context['session']
    #session.add(info)
    session.commit()
    return {"status":"success"}

@ckan.logic.side_effect_free
def new_like(context, data_dict):
    tester = in_like_db(context, data_dict)
    if tester['is'] == False:
        info = likes_db.DatasetLikes()
        info.id = unicode(uuid.uuid4()) 
        info.user_id = data_dict['user_id']
        info.dataset_id = data_dict['dataset_id']
        info.type = 'like'
        info.save()
        session = context['session']
        session.add(info)
        session.commit()
        return {"status":"success"}
    else:
        if tester['type'] == 'dislike':
        	mod_like(context, data_dict)
        return {"status":"fail"}

@ckan.logic.side_effect_free
def new_dis_like(context, data_dict):
    tester = in_like_db(context, data_dict)
    if tester['is'] == False:
        info = likes_db.DatasetLikes()
        info.id = unicode(uuid.uuid4()) 
        info.user_id = data_dict['user_id']
        info.dataset_id = data_dict['dataset_id']
        info.type = 'like'
        info.save()
        session = context['session']
        session.add(info)
        session.commit()
        return {"status":"success"}
    else:
        if tester['type'] == 'like':
            mod_like(context, data_dict)
        return {"status":"fail"}


@ckan.logic.side_effect_free
def get_likes(context, data_dict):
    if likes_db.dataset_likes_table is None:
        likes_db.init_db(context['model'])
    res = likes_db.DatasetLikes.get(**data_dict)
    return res
def summary(dataset_id):
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
    data_dict = {'dataset_id':dataset_id}
    if likes_db.dataset_likes_table is None:
        likes_db.init_db(context['model'])
    res = likes_db.DatasetLikes.getAll(**data_dict)
    likes = 0
    dislikes = 0
    for i in res:
    	if i.type == 'like':
    		likes+=1
    	else:
    		dislikes+=1
    sum = likes+dislikes
    return str(likes/sum)

class LikesController(base.BaseController):

    def LikeDataset(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        dataset_id = base.request.params.get('dataset_id','')
        user_id = base.request.params.get('user_id','')

        data_dict = {'dataset_id':dataset_id,'user_id':user_id}
        new_like(context, data_dict)
        return h.redirect_to(controller='package', action='read', id=dataset_id)

    def DisLikeDataset(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        dataset_id = base.request.params.get('dataset_id','')
        user_id = base.request.params.get('user_id','')
        data_dict = {'dataset_id':dataset_id,'user_id':user_id}
        new_dis_like(context, data_dict)
        return h.redirect_to(controller='package', action='read', id=dataset_id)