from typing import Iterator
from pymongo import MongoClient
import requests
import lxml.html
import time


def main():
    """
    クローラー
    """
    client = MongoClient('localhost', 27017)
    db = client.scraping
    collection = db.support_cards
    collection.delete_many({})

    # 複数ページをクロールする場合、Sessionを使う
    with requests.Session() as session:
        response = session.get('https://gamewith.jp/uma-musume/article/show/255035')
        support_cards = scrape_list_page(response)
        for support_card in support_cards:
            time.sleep(1.5)
            response = session.get(support_card['url'])
            detail_response = session.get(support_card['url'])
            print(support_card)
            support_card = scrape_detail_page(support_card, detail_response)
            print(support_card)
            collection.insert_one(support_card)
            break  # まず１回で止める


"""
Iterator:イテレータはデータの集団に対し順番にアクセスしていくためのオブジェクト
str関数は文字列に変換する
リストとイテレータの違いはこんな感じ

リスト
0番目：田中さん
1番目：佐藤さん
2番目：鈴木さん

イテレータ
最初は田中さん
田中さんの次は佐藤さん
佐藤さんの次は鈴木さん
鈴木さんは最後

# 関数アノテーション(->のところ)はあくまで注釈なので型が違ってもエラーにならないので注意
"""


def scrape_list_page(response: requests.Response) -> Iterator[dict]:
    html = lxml.html.fromstring(response.text)
    # 相対パスを絶対パスに変換
    html.make_links_absolute(response.url)

    # テーブル行の最初にヒットしたリンクだけ取得
    for a in html.cssselect('#article-body > div.w-instant-database-list > div > table.sorttable > tr > td > a:first-child'):
        # Aタグからテキストを取る
        print(a.text_content())

        umamusume = a.text_content()
        url = a.get('href')
        # yieldが含まれる関数をジェネレータとよび反復利用（ループ処理が可能）
        yield {'umamusume': umamusume, 'url': url}


def scrape_detail_page(support_card, response: requests.Response) -> dict:
    html = lxml.html.fromstring(response.text)
    html.make_links_absolute(response.url)

    columns = ['lv30','lv35','lv40','lv45', 'lv50']
    # サポート効果（適宜調整がいる部分）
    SUPPORT_WORKS = {
        'good_rate': '得意率',
        'friendship_bonus': '友情ボーナス',
        'intention_work': 'やる気効果',
        'training_work': 'トレーニング効果',
        'initial_power': '初期パワー',
        'race_bonus': 'レースボーナス',
        'fan_bonus': 'ファン数ボーナス',
        'hint_level': 'ヒントLv',
        'hint_rate': 'ヒント発生率',
        'power_bonus': 'パワーボーナス',
        'initial_ties': '初期絆ゲージ',
    }

    # article-body > div.uma_bonus_table > table > tbody > tr:nth-child(10) > th
    bonuses = []
    row_index = 0
    for record in html.cssselect('#article-body > div.uma_bonus_table > table > tr:not(:first-child)'):
        row_key = record.cssselect('th')[0].text
        bonus = {}
        bonus["name"] = row_key
        for i in range(0, 4):
            bonus[columns[i]] = html.cssselect(f'#article-body > div.uma_bonus_table > table > tr:nth-child({row_index + 2}) > td:nth-child({i + 2})')[0].text
        bonuses.append(bonus)

        row_index = row_index + 1
    card = {
        'url': response.url,
        'umamusume': support_card['umamusume'],
        'rarity': html.cssselect('#article-body > table:nth-child(14) > tr:nth-child(1) > td > span > a')[0].text_content(), # レア
        'another_name': html.cssselect('#article-body > table:nth-child(14) > tr:nth-child(3) > td')[0].text,
        'bonus': bonuses
    }
    return card


# 関数前後にアンダースコア２つ付けるとマジックメソッド(特殊メソッド)に
# if __name__ == '__main__':は
# python ファイル名.pyのコマンドで呼ばれたときだけ実行するようになります
# import xxxで実行されても動かなくなります
if __name__ == '__main__':
    main()
