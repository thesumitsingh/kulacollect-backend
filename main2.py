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
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional

app=FastAPI()

class UrlForScraping(SQLModel):
    url:str

class ZaubaItem(SQLModel, Table=True):
    id:str=""
    name:str=""
    link:str=""
    location:str=""
    status:str=""
    otherDetails:str=""
    email:str=""
    address:str=""

class ItemSet(SQLModel):
    pagesJson: List[ZaubaItem]


@app.get("/scrapezaubaaiohttp")
async def slow_route(zaubaUrl: UrlForScraping):
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
                    i+=1
            finaljson=json.dumps(dictofcompanies)
            return {"pagesJson":json.loads(finaljson)}


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
                # return "inside the sessions"
                data = await resp.text()
                print("received the page")
                doc = BeautifulSoup(data, "html.parser")
                contactdetailstext=doc.find(class_="col-12").find(class_="col-lg-6 col-md-6 col-sm-12 col-xs-12").text
                i.otherDetails=contactdetailstext
                i.address=contactdetailstext.split("Address:")[1]
                email = re.findall(r"[a-zA-Z0-9\.\-+_]+@[a-zA-Z0-9\.\-+_]+\.[a-zA-Z]+", contactdetailstext)
                i.email=email
                # # match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', contactdetailstext)
                # # print(match.group(0))
                print(email)
                # i+=1
    return inputjson


