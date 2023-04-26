# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
import openpyxl
from pymongo import MongoClient

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

def parseProduct(itemName):
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
                                    valid_filename = "".join([c if c.isalnum() else "_" for c in itemName]).rstrip("_")
                                    with open('erichkrause/{}.jpg'.format(valid_filename), 'wb') as f:
                                        f.write(response.content)

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

productsList = [
    "Цветные карандаши шестигранные ErichKrause® 24 цвета",
]

workbook = openpyxl.load_workbook('EK.xlsx')
worksheet = workbook['data']
data_list = []

for row in worksheet.iter_rows(min_row=7, min_col=2):
    cell_value = row[0].value
    if cell_value:
        data_list.append(str(cell_value))

def scrapeProducts():
    for itemName in data_list:
        try:
            parseProduct(itemName)
        except Exception as e: 
            print(itemName,"===",e)
    return "done"    


def getProductFromDb():
    print("STARTED WEB PARSER")
    user = "AdminMono"
    password = "123123123"
    uri = f"mongodb://{user}:{password}@localhost:27017/kanzler?authSource=admin&readPreference=primary&directConnection=true&ssl=false"
    client = MongoClient(uri)
    db = client["kanzler"]
    products_collection  = db["products"]
    webScraper_collection  = db["WebScraper"]
    products = products_collection.find({"found": False})
    count = products_collection.count_documents({"found": False})

    scraperLog = {
        "status": "parsing",
        "errorMessage": "",
        "productsToParse": count,
        "productsFound": 0,
    }

    if count == 0:
        scraperLog["errorMessage"] = "no Products to Parse"
        scraperLog["status"]       = "error"
 
    #create
    resuscraperLog = webScraper_collection.insert_one(scraperLog)
    #update
    listOfErrors = [];
    foundCount = 0
    for product in products:
        try:
            parsedData = parseProduct(product["name"])
            query = {"_id": product["_id"]}
            if parsedData['found']:
                foundCount +=1
                new_values = {"$set": {
                    "found": parsedData["found"],
                    "trademark": parsedData.get("trademark", ""),
                    "description": parsedData.get("description", ""),
                    "model": parsedData.get("model", ""),
                    "collection": parsedData.get("collection", ""),
                    "format": parsedData.get("format", ""),
                    "color": parsedData.get("color", ""),
                    "pages": parsedData.get("pages", ""),
                    "lockType": parsedData.get("lockType", ""),
                    "size": parsedData.get("size", ""),
                    "surfaceTexture": parsedData.get("surfaceTexture", ""),
                    "thickness": parsedData.get("thickness", ""),
                    "transparrency": parsedData.get("transparrency", ""),
                    "suspensionType": parsedData.get("suspensionType", ""),
                    "gender": parsedData.get("gender", ""),
                    "countryOfManufacture": parsedData.get("countryOfManufacture", ""),
                    }}
                products_collection.update_one(query, new_values)
        except Exception as e:
            listOfErrors.append({
                "name":product["name"],
                "error":e
            })


    logerQuery = {"_id": resuscraperLog.inserted_id}
    logerNew_values = {"$set": {
                    "productsFound": foundCount,
                    "status": "done",
                    "errorMessage":listOfErrors
                    }}

    webScraper_collection.update_one(logerQuery, logerNew_values)