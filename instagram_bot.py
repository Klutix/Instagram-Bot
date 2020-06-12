from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
#--------------------------------------------------------------
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#---------------------------------------------------------------
import sqlite3
from CONFIG import * #user configuration file
import configparser #using this for results.. may switch config to this

import datetime
import os
import time





class instagram_automation:
    def __init__(self, profile_path = ''): #path is hardcoded for windows
        #Chrome Driver Setup---------------------------------------------
        #options create options to handle profiles and or headless
        self._chrome_options = Options()
        
        #chrome driver hardcoded to current path
        self.chromedriver = "chromedriver.exe"
        
        #set the environment
        os.environ["webdriver.chrome.driver"] = self.chromedriver

        #make headless
        #self._chrome_options.add_argument('--remote-debugging-port=9222')
        #self._chrome_options.add_argument("--headless")
        #self._chrome_options.add_argument("--disable-gpu") # needed for headless
        #self._chrome_options.add_argument("window-size=1200x600");
        #self._chrome_options.add_argument("--disable-extensions")
    
        #add the profile to options
        self._chrome_options.add_argument('--profile-directory=Default')
        self._chrome_options.add_argument("user-data-dir={path}".format(path = profile_path))
        
        #create the bot driver
        self.driver = webdriver.Chrome(self.chromedriver, options = self._chrome_options)

        try:
            self.conn = sqlite3.connect('db_instagram_data.db')
            self.c = self.conn.cursor()
        except sqlite3.Error:
            print ("Error open db.\n")
            exit()

        try:
            #set up two tables Questions and jobs applied to
            self.c.execute('''CREATE TABLE tblUrlsVisted 
             (url text)''')
            print("Created Anser Table")

            # Save (commit) the changes
            self.conn.commit()
            print("Tables Created")
        except:
            print("Tables already exist")

            #ok setup the results varaiables
            self.likes = 0
            self.skips = 0
            self.grabbed = 0
            self.lph = 0
            self.ltd = 0
            
    def __del__(self):
        self.driver.close()
 

    def create_results_file(self):
        print("Creating results file: Results.ini")
        date = datetime.datetime.now()
        config = configparser.ConfigParser()
        config['Results_{}'.format(date)] = {}
        config['Results_{}'.format(date)]['DATE'] = str(date)
        config['Results_{}'.format(date)]['LIKES'] = str(self.likes)
        config['Results_{}'.format(date)]['SKIPS'] = str(self.skips)
        config['Results_{}'.format(date)]['GRABED'] = str(self.grabbed)
        #config['Results_{}'.format(date]['LTD'] = results[4]
        with open('Results.ini', 'a') as configfile:
            config.write(configfile)
        print("Created results file.")
    def sleep(self,_from,_to):
        sleep_time = randint(_from,_to)
        print('sleeping for {} seconds'.format(sleep_time)) 
        time.sleep(sleep_time)
        
        
    def open_instagram(self):
        #open instagram
        print('opening instagram')
        self.driver.get('https://www.instagram.com/')
        
#this function is abit depreciated and profile is better to work with        
##    def login(self,username, password):
##        #get username textbox
##        elem = self.driver.find_element_by_name("username")
##        elem.clear()
##        
##        #send username to textbox
##        elem.send_keys(username)
##
##        #get password textbox
##        elem = self.driver.find_element_by_name("password")
##        elem.clear()
##        
##        #send password to textbox
##        elem.send_keys(password)
##        
##        #delay so login button can appear
##        time.sleep(2)
##        
##        #attempt to login
##        print("attempting login credentials")
##        elem.send_keys(Keys.ENTER)

    def search(self,search_text):
        #find search textbar
       
        elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]')))

        #olf version without wait
        #elem = self.driver.find_element_by_xpath('//input[@placeholder="Search"]')
        elem.clear()
        
        #send search_text to textbox
        elem.send_keys(search_text)
        print('searching for {}'.format(search_text))
        #sleep so drop down has a moment to populate
        time.sleep(2) #NEED THIS
    
        #get first result
        #In dropdown list go DOWN one then press ENTER
        elem.send_keys(Keys.DOWN)
        #time.sleep(1) # do i need this?
        elem.send_keys(Keys.ENTER)
        time.sleep(3) #let things load

    def scroll(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    def _is_used_url(self,url):
        t = (url,) #safer then python string functions according to SquliteDoc
        self.c.execute("SELECT url FROM tblUrlsVisted WHERE url = '{}'".format(url))
        if(self.c.fetchone() is not None):
            return True
        return False

    def get_posts_urls(self,limit):
        print('getting url list..')
        #gets urls listed on page
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        count = 0
        url_list = []
        for elem in elems:
            if(count == limit):
                break
            url = elem.get_attribute("href")
            #grab on post with /p which your user post
            if('.com/p' in url):
                #check if url is already exist in DB
                if(self._is_used_url(url)):
                    self.skips = self.skips + 1
                else:
                    url_list.append(url)
                    print(url)
                    cout = count + 1
        #count add to total grabbed            
        self.grabbed  = self.grabbed + len(url_list)
        return url_list

    def like_posts(self,post_list_urls,limit = 30,sleep_from = 3,sleep_to = 10 ):
        count = 0
        for post in post_list_urls:
            if (count == limit):
                print("like limit reached")
                break
            
            #navigate to url in url list
            self.driver.get(post)
            
            #wait a moment for page to load
            #time.sleep(2)
            
            #get the like icon
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'svg')))
            #old vewrsion without wait
            #elem = self.driver.find_element_by_css_selector('svg')

            sql = ''' INSERT INTO tblUrlsVisted(url) VALUES(?) '''
            
            #check if shows "Like or Unlike" if like exist on page then go and like
            if (elem.get_attribute("aria-label") == "Like"):
                elem.click()
                count = count + 1
                print('{i} liked post {p}'.format(p = post, i = self.likes + 1))         
                self.c.execute(sql,[post])
                self.conn.commit()
                self.ltd = self.ltd + 1     #likes to date
                self.likes= self.likes + 1  #likes this session
            elif(elem.get_attribute("aria-label") == "Unlike"): 
                #we have already liked this in the past sorted added to the DB
                self.c.execute(sql,[post])
                self.conn.commit()
                self.ltd = self.ltd + 1     #likes to date
                self.skips = self.skips + 1
            else:
                print("Something isnt right.. not loaded or not were im supposed to be. Moving on..")
                continue
            #sleep for moment to keep bot human like    
            self.sleep(sleep_from,sleep_to)
        

insta_bot = instagram_automation(GOOGLE_PROFILE_PATH)
insta_bot.open_instagram()
#give browser a few seconds to main page
#time.sleep(6)
for c in CATEGORIES:   
    insta_bot.search(c)
    #give browser a few seconds to load search results
    #scroll down to get more results
    for x in range(0, SCROLL_COUNT):
        insta_bot.scroll()
        time.sleep(1)
    #get all urls_post on page
    urls = insta_bot.get_posts_urls(GRAB_LIMIT)
    insta_bot.like_posts(urls,LIKE_LIMIT_PER_CATGEORY,LIKE_DELAY_RANGE[0],LIKE_DELAY_RANGE[1])
    insta_bot.create_results_file()
print("Ending Driver Like :)")
del insta_bot
