from fastapi import FastAPI, Query
from enum import Enum
from typing import Union,List
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import json
import asyncio
from requests_html import AsyncHTMLSession
import aiohttp
import re
import pytest
from sqlmodel import Field, Session, SQLModel, create_engine, select, delete
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ZaubaItem(BaseModel):
    id:str =""
    name:str=""
    link:str=""
    location:str=""
    status:str=""
    otherDetails:str=""
    email:str=""
    address:str=""


class ZaubaItemDBModel(SQLModel, table=True):
    id:str = Field(default="", primary_key=True)
    name:str=""
    link:str=""
    location:str=""
    status:str=""
    otherDetails:str=""
    email:str=""
    address:str=""

class ItemSet(SQLModel):
    pagesJson: List[ZaubaItem]

# class Hero(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     secret_name: str
#     age: Optional[int] = None

# hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
# hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
# hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)

engine=create_engine("sqlite:///database.db")

SQLModel.metadata.create_all(engine)

headers2 = {
    'accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
    'Accept-Language': 'en-US,en;q=0.9,it;q=0.8,es;q=0.7',
    'referer': 'https://www.google.com/',
}


class ModelName(str, Enum):
    alexnet="alexnet"
    resnet="resnet"
    lenet="lenet"

class Item(BaseModel):
    name:str
    description:Union[str,None]
    price:float
    tax: Union[float,None]

class UrlForScraping(SQLModel):
    url:str

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/deletefullzaubadb")
async def deletefromzaubadb():
    with Session(engine) as session:
        statement=delete(ZaubaItemDBModel)
        results=session.exec(statement)
        # finalres=results.first()
        # session.delete(finalres)
        session.commit()
    return "done"

#for this endpoint give a URL like https://www.zaubacorp.com/company-list/roc-RoC-Delhi-company.html in Postman
# make sure to go to Body ->raw-> choose json type. then for the second endpoint, copy the response body of this api and paste in the body of next one
@app.post("/scrapezaubaaiohttp")
async def scrapezaubaaiohttp(zaubaUrl: UrlForScraping):
    await deletefromzaubadb()
    async with aiohttp.ClientSession() as session:
        print("went inside")
        async with session.get(zaubaUrl.url, headers=headers2) as resp:
            print("got further inside")
            data = await resp.text()
            print("received the page")
            doc = BeautifulSoup(data, "html.parser")
            # print(doc.prettify())
            res=doc.find(class_ = "table table-striped col-md-12 col-sm-12 col-xs-12").find_all("tr")
            i=0
            for row in res:
                if(len(row.find_all("td"))>0):
                    elements=row.find_all("td")
                    i+=1
            i=0
            dictofcompanies=[]
            for row in res:
                if(len(row.find_all("td"))>0):
                    elements=row.find_all("td")
                    id=elements[0].text
                    name=elements[1].text
                    link=elements[1].find("a")["href"]
                    location=elements[2].text
                    if(len(elements)>3):
                        status=elements[3].text
                    else:
                        status=""
                    # status=(elements[3].text!=None elements[3].text:"")
                    dictofcompanies.append({"id":id,"name":name, "link":link, "location":location, "status":status})
                    with Session(engine) as session:
                        currentitem=ZaubaItemDBModel(id=id,name=name,link=link, location=location,status=status,otherDetails="",email="",address="")
                        session.add(currentitem)
                        print("added row",id)
                        session.commit()
                    i+=1
            finaljson=json.dumps(dictofcompanies)
            return {"pagesJson":json.loads(finaljson)}

@app.get("/showfullzaubadb")
async def showzaubadb():
    with Session(engine) as session:
        statement=select(ZaubaItemDBModel)
        result=session.exec(statement)
        finalres=result.all()
        return finalres



