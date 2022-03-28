import requests_html
from . import model
session = requests_html.HTMLSession()
domain = 'https://rent.591.com.tw'
headers = {
    'user-agent': 'Mozilla/5.0',
    'x-csrf-token': '8CAFjE3G3fAAPouIPWrvRWs9Y7el9fxCJQ90wRUZ'
}


def update_csrf_token(domain=domain, session=session, headers=headers):
    '''更新headers中帶的x-csrf-token'''
    print('--- update_csrf_token ---')
    resp = session.get(domain, headers={'user-agent': 'Mozilla/5.0',})
    headers['x-csrf-token'] = resp.html.find('meta[name="csrf-token"]', first=True).attrs.get('content')
    print(resp)
    print('headers: ', headers)


def get_json(url, params, session=session, headers=headers):
    '''將取得的資料轉為dict回傳，若遇到419則更新csrf-token後重試'''
    resp = session.get(url, params=params, headers=headers)
    if resp.status_code == 419:
        update_csrf_token()
        resp = session.get(url, params=params, headers=headers)
    print(resp, url, params)
    return resp.json()


def get_list(region, domain=domain, endpoints='/home/search/rsList', early_break=True, max_page=None):
    '''取得指定region的清單'''
    last_data = model.House.query.filter_by(regionid=region).order_by(model.House.ltime.desc()).first()
    total_page = max_page or 0
    result = {}
    page = 1
    # 迴圈抓取每一頁
    while page < total_page:
        params = {'region': region, 'firstRow': (page-1)*30, 'order': 'posttime', 'orderType': 'desc'}
        data = get_json(domain+endpoints, params=params)
        # 抓取清單
        result = {**result, **{
                d['post_id']: {
                    'post_id': d['post_id'],
                    'regionid': d['regionid'],
                    'region_name': d['region_name'],
                    'price': d['price'],
                    'unit': d['unit'],
                    'section_name': d['section_name'],
                    'street_name': d['street_name'],
                    'address': d['address'],
                    'room_str': d['roomStr'],
                    'closed': d['closed'],
                    'linkman': d['linkman'],
                    'role_name': d['role_name'],
                    'layout': d['layout'],
                    'floorStr': d['floorStr'],
                    'kind_name': d['kind_name'],
                    'ltime': d['ltime'],
                } for d in data['data']['data']
            }
        }
        if early_break and last_data and last_data.post_id in result:
            break

        # 讀取總頁數
        total_page = max_page or int(page.find('a.pageNext', first=True).attrs.get('data-total'))
        # 準備爬下一頁
        page += 1
    # 回傳結果
    return result


def get_detail(post_id):
    '''讀取指定資源，整理格式後回傳'''
    # 讀資料
    result = get_json(
        'https://bff.591.com.tw/v1/house/rent/detail',
        params={'id': post_id},
        headers={
            'device': 'pc',
            'deviceid': session.cookies.get_dict()['PHPSESSID'],
            **headers
        }
    )
    # 取得需要的欄位
    return {
        'deposit': result['data']['deposit'],
        'imName': result['data']['linkInfo']['imName'],
        'mobile': result['data']['linkInfo']['mobile'],
        'rule': result['data']['service']['rule'],
    }


if __name__ == '__main__':
    lst_data = {}
    detail_data = []

    # 更新 cookies
    update_csrf_token()

    # 讀取[台北、新北]清單
    print('--- get_list ---')
    for region in [1, 3]:
        lst_data = {**lst_data, **get_list()}

    # 排除已經存在於DB的資料
    exists_data = model.House.query.filter(model.House.post_id._in(lst_data.keys())).all()
    exists_data = [data.post_id for data in exists_data]
    lst_data = {key: value for key, value in lst_data if key not in exists_data}

    # 逐一讀取詳細內容
    print('--- get_detail ---')
    for post_id, data in lst_data.items():
        detail = get_detail(post_id)
        detail_data.append(model.House(**data, **detail))

    # 寫入資料庫
    print('--- commit ---')
    model.db.session.add_all(detail_data)
    model.db.session.commit()
    print('success.')
