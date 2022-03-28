from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

save_path = r"D:\scraped_csv_files"

options = Options()
options.add_argument("start-maximized")

# Clear through popups or ads before clicks
def clear_click(element):
    try:
        popup = driver.find_element_by_xpath("//*[@id='PromoteSignUpPopUp']/div[2]/i")
        popup.click()
        adbox = driver.find_element_by_id("closeIcon")
        adbox.click()
    except:
        pass
    element.click()

#Generate csv files from current webpage
def get_csv():         
        hist = WebDriverWait(driver,30).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Historical Data"))
        )
        hist.click()

        date_pick = driver.find_element_by_id("flatDatePickerCanvasHol")
        clear_click(date_pick)
        input_date = driver.find_element_by_id("startDate")
        input_date.clear()
        input_date.send_keys("02/27/2008")
        hit_apply = driver.find_element_by_id("applyBtn")
        hit_apply.click()
        main = WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.ID, "curr_table"))
            )
        df = pd.DataFrame(columns=['Month','Date','Year','Price','Open','High','Low','Vol'])
        rows = driver.find_element_by_id("curr_table").find_elements_by_tag_name("tr")
        for yr in range(1,len(rows)):
            sry=[]
            trs = rows[yr].text
            trlist = trs.split(' ')
            for i in range(8):
                sry.append(trlist[i])
            df.loc[yr-1] = sry
        df['day']=df['Month'] + str(" ") + df['Date'] + str(" ") + df['Year']
        df.drop(['Month','Date','Year'], axis=1, inplace=True)

        for k in df.index:
            volume = df['Vol'][k]
            vol1 = volume[-1:]
            vol2 = volume[:-1]
            if vol1=="K":
                df['Vol'][k] = float(vol2)*1000
            elif vol1=="M":
                df['Vol'][k] = float(vol2)*1000000

        filename = driver.find_element_by_xpath("//*[@id='quotes_summary_current_data']/div[2]/div[4]/span[2]")
        filepath = str(save_path) + str('\\') + (filename.text) + str (".csv")
        print (filepath)
        df.to_csv(filepath)
        
#Initialize selenium driver
PATH = r"C:\Users\ASUS\Downloads\chromedriver.exe"
s = Service(PATH)
driver = webdriver.Chrome(chrome_options=options, service=s)
driver.get('https://www.investing.com/equities/bangladesh')
main_table = WebDriverWait(driver,30).until(
    EC.presence_of_element_located((By.ID, "cross_rate_markets_stocks_1"))
)

#Find outbound links
links = main_table.find_elements_by_tag_name("a")
total_links = len(links)
hrefs=[]
for link in links:
    hrefs.append(link.get_attribute('href'))
print("The list of links:", hrefs)

# MASTER: Loop through all the links and launch one by one
for h in hrefs:
    driver.get(h)
    time.sleep(5)
    get_csv()