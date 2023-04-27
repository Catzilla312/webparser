# -*- coding: utf-8 -*-
from pymongo import MongoClient
from erichkrause.web_parser import erich_parseProduct
from dotenv import load_dotenv
load_dotenv()
import os


def getProductFromDb():
    print("STARTED WEB PARSER")
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    uri = f"mongodb://{user}:{password}@localhost:27017/{db_name}?authSource=admin&readPreference=primary&directConnection=true&ssl=false"
    client = MongoClient(uri)
    db = client[db_name]
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
            parsedData = erich_parseProduct(product["name"],product["_id"])
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
                    "imageUrl": parsedData.get("imagePathName", ""),
                    }}
                products_collection.update_one(query, new_values)
        except Exception as e:
            print(product["name"],"ERROR = ",e)
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


 #If working with excell file

# workbook = openpyxl.load_workbook('EK.xlsx')
# worksheet = workbook['data']
# data_list = []
# for row in worksheet.iter_rows(min_row=7, min_col=2):
#     cell_value = row[0].value
#     if cell_value:
#         data_list.append(str(cell_value))

# def scrapeProducts():
#     for itemName in data_list:
#         try:
#             parseProduct(itemName)
#         except Exception as e: 
#             print(itemName,"===",e)
#     return "done"   