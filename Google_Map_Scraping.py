import time
import random
import warnings
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait    
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def Random_Delay():
	# 生成介於1到5之間的隨機浮點數
	delay = random.uniform(1, 5)
	
	# 等待隨機時間
	time.sleep(delay)
    
def Progress_Bar(bar_name, temp, total):
	print('\r' + f'{bar_name}：[%s%s]%.2f%%' % (
	'■' * int(temp*20/total), ' ' * (20-int(temp*20/total)),
	float(temp/total*100)), end='')
    
def Search_Store_Name(driver, store_name):
	# 抓取搜尋欄的XPath
	Search = WebDriverWait(driver,10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]'))
		)
	Random_Delay()
 
	# 輸入店家名稱到搜尋欄
	Search.send_keys(store_name)
 
	# 按下Enter
	Search.send_keys(Keys.ENTER)
    
def Search_Store_URL(driver, store_url):
	# 讀取網頁
	driver.get(store_url)
    
def Get_Store_Info(driver):
	try:
		store_info = {}
 
		info_list = WebDriverWait(driver,10).until(
				EC.presence_of_all_elements_located((By.CLASS_NAME, 'CsEnBe'))
			)
 
		# 抓取店家名稱的Class_Name，並且讀取裡面的文字
		store_info['Name'] = WebDriverWait(driver,10).until(
				EC.presence_of_element_located((By.CLASS_NAME, 'DUwDvf'))
			).text
 
		# 抓取店家電話的Class_Name，並且讀取裡面的文字
		store_info['Tel'] = [value.find_element(By.CLASS_NAME, 'Io6YTe').text for value in info_list if "電話號碼" in value.get_attribute('aria-label')]
 
		# 判斷店家是否有提供電話資料
		if len(store_info['Tel']) > 0:
			store_info['Tel'] = store_info['Tel'][0].replace(' ','')
		else: 
			store_info['Tel'] = 'None'
 
		# 抓取店家地址的Class_Name，並且讀取裡面的文字
		store_info['Address'] = [value.find_element(By.CLASS_NAME, 'Io6YTe').text for value in info_list if "地址" in value.get_attribute('aria-label')][0]
 
		print(f"店家名稱：{store_info['Name']}")
		print(f"店家電話：{store_info['Tel']}")
		print(f"店家地址：{store_info['Address']}")
		return store_info
 
	except TimeoutException:
		# 抓取店家網址的Class_Name
		store_link = driver.find_elements(By.CLASS_NAME, 'hfpxzc')
 
		# 判斷是否有抓到店家網址
		if len(store_link) > 0:
			# 取得店家網址連結
			store_link = store_link[0].get_attribute('href')
			Search_Store_URL(driver, store_link)
		else:
			# 抓取店家資訊總攬的Class_Name，並且點擊
			store_index = driver.find_elements(By.CLASS_NAME, 'LRkQ2')[0].click()
		return Get_Store_Info(driver)

def Review_Counts(driver):
	# 抓取評論區的XPath，並且點擊
	review_area = WebDriverWait(driver,10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]'))
		).click()
	Random_Delay()
	try:
		# 抓取店家評論總數的Class_Name，並且讀取裡面的文字
		counts = WebDriverWait(driver, 10).until(
			EC.presence_of_all_elements_located((By.CLASS_NAME, 'fontBodySmall'))
		)
		
	except StaleElementReferenceException:
		# 執行網頁重新整理
		driver.refresh()
		counts = WebDriverWait(driver, 10).until(
			EC.presence_of_all_elements_located((By.CLASS_NAME, 'fontBodySmall'))
		)
	counts = [value.text for value in counts if "篇評論" in value.text][0].replace(',', '').split(' ')[0]
	print(f"目前{store_info['Name']}總共有 {counts} 則評論！")
	return counts

def Scrolling(driver, total_counts, counts):
	print('正在爬取評論中...')
	
	# 抓取卷軸的Class_Name
	scrollable_div = driver.find_elements(
		By.CLASS_NAME, 'm6QErb DxyBCb kA9KIf dS8AEf ')
	
	prev_review_count = 0
	
	# 根據counts去滑動卷軸
	for i in range(int(counts)):
		scrolling = driver.execute_script(
			'document.getElementsByClassName("dS8AEf")[0].scrollTop = document.getElementsByClassName("dS8AEf")[0].scrollHeight',
			scrollable_div
		)        
		Random_Delay()
		
		# 檢查評論數量是否有增加
		current_review_count = len(driver.find_elements(By.CLASS_NAME, 'jftiEf'))
		while current_review_count == prev_review_count:
			# 判斷是否已讀取到最大評論數
			if current_review_count >= int(total_counts):
				break
			else:
				current_review_count = len(driver.find_elements(By.CLASS_NAME, 'jftiEf'))
		prev_review_count = current_review_count
		Progress_Bar('卷軸滾動進度', i+1, int(counts))
	print('\n', end='\r')

