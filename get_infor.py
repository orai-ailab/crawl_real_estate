from decimal import *
import requests
from bs4 import BeautifulSoup
import requests, json, urllib, random, time
from pymongo import MongoClient
from datetime import datetime
from threading import Thread

def get_info(link, conn):
    try:
        # init data
        data = {}
        html = requests.get(link).content
        soup = BeautifulSoup(html, 'html.parser')
        # district
        try:
            dis = soup.find('nav', class_='mt-3 custom-breadcrumbs').find_all('li')[3].text.strip()
            data['district'] = dis
        except:
            data['district'] = None
        # link_url
        data['link_url'] = link
        # get all information
        info = soup.find('div', {"id": "article-wrapper"})
        # get link images
        try:
            images = info.find('div', class_='single-property-media').find_all('a')
            link_img = []
            for i in images:
                link_img.append(i.find('img', class_='single-property-media__image')['src'])
            link_img = list(dict.fromkeys(link_img))
            data['link_image'] = link_img
        except:
            data['link_image'] = []
        # get title
        try:
            title = info.find('div', class_='property-header').find('h1').text.strip()
            data['title'] = title
        except:
            data['title'] = None
        # get address
        try:
            address = info.find('div', class_='property-header').find('div', class_='mt-3 property-header__address').text.split(':')[1].strip()
            data['address'] = address
        except:
            data['address'] = None
        # init real estate features
        real_estate_features = {
            "type_of_house": None,
            "acreage": None,
            "juridical": None, # Pháp lý , thường thuê nhà thì trường này hay để none
            "facede": None,
            "interior": None,
            "number_of_floors": None,
            "number_of_toilets": None,
            "number_of_bedrooms": None,
            "price": None,
            "price/acreage": None,
            "road_width_in_front_of_house": None,
            "the_direction_of_the_house": None
        }
        # cal price
        try:
            price_and_acreage = info.find('div', class_='property-section is-info').find_all('div', class_='col-6 col-md-3 col-auto')
            price = price_and_acreage[0].find_all('p')
            for i in price:
                if '/m2' in i.text:
                    real_estate_features['price/acreage'] = i.text
                else :
                    real_estate_features['price'] = i.text
        except:
            real_estate_features['price/acreage'] = None
            real_estate_features['price'] = None

        # get full bio
        try:
            bio = info.find('div', class_='mt-4 single-property-content').find('div', class_='position-relative overflow-hidden single-property-content__wrap js-single-property-content').text.strip()
            data['bio'] = bio
        except:
            data['bio'] = None
        # get type sale
        try:
            type_sale = info.find('div', class_='mt-2 property-header__meta').find('span', class_='bg-success text-white rounded-pill py-1 px-2').text
            data['type_sale'] = type_sale
        except:
            data['type_sale'] = None
        # cal time post
        try:
            data_submitted = info.find('div', 'mt-2 property-header__meta').find('span', class_='d-flex gap-1 align-items-center small text-gray property-header__date').text.strip()
            date_now = datetime.today().strftime('%Y-%m-%d')
            dd_now = int(date_now.split('-')[2])
            mm_now = int(date_now.split('-')[1])
            yy_now = int(date_now.split('-')[0])
            if "giờ" in data_submitted or "phút" in data_submitted:
                data['data_submitted'] = date_now
            elif "ngày" in data_submitted:
                dd_last = int(data_submitted.split(' ')[0])
                if dd_now - dd_last < 0:
                    if mm_now == 1:
                        data['data_submitted'] = str(yy_now - 1)+'-'+str(12)+'-'+str(30 - (dd_last - dd_now))
                    else:
                        data['data_submitted'] = str(yy_now)+'-'+str(mm_now - 1)+'-'+str(30 - (dd_last - dd_now))
                elif dd_now == dd_last:
                    data['data_submitted'] = str(yy_now)+'-'+str(mm_now)+'-'+str(1)
                else:
                    data['data_submitted'] = str(yy_now)+'-'+str(mm_now)+str(dd_last-dd_now)
            elif "tuần" in data_submitted:
                week_num = int(data_submitted.split(" ")[0])
                dd_by_week = week_num * 7
                if dd_now - dd_by_week < 0:
                    if mm_now == 1:
                        data['data_submitted'] = str(yy_now - 1)+'-'+str(12)+'-'+str(30 - (dd_by_week - dd_now))
                    else:
                        data['data_submitted'] = str(yy_now)+'-'+str(mm_now - 1)+'-'+str(30 - (dd_by_week - dd_now))
                elif dd_now == dd_by_week:
                    data['data_submitted'] = str(yy_now)+'-'+str(mm_now)+'-'+str(1)
                else:
                    data['data_submitted'] = str(yy_now)+'-'+str(mm_now)+str(dd_by_week-dd_now)
            elif "tháng" in data_submitted:
                mm_by_year = int(data_submitted.split(" ")[0])
                if mm_now - mm_by_year < 0:
                    data['data_submitted'] = str(yy_now -1)+'-'+str(12 - (mm_by_year - mm_now))+'-'+str(dd_now)
                elif mm_by_year == mm_now:
                    data['data_submitted'] = str(yy_now)+'-'+str(1)+'-'+str(dd_now)
                else:
                    data['data_submitted'] = str(yy_now)+'-'+str(mm_now - mm_by_year)+'-'+str(dd_now)
                        
            elif "năm" in data_submitted:
                yy = int(data_submitted.split(" ")[0])
                data['data_submitted'] = str(yy_now - yy)+'-'+str(mm_now)+'-'+str(dd_now)
        except:
            data['data_submitted'] = None
        # get other information
        details = info.find('div', class_='mt-4 property-section property-detail')
        other_information = details.find('div', class_='row property-section__detail').find_all('div', class_='col col-12 col-md-6 mt-2 property-section__detail__col')
        for i in other_information:
            key = i.find('span', class_='property-section__detail__title').text.strip()
            value = i.find('span', class_='pl-2 fw-bold property-section__detail__value').text.strip()
            if key == 'Mặt tiền':
                real_estate_features['facede'] = value
            if key == 'Diện tích':
                real_estate_features['acreage'] = value
            if key == 'Số tầng':
                real_estate_features['number_of_floors'] = value
            if key == 'Phòng ngủ':
                real_estate_features['number_of_bedrooms'] = value
            if key == 'Loại hình BĐS':
                real_estate_features['type_of_house'] = value
            if key == 'Phòng tắm':
                real_estate_features['number_of_toilets'] = value
            if key == 'Pháp lý':
                real_estate_features['juridical'] = value
            if key == 'Đường trước nhà':
                real_estate_features['road_width_in_front_of_house'] = value
            if key == 'Hướng nhà':
                real_estate_features['the_direction_of_the_house'] = value
            if key == 'Thời gian thuê':
                real_estate_features['lease_time'] = value
        # get furniture
        try:
            furniture = details.find_all('div', class_='row')[1].find_all('div', class_='col-12 mt-3')
            for i in furniture:
                key = i.find('p', class_='fw-bold d-inline-block mb-2').text
                value = i.find('div', class_='bg-light p-2 rounded').text
                if key == 'Nội thất':
                    real_estate_features['interior'] = value
        except:
            real_estate_features['interior'] = None
        # get public utility
        try:
            location_near = info.find('div', class_='mt-4 property-location-places').find_all('span')
            public_utility = []
            for i in location_near:
                public_utility.append(i.text)
            real_estate_features['public_utility'] = public_utility
        except:
            real_estate_features['public_utility'] = []
        data['real_estate_features'] = real_estate_features
        # get phone
        phone = soup.find('div', {"id": "article-sidebar"}).find('a', class_='btn position-relative d-flex pe-none justify-content-between btn-block link-light btn-danger profile-contact__phone-link js-phone-number')['data-number']
        data['phone'] = phone
        data['link_map'] = 'https://www.google.com/maps/place/'+address.replace(" ", "+")

        #insert to DB
        db = conn.BDS_NestStock
        collection = db.information
        collection.insert_one(data)
    except:
        print("Lỗi")
        pass

def run():
    try:
        conn = MongoClient("mongodb://127.0.0.1:27017")
        print("Connected successfully!!!")
        links = open('links_duli_thue.txt', 'r', encoding='utf-8')
        links = links.read().splitlines()
        lenght = len(links)
        num_thread = 10
        i = 0
        while i < lenght:
            for j in range(num_thread):
                thread = Thread(target=get_info, args=(links[i+j], conn, ))
                thread.start()
                thread.join()
            i+=num_thread
            print("--------------Done "+str(i)+' links -----------------')
    except:
        print("Could not connect to MongoDB")
run()
