import json
from flask.views import MethodView
from flask import Response
from flask import request
from . import model
import math


def check_input(input_dic):
    role_name = input_dic.get('role_name')
    rule = input_dic.get('rule')
    if role_name not in ['代理人', '屋主', '仲介']:
        return {
            'role_name': f'"{role_name}" is not allow.'
        }
    out_rule = set(rule) - set(['限女生', '限男生', '不可養寵物', '不可開伙', '男女皆可租住'])
    if out_rule:
        return {
            'rule': f'"{out_rule}" is not allow.'
        }
    return {}

class HouseSpaceView(MethodView):
    def get(self):
        '''file: ./spec/house_list.yaml'''
        page = request.args.get('page')
        region = request.args.get('region')
        role_name = request.args.get('role_name')
        im_gender = request.args.get('im_gender')
        rules = request.args.get('rule')
        mobile = request.args.get('mobile')
        if not page.isdigit() or int(page) <= 0:
            return {
                'page': '輸入錯誤'
            }
        # 篩選內容
        queryset = model.House.query
        if region:
            queryset = queryset.filter(model.House.region_name == role_name)
        if im_gender:
            queryset = queryset.filter(model.House.imName.like(f'%{im_gender}'))
        if rules:
            for rule in rules.split(','):
                queryset = queryset.filter(model.House.rule.like(f'%{rule}%'))
        if mobile:
            queryset = queryset.filter(model.House.mobile == mobile)
        # 計算分頁
        paginate = queryset.paginate(int(page), 10, False)
        total_pages = math.ceil(queryset.count() / 10)
        results = [obj.to_dict() for obj in paginate.items]
        # 返回
        return {
            'total_pages': total_pages,
            'results': results
        }

    def post(self):
        '''file: ./spec/house_create.yaml'''
        # 檢查是否重複新增
        post_id = request.json.get('post_id')
        obj_is_exists = model.House.query.filter(model.House.post_id == post_id).first()
        if obj_is_exists:
            return {
                'post_id': f'object "{post_id}" is already exists.'
            }
        # 檢查欄位enum是否錯誤
        error_dic = check_input(request.json)
        if error_dic:
            return error_dic
        # 調整rule欄位
        obj = request.json
        obj['rule'] = '，'.join(obj['rule'])
        # 新增
        obj = model.House(**obj)
        model.db.session.add(obj)
        model.db.session.commit()
        # 回傳結果
        return Response(
            json.dumps(obj.to_dict(), ensure_ascii=False),
            status=201,
            mimetype='application/json'
        )

class HouseDetailView(MethodView):
    def get(self, post_id):
        '''file: ./spec/house_retrieve.yaml'''
        obj = model.House.query.filter(model.House.post_id == post_id).first()
        if not obj:
            return {
                'post_id': f'object "{post_id}" is not exists.'
            }
        return obj.to_dict()

    def put(self, post_id):
        '''file: ./spec/house_update.yaml'''
        # 查詢目標
        obj = model.House.query.filter(model.House.post_id == post_id).first()
        if not obj:
            return {
                'post_id': f'object "{post_id}" is not exists.'
            }

        # 檢查欄位enum是否錯誤
        error_dic = check_input(request.json)
        if error_dic:
            return error_dic
        # 所有欄位逐一取代
        for k, v in request.json.items():
            setattr(obj, k, v)
        # 保存
        model.db.session.add(obj)
        model.db.session.commit()
        return obj.to_dict()

    def patch(self, post_id):
        '''file: ./spec/house_particial_update.yaml'''
        # 查詢目標
        obj = model.House.query.filter(model.House.post_id == post_id).first()
        if not obj:
            return {
                'post_id': f'object "{post_id}" is not exists.'
            }

        # 檢查欄位enum是否錯誤
        error_dic = check_input(request.json)
        if error_dic and (error_dic.keys() & request.json.keys()):
            return {k: v
                for k, v in error_dic.items() 
                if k in request.json.keys()}
        # 所有欄位逐一取代
        for k, v in request.json.items():
            if v is None:
                continue
            setattr(obj, k, v)
        # 保存
        model.db.session.add(obj)
        model.db.session.commit()
        return obj.to_dict()

    def delete(self, post_id):
        '''file: ./spec/house_delete.yaml'''
        # 查詢目標
        obj = model.House.query.filter(model.House.post_id == post_id).first()
        if not obj:
            return {
                'post_id': f'object "{post_id}" is not exists.'
            }
        model.db.session.delete(obj)
        model.db.session.commit()
        return Response('', status=204)
