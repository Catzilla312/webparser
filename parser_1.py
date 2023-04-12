# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
baseUrlErik = "https://www.erichkrause.com"
# itemName="Zip-пакет пластиковый ErichKrause® Avocado Dusk, Travel (в пакете по 12 шт.)"

def parseProduct(itemName):

    # clear the name, replace all spaces with one
    itemName = re.sub(r'\s+', ' ', itemName)

    print("STARTED")
    url="https://www.erichkrause.com/search/?search_cat=&q={}".format(itemName)
    session = requests.Session()
    page = session.get(url, verify=True)
    soup = BeautifulSoup(page.text, 'html.parser')
    search_result = soup.find(class_="catalog__title").text
    itemData = {
        "found":False,
        "name":itemName,
    }
    # check if we got result
    if 'Результаты поиска' in search_result:
        firstFound = soup.find(class_="catalog__item-block")
        if firstFound:
            itemHref = firstFound.find("a", {"class": "catalog__item-img"})['href']
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
                            with open('erichkrause/{}.jpg'.format(itemName), 'wb') as f:
                                f.write(response.content)


                        # get other info

                        infoContainer = itemSoup.select_one('div[{}].catalog__about'.format(itemData["itemSKU"]))
                        if infoContainer:
                            infoContainerActive = infoContainer.select_one('div.catalog__about-item:not(._active)')
                            if infoContainerActive:
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

                                for label, key in info_labels:
                                    row = infoContainerActive.find('td', string=label)
                                    if row:
                                        itemData[key] = row.find_next('td').string

    print(itemData)

productsList = [
    "Zip-пакет пластиковый ErichKrause® Avocado Dusk, B5 (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Avocado Dusk, Travel (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Cute Animals, B5, ассорти (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Dreamy Girls, A4, ассорти (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Dreamy Girls, B5, ассорти (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Dreamy Girls, Travel, ассорти (в пакете по 12 шт.)",
    "Zip-пакет пластиковый ErichKrause® Tulips, Travel (в пакете по 12 шт.)",
    "Антистеплер с фиксатором ErichKrause® Elegance черный (в коробке по 1 шт.)",
    "Чернографитный шестигранный карандаш ErichKrause® Grafica 100 HB (в коробке по 12 шт.)",
    "Фломастеры Erichkrause® Washable 18 цветов",
]

for itemName in productsList:
    parseProduct(itemName)