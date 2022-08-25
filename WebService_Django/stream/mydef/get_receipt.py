# 함수 모음
import pandas as pd 

# csv 파일을 호출하는 함수
def call_csv(path = './mydef/item_list.csv'):
    item_list = pd.read_csv(path)

    return item_list

# csv 파일에서 이름, 가격정보를 찾아 반환하는 함수
def call_info(key, item_file):
    name = item_file.loc[item_file['key'] == key]['name']
    name = name.item()

    cost = item_file.loc[item_file['key'] == key]['cost']
    cost = int(cost.item())

    return name, cost


# 전체 영수증 정보 (아이템 목록, 수량, 개당 가격, 전체 가격, 총 결제 금액)를 딕셔너리 형태로 반환하는 함수
def get_receipt(key_list):

    item_list = call_csv()
    # 아이템들의 수량을 계산
    cart_dict = {}
    for key in key_list:
        if key in cart_dict:
            cart_dict[key] += 1
        else:
            cart_dict[key] = 1

    # total receipt라는 dict에 구매 정보 저장
    sum = 0
    total_receipt = {}

    for key in cart_dict:
        ls = []
        # name, cost = cc.call_info(key, item_list)
        name, cost = call_info(key, item_list)

        sum += ( cost*cart_dict[key])
        ls = [name, cost, cart_dict[key], cost*cart_dict[key]]
        total_receipt[str(key)] = ls

    total_receipt['sum'] = sum

    return total_receipt