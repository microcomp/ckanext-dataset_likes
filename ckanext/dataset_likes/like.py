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
def IsRes(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'related_id': id}
    resource = model.Session.query(model.Resource) \
                .filter(model.Resource.id == id).first()

    return resource != None
def create_dataset_likes_table(context):
    if likes_db.dataset_likes_table is None:
        likes_db.init_db(context['model'])

@ckan.logic.side_effect_free
def in_like_db(context, data_dict):
    create_dataset_likes_table(context)
    if data_dict['user_id'] == None or data_dict['user_id'] == '':
        return {'is':False, 'type':''}
    res = likes_db.DatasetLikes.get(**data_dict)
    if res:
        for i in res:
            if i.user_id == data_dict['user_id']:
                return {'is':True, 'type':i.type}

    return {'is':False, 'type':''}
    
def liked(user_id, dataset_id):
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
    data_dict = {'dataset_id':dataset_id, 'user_id':user_id}
    result = in_like_db(context, data_dict)
    return result

@ckan.logic.side_effect_free
def mod_like(context, data_dict):
    create_dataset_likes_table(context)
    res = likes_db.DatasetLikes.get(**data_dict)[0]
    if res.type == 'like':
        res.type = 'dislike'
    else:
        res.type = 'like'
    res.save()
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
    res = likes_db.DatasetLikes.get(**data_dict)
    likes = 0
    dislikes = 0
    for i in res:
    	if i.type == 'like':
    		likes+=1
    	else:
    		dislikes+=1
    users = model.Session.query(model.User).filter(model.User.name != '').all()
    users = len(users)
    return {'val':likes, 'max':users}
def fromUsers(dataset_id):
    context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
    data_dict = {'dataset_id':dataset_id, 'type':"like"}
    if likes_db.dataset_likes_table is None:
        likes_db.init_db(context['model'])
    res = likes_db.DatasetLikes.get(**data_dict)

    uIDs = [x.user_id for x in res]
    logging.warning(uIDs)
    return {'uIDs':uIDs, 'val':len(uIDs)}
def IsApp(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author, 'auth_user_obj': c.userobj,
               'for_view': True}
    data_dict = {'related_id': id}
    related = model.Session.query(model.Related) \
                .filter(model.Related.id == id).first()
    if related != None:
        return True
    return False
class LikesController(base.BaseController):

    def LikeDataset(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        dataset_id = base.request.params.get('dataset_id','')

        if context['auth_user_obj']: 
            user_id = context['auth_user_obj'].id
        else:
            base.abort(401, base._('Not authorized to see this page'))

        comment_id = base.request.params.get('comment_id','')
        logging.warning('data dict...')
        if len(comment_id) <= 0 or comment_id == None:
            data_dict = {'dataset_id':dataset_id,'user_id':user_id}
        else:
            data_dict = {'dataset_id':comment_id,'user_id':user_id}

        try:
            logic.check_access('app_create', context, data_dict)
        except logic.NotFound:
            base.abort(404, base._('Dataset not found'))
        except logic.NotAuthorized:
            base.abort(401, base._('Not authorized to see this page'))

        new_like(context, data_dict)

        if IsApp(dataset_id) == True:
            return h.redirect_to(controller='ckanext.applications.detail:DetailController', action='detail', id=dataset_id)
        else:
            if IsRes(dataset_id):
                resource = model.Session.query(model.Resource).filter(model.Resource.id == dataset_id).all()[0].resource_group_id
                dts_id = model.Session.query(model.ResourceGroup).filter(model.ResourceGroup.id == resource).all()[0].package_id
                return h.redirect_to(controller='package', action='resource_read', id=dts_id ,resource_id=dataset_id)
            else:
                return h.redirect_to(controller='package', action='read', id=dataset_id)
            

    def DisLikeDataset(self):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj,
                   'for_view': True}
        dataset_id = base.request.params.get('dataset_id','')
        user_id = context['auth_user_obj'].id
        comment_id = base.request.params.get('comment_id','')
        if len(comment_id) <= 0 or comment_id == None:
            data_dict = {'dataset_id':dataset_id,'user_id':user_id}
        else:
            data_dict = {'dataset_id':comment_id,'user_id':user_id}

        logging.warning(context)
        try:
            logic.check_access('app_create', context, data_dict)
        except logic.NotFound:
            base.abort(404, base._('Dataset not found'))
        except logic.NotAuthorized:
            base.abort(401, base._('Not authorized to see this page'))
        new_dis_like(context, data_dict)
        
        if IsApp(dataset_id) == True:
            return h.redirect_to(controller='ckanext.applications.detail:DetailController', action='detail', id=dataset_id)
        else:
            if IsRes(dataset_id):
                resource = model.Session.query(model.Resource).filter(model.Resource.id == dataset_id).all()[0].resource_group_id
                dts_id = model.Session.query(model.ResourceGroup).filter(model.ResourceGroup.id == resource).all()[0].package_id
                return h.redirect_to(controller='package', action='resource_read', id=dts_id ,resource_id=dataset_id)
            else:
                return h.redirect_to(controller='package', action='read', id=dataset_id)

