# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import openpyxl
from pymongo import MongoClient
import os

baseUrlErik = "https://www.erichkrause.com"
info_labels = [
    ('Торговая марка:', 'trademark'), 
    ('Описание:', 'description'), 
    ('Модель:', 'model'), 
    ('Коллекция:', 'collection'), 
    ('Формат:', 'format'), 
    ('Цвет:', 'color'),
    ('Вместимость, листов:', 'pages'),
    ('Тип замка:', 'lockType'),
    ('Тип печати:', 'printType'),
    ('Размер, мм:', 'size'),
    ('Текстура поверхности:', 'surfaceTexture'),
    ('Толщина, мм:', 'thickness'),
    ('Прозрачность:', 'transparrency'),
    ('Наличие подвеса:', 'suspensionType'),
    ('Пол:', 'gender'),
    ('Страна производства:', 'countryOfManufacture'),
    ]

def erich_parseProduct(itemName,productId):
    # clear the name, replace all spaces with one
    itemName = re.sub(r'\s+', ' ', itemName)
    url="https://www.erichkrause.com/search/?search_cat=&q={}".format(itemName)
    session = requests.Session()
    page = session.get(url, verify=True)
    soup = BeautifulSoup(page.text, 'html.parser')
    search_result = soup.find(class_="catalog__title").text
    itemData = {
        "found":False,
        "name":itemName,
        "itemSKU":itemName,
        "imagePathName":""
    }
    # check if we got result
    if 'Результаты поиска' in search_result:
        allFound = soup.find_all(class_="catalog__item-block")

        if len(allFound)>0:
            for foundItem in allFound:
                foundItemName = foundItem.find("a", {"class": "catalog__item-title"})
                if itemName == re.sub(r'\s+', ' ', foundItemName.string):
                    itemAHref = foundItem.find("a", {"class": "catalog__item-img"})
                    if itemAHref == None:
                        return
                    itemHref = itemAHref['href']
                    if itemHref:
                        itemPageUrl=baseUrlErik+itemHref
                        itemPage = session.get(itemPageUrl, verify=True)
                        itemSoup = BeautifulSoup(itemPage.text, 'html.parser')

                        # get and check item SKU

                        itemtitleTags = itemSoup.findAll('h1', {'class': 'catalog__title'})
                        for itemh1 in itemtitleTags:
                            tempItemName = re.sub(r'\s+', ' ', itemh1.string)
                            
                            if tempItemName == itemName:
                                sku_attrs = {attr: value for attr, value in itemh1.attrs.items() if attr.startswith('data-sku-id')}
                                sku =  [key for key in sku_attrs][0]
                                itemData["itemSKU"] = sku

                                # itemSKU will be the id to check

                                itemData['found'] = True

                                itemImage = itemSoup.select_one('a[{}].slider-big__item'.format(itemData["itemSKU"]))

                                # download image
                                if itemImage:
                                    img_url = itemImage['href']
                                    response = requests.get(baseUrlErik+img_url)
                                    # valid_filename = "".join([c if c.isalnum() else "_" for c in itemName]).rstrip("_")
                                    os.makedirs('../erichkrause_public', exist_ok=True)
                                    with open('../erichkrause_public/{}.jpg'.format(productId), 'wb') as f:
                                        f.write(response.content)
                                        itemData["imagePathName"] = f'erichkrause_public/{productId}.jpg'
                                # get other info

                                infoContainer = itemSoup.select_one('div[{}].catalog__about'.format(itemData["itemSKU"]))
                                if infoContainer:
                                    infoContainerActive = infoContainer.select_one('div.catalog__about-item:not(._active)')
                                    if infoContainerActive:
                                        for label, key in info_labels:
                                            row = infoContainerActive.find('td', string=label)
                                            if row:
                                                itemData[key] = row.find_next('td').string

    return itemData