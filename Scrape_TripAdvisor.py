from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import csv


# we are web scraping the U.S. landmark information from 
# "https://www.tripadvisor.com/Attractions-g191-Activities-oa0-United_States.html"


# move scroll bar
def scroll_window(driver, stop_length=0, step_length=8000):
    driver.execute_script(f'window.scrollBy(0,{step_length});')
    time.sleep(2)


def get_wineshop_list(url):
    driver.get(url)
    scroll_window(driver)
    js = 'window.open("")'
    driver.execute_script(js)
    # next_url=url
    for i in range(10000):
        print("The number of the scraped data=================",i)
        with open("page.txt","w") as f:
            f.write(str(i))
        driver.switch_to.window(driver.window_handles[0])
        scroll_window(driver)
        allowEllipsis_list = driver.find_elements(By.CLASS_NAME, "hZuqH")
        url_list=[]
        for allowEllipsis in allowEllipsis_list:
            url_list.append(allowEllipsis.find_element(By.TAG_NAME,"a").get_attribute("href"))

        driver.switch_to.window(driver.window_handles[1])
        for url in url_list:
            content_list=[]
            driver.get(url)
            scroll_window(driver)
            # get the title
            try:
                title = driver.find_element(By.TAG_NAME, "h1").text
                print("Name============", title)
            except:
                title = "NULL"
                print("Name============", title)
            # get rating
            content_list.append(title)
            try:
                grade = driver.find_element(By.CLASS_NAME, "yFKLG").find_element(By.CLASS_NAME, "biGQs").text
                print("Rating============：", grade)
            except:
                grade = 'NULL'
                print("Rating============：", grade)
            content_list.append(grade)
            # get landmark
            try:
                landmark = driver.find_element(By.CLASS_NAME, "aVUMb").find_element(By.CLASS_NAME, "fIrGe").text
                # split stings
                landmark_list = landmark.split("•")
                # define landmarks type
                tourism_type = landmark_list[-2]
                print("Type============", tourism_type)
                # define landmarks type2
                tourism_type_one = landmark_list[-1]
                print("Type1============", tourism_type_one)
            except:
                tourism_type = "NULL"
                tourism_type_one = "NULL"
                print("Type============", tourism_type)
                print("Type1============", tourism_type_one)
            content_list.append(tourism_type)
            content_list.append(tourism_type_one)
            # get the open hours for landmark
            try:
                open_time = driver.find_element(By.CLASS_NAME, "EIVzV").find_element(By.CLASS_NAME, "EFKKt").text
                print("Hours============", open_time)
            except:
                open_time = "NULL"
                print("Hours============", open_time)
            content_list.append(open_time)
            # get the landmark description
            try:
                brief = driver.find_element(By.CLASS_NAME, "IxAZL").find_element(By.CLASS_NAME, "pZUbB").text
                print("About============", brief)
            except:
                brief = "NULL"
                print("About============", brief)
            content_list.append(brief)
            # get duration suggestion
            try:
                suggested_duration = driver.find_element(By.CLASS_NAME, "IxAZL").find_element(By.CLASS_NAME, "_c").text
               print("suggest_duration============", suggested_duration)
            except:
                suggested_duration = "NULL"
                print("suggest_duration============", suggested_duration)
            content_list.append(suggested_duration)
            # get the image address
            try:
                src = driver.find_element(By.CLASS_NAME, "Kxegy").find_element(By.TAG_NAME, "img").get_attribute("src")
                print("ImageURL============", src)
            except:
                src = "NULL"
                print("ImageURL============", src)
            content_list.append(src)
            # get landmark address
            try:
                address = driver.find_element(By.CLASS_NAME, "wgNTK").find_element(By.CLASS_NAME, "XWJSj").text
                print("Address===========", address)
            except:
                address = "NULL"
                print("Address============", address)
            content_list.append(address)
            # get guide to the landmark
            try:
                there = driver.find_element(By.CLASS_NAME, "AqkGs").text
                print("Guide==========", there)
            except:
                there = "NULL"
                print("Guide==========", there)
            content_list.append(there)
            with open('data.csv', 'a', newline="") as f:
                writer = csv.writer(f)
                writer.writerow(content_list)

        driver.switch_to.window(driver.window_handles[0])
        if i==0:

            driver.execute_script('document.getElementsByClassName("BrOJk u j z _F wSSLS tIqAi unMkR")[0].click()')
        else:
            driver.execute_script('document.getElementsByClassName("BrOJk u j z _F wSSLS tIqAi unMkR")[1].click()')


def run():
    # Website: Tripadvisor, Page: Things to Do in United States
    get_wineshop_list("https://www.tripadvisor.com/Attractions-g191-Activities-oa0-United_States.html")


if __name__ == '__main__':
    option = Options()
    # option.add_argument("--headless")
    # option.add_argument('--disable-gpu')
    # option.add_argument("--window-size=4000,1600")
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument('--disable-blink-features=AutomationControlled')
    driver = Chrome(executable_path="chromedriver", options=option)
    
    # Save result to csv files
    with open('data.csv', 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ['Name', 'Rating', 'Type', 'Type1', 'Hours', 'About', 'suggest_duration', "ImageURL", "Address", "Guide"
             ])
    run()