@app.post("/scrapemultiplezauba")
async def scrapeMultiplePages(inputjson:ItemSet):
    # return inputjson.pagesJson[0].id
    inputjson=inputjson.pagesJson
    i=0
    # return inputjson.pagesJson
    for i in inputjson:
        print(i.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(i.link, headers=headers2) as resp:
                # return "hi"
                data = await resp.text()
                print("received the page")
                doc = BeautifulSoup(data, "html.parser")
                contactdetailstext=doc.find(class_="col-12").find(class_="col-lg-6 col-md-6 col-sm-12 col-xs-12").text
                i.otherDetails=contactdetailstext
                i.address=contactdetailstext.split("Address:")[1]
                email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", contactdetailstext)
                if(len(email)>0):
                    email=email[0]
                i.email=email
                # # match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', contactdetailstext)
                # # print(match.group(0))
                print(email)
                # i+=1
    return inputjson


@app.post("/scrapemultiplezaubaandsave")
async def scrapeMultiplePages(inputjson:ItemSet):
    # return inputjson.pagesJson[0].id
    inputjson=inputjson.pagesJson
    i=0
    # return inputjson.pagesJson
    for i in inputjson:
        print(i.id)
        async with aiohttp.ClientSession() as session:
            async with session.get(i.link, headers=headers2) as resp:
                # return "hi"
                data = await resp.text()
                print("received the page")
                doc = BeautifulSoup(data, "html.parser")
                contactdetailstext=doc.find(class_="col-12").find(class_="col-lg-6 col-md-6 col-sm-12 col-xs-12").text
                otherDetails=contactdetailstext
                address=contactdetailstext.split("Address:")[1]
                email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", contactdetailstext)
                if(len(email)>0):
                    email=email[0]
                else:
                    email=""
                with Session(engine) as dbsession:
                        statement=select(ZaubaItemDBModel).where(ZaubaItemDBModel.id==i.id)
                        result=dbsession.exec(statement).first()
                        result.email=email
                        result.otherDetails=otherDetails
                        result.address=address
                        dbsession.add(result)
                        print("updated row",i.id, email)
                        dbsession.commit()
                # # match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', contactdetailstext)
                # # print(match.group(0))
                print(email)
                # i+=1
    return inputjson
    

@app.get("/scrapezauba2")
async def zaubascraper(zaubaUrl: UrlForScraping):
    return await scraper(zaubaUrl.url)


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    with Session(engine) as session:
        stmt=select(Hero).where(Hero.name=="Deadpond")
        hero=session.exec(stmt).first()
        print(hero,"--------")
    if q:
        item.update({"q": q}) #item.update gives you ability to add a fields in the JSON
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

def test_answer():
    assert read_item(3) == 5

@app.get("/itemsquery")
async def read_items(q: str = Query(default="fixedquery", min_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.get("/itemsquery2")
async def read_items(
    q: Union[str, None] = Query(default=None, title="Query string", min_length=3)
):
    results = {"items": [{"item_id": "Foo"}, {"item_id2": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@app.post('/postitems/{itemno}')
async def createitem(item: Item, itemno:int, itemno2:Union[int,None]=44):
    itemdict=item.dict()
    return {"itemdict":itemdict, "itemno":itemno,"itemno2":itemno2}

@app.get('/{itemid}')
async def root(itemid:int):
    total="yoyoyo" + str(itemid)
    return {"message":"hello alll"+total}

@app.get('/models/{modelname}')
async def modeltown(modelname : ModelName):
    if modelname is ModelName.alexnet:
        return {"modelname":modelname, "message":"AlexNet Deep Learning FTW"}
    if modelname.value == "lenet":
        return {"modelname":modelname, "message":" LeNet - LeCNN all the images"}
    return {"message":modelname,  "Message":"resnet - Have some residuals"}        

@app.get("/items")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]



@app.get("/items2/{itemid}--{itemno}")
async def showit(itemid,itemno):
    return({"message": str(itemid+itemno)})


def answer(x):
    return (x+10)

def test_answer():
    assert answer(5) == 15
