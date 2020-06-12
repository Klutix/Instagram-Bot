from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sqlite3
#from CONFIG import * #user configuration file***
import configparser #using this for results.. may switch config to this

import datetime
import os       #used for working path
import time     #used for sleep
import sys      #used for command line arg

class instagram_automation:
    def __init__(self): #path is hardcoded for windows
        #first set up config
        self.set_config()
        #Chrome Driver Setup---------------------------------------------
        #options create options to handle profiles and or headless
        self._chrome_options = Options()
        
        #chrome driver hardcoded to current path
        self.chromedriver = "chromedriver.exe"
        
        #set the environment
        os.environ["webdriver.chrome.driver"] = self.chromedriver

        #make headless #might be flagging server.. need to test this
        #self._chrome_options.add_argument('--remote-debugging-port=9222')
        #self._chrome_options.add_argument("--headless")        #self._chrome_options.add_argument("--disable-gpu") # needed for headless
        #self._chrome_options.add_argument("window-size=1200x600");
        #self._chrome_options.add_argument("--disable-extensions")
    
        #add the profile to options
        self._chrome_options.add_argument('--profile-directory=Default')
        self._chrome_options.add_argument("user-data-dir={path}".format(path = self.GOOGLE_PROFILE_PATH))
        
        #create the bot driver
        try:
            self.driver = webdriver.Chrome(self.chromedriver, options = self._chrome_options)
        except:
            print("An error occured in attempt to use the WebDriver.")
            print("Make sure NO OTHER CHROME INSTANCES ARE RUNNNING before using the bot..")
            print("or TRY making sure you have the correct chromedriver.exe in the program folder.")
            input("Exiting Program.. Press Enter to Exit..")
            exit()
        try:
            self.conn = sqlite3.connect('db_instagram_data.db')
            self.c = self.conn.cursor()
        except sqlite3.Error:
            print ("Error open db.\n")
            print("Exiting Program")
            input("Press Enter to Exit Program...")
            exit()
            
        try:
            #set up two tables Questions and jobs applied to
            self.c.execute('''CREATE TABLE tblUrlsVisted 
             (url text)''')
            print("Created tblUrlsVisted Table")

            # Save (commit) the changes
            self.conn.commit()
            print("Tables Created")
        except:
            print("Tables Already Exist")

        #ok setup the results varaiables
        self.likes = 0
        self.skips = 0
        self.grabbed = 0
        self.lph = 0
        self.ltd = 0
            
    def __del__(self):
        self.driver.close()

        
    def set_config(self):
        #create configuration file if not exist
        if not os.path.exists('config.ini'):
            print("Creating config file: Results.ini")
            date = datetime.datetime.now()
            config = configparser.ConfigParser()
            config['CONFIG'] = {}
            config['CONFIG']['GOOGLE_PROFILE_PATH'] = "C:\\Users\\YOUR_USER_NAME\\AppData\\Local\\Google\\Chrome\\User Data" 
            config['CONFIG']['LIKE_LIMIT_PER_CATGEORY'] = '5'
            config['CONFIG']['GRAB_LIMIT'] = '300'
            config['CONFIG']['LIKE_DELAY_RANGE'] = '15 60'
            config['CONFIG']['SCROLL_COUNT'] = '5'
            config['CONFIG']['CATEGORIES'] = "#Fractals #FractalArt #prettyArt"
            with open('CONFIG.ini', 'w') as configfile:
                config.write(configfile)
            print("Created CONFIG.ini")
            print("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program")
            input("Press Enter to continue...")
            exit()

        #pull from the config file
        config = configparser.ConfigParser()
        config.read('CONFIG.ini')
        
        self.GOOGLE_PROFILE_PATH     = config['CONFIG']['GOOGLE_PROFILE_PATH']
        self.LIKE_LIMIT_PER_CATGEORY = int(config['CONFIG']['LIKE_LIMIT_PER_CATGEORY'])
        self.GRAB_LIMIT              = int(config['CONFIG']['GRAB_LIMIT'])
        self.LIKE_DELAY_RANGE        = list(map(int,config['CONFIG']['LIKE_DELAY_RANGE'].split()))
        self.SCROLL_COUNT            = int(config['CONFIG']['SCROLL_COUNT'])
        self.CATEGORIES              = config['CONFIG']['CATEGORIES'].split()

        #make sure user has been set correctly
        if('YOUR_USER_NAME' in self.GOOGLE_PROFILE_PATH):
             print("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program")
             print("Exiting Program")
             input("Press Enter to Exit Program...")
             exit()

    def create_results_file(self):
        print("Creating results file: Results.txt")
        date = datetime.datetime.now()
        config = configparser.ConfigParser()
        config['Results_{}'.format(date)] = {}
        config['Results_{}'.format(date)]['LIKES'] = str(self.likes)
        config['Results_{}'.format(date)]['SKIPS'] = str(self.skips)
        config['Results_{}'.format(date)]['GRABED'] = str(self.grabbed)

        with open('Results.txt', 'a') as configfile:
            config.write(configfile)
        print("Created results file.")
        
    def sleep(self,_from,_to):
        sleep_time = randint(_from,_to)
        print('sleeping for {} seconds'.format(sleep_time)) 
        time.sleep(sleep_time)
                
    def open_instagram(self):
        print('opening instagram')
        self.driver.get('https://www.instagram.com/')

    def search(self,search_text):
        #find search textbar
        try:
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]')))
        except NoSuchElementException:
            print("Web page either failed to load correctly or You not have Instgagram Credentials saved to your Chrome profile")
            print("--Make sure you have set <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini.")
            print("Exiting Program")
            input("Press Enter to Exit Program...")
            exit()
        
        #send search_text to textbox
        elem.send_keys(search_text)
        print('searching for {}'.format(search_text))
        #sleep so drop down has a moment to populate
        time.sleep(2) #DO NOT DELETE
    
        #get first result
        #In dropdown list go DOWN one then press ENTER
        elem.send_keys(Keys.DOWN)
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
            #grab on post with /p which means its a user post
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
            
            #get the like icon
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'svg')))

            sql = ''' INSERT INTO tblUrlsVisted(url) VALUES(?) '''
            
            #check if shows "Like or Unlike" if like exist on page then go and like
            if (elem.get_attribute("aria-label") == "Like"):
                elem.click()
                count = count + 1
                print('{i} liked post {p}'.format(p = post, i = self.likes + 1))         
                self.c.execute(sql,[post])
                self.conn.commit()
                self.ltd = self.ltd + 1     #likes to date
                self.likes = self.likes + 1  #likes this session
            elif(elem.get_attribute("aria-label") == "Unlike"): 
                #we have already liked this in the past sorted added to the DB
                self.c.execute(sql,[post])
                self.conn.commit()
                self.ltd = self.ltd + 1     #likes to date
                self.skips = self.skips + 1
                print('Skipping {}'.format(post))
            else:
                print("Something isnt right.. not loaded or not were im supposed to be. Moving on..")
                continue
            #sleep for moment to keep bot human like    
            self.sleep(sleep_from,sleep_to)

    def run(self):
        self.open_instagram()
        for c in self.CATEGORIES:   
            self.search(c)
            #scroll down to get more results
            for x in range(0, self.SCROLL_COUNT):
                self.scroll()
                time.sleep(1)
            #get all urls_post on page
            urls = self.get_posts_urls(self.GRAB_LIMIT)
            self.like_posts(urls,self.LIKE_LIMIT_PER_CATGEORY,self.LIKE_DELAY_RANGE[0],self.LIKE_DELAY_RANGE[1])
            self.create_results_file()
        print("Finished Running")

insta_bot = instagram_automation()
insta_bot.run()
del insta_bot