def Get_Review(driver, counts):
	# 抓取每一則顯示完整評論的Class_Name
	full_reviews = WebDriverWait(driver,10).until(
			EC.presence_of_all_elements_located((By.CLASS_NAME, 'w8nwRe'))
		)
 
	# 點開每一則被摺疊的評論
	for index, full_review in enumerate(full_reviews):
			full_review.click()
			Progress_Bar('展開全文進度', int(index+1), len(full_reviews))
	print('\n', end='\r')
 
	# 抓取每一則評論的整個Div區塊的Class_Name
	review_div = WebDriverWait(driver,10).until(
			EC.presence_of_all_elements_located((By.CLASS_NAME, 'jftiEf'))
		)
	review_data = []
 
	# 抓取每一則評論資料的Class_Name，並且讀取裡面的文字
	for index, data in enumerate(review_div):
		# 抓取每一則評論者的姓名
		name = data.find_element(By.CLASS_NAME, 'd4r55').text
		
		# 抓取每一則評論內容的Class_Name
		review = data.find_elements(By.CLASS_NAME, 'MyEned')
		
		# 判斷該評論是否為空值，是的話就用'None'取代
		if len(review) > 0:
			review = review[0].find_element(By.CLASS_NAME, 'wiI7pd').text
		else:            
			review = 'None'
		
		# 抓取每一則評論星數的Class_Name，並且取得aria-label的值
		score = data.find_element(By.CLASS_NAME, 'kvMYJc').get_attribute("aria-label")
		
		# 將每一則評論資訊存入review_data
		review_data.append([name , review, score[0]])
		
		# 判斷是否已達到指定的評論數量
		if len(review_data) >= int(counts):
			Progress_Bar('評論爬取進度', len(review_data), int(counts))
			break
		Progress_Bar('評論爬取進度', len(review_data), int(counts))
	print(f"\n已爬取完{len(review_data)}則評論！")
	return review_data

def Write_To_CSV(data):
	cols = ["Name", "Review", 'Score']
	df = pd.DataFrame(data, columns=cols)
	df.to_csv(f"{store_info['Name']}.csv", index=False, encoding='utf-8-sig')
	print('已成功將評論匯出成CSV檔！')

def Driver_Setting():
	# 設定使用者資料
	headers = {"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71"}
 
	#創建一個設定Chrome瀏覽器的物件
	option = webdriver.ChromeOptions()
 
	# 排除日誌記錄
	option.add_experimental_option('excludeSwitches', ['enable-logging'])
 
	# 使用Chromium作為瀏覽器的引擎
	option.use_chromium = True
 
	# 讓瀏覽器在背景執行
	#option.add_argument('--headless')
 
	# 設定瀏覽器
	driver = webdriver.Chrome(ChromeDriverManager().install(),options = option)
 
	# 讀取網頁
	driver.get('https://www.google.com/maps')
	return driver

driver = Driver_Setting()
input_store = input('輸入店家名稱或網址：')
print('正在搜尋店家中...')
if "https://" in str(input_store):
	Search_Store_URL(driver, input_store)
else:
	Search_Store_Name(driver, input_store)
Random_Delay()
 
# 爬取店家資訊
store_info = Get_Store_Info(driver)
Random_Delay()
 
#爬取店家評論數量
total_counts = Review_Counts(driver)
input_counts = input('請輸入要爬取的評論數量：')
 
while int(input_counts) > 1000:
	print('要爬取的評論數不能超過1000則！')
	input_counts = input('請輸入要爬取的評論數量：')
	
# 拉動卷軸
Scrolling(driver, total_counts, int(int(input_counts)/10)+1)
 
# 抓取評論資料
review_data = Get_Review(driver, input_counts)
 
# 關閉瀏覽器
driver.close()
 
# 將抓取的評論會出成CSV檔
Write_To_CSV(review_data)

