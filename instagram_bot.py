from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sqlite3
import threading

import configparser 

import datetime
import os       #used for working path
import time     #used for sleep
import sys      #used for command line arg

class instagram_automation:
    def __init__(self): #path is hardcoded for windows
        #first set up config
        self.create_example_ini()
        self.set_config_from_ini()
        #Chrome Driver Setup---------------------------------------------
        #options create options to handle profiles and or headless
        self._chrome_options = Options()
        
        #chrome driver hardcoded to current path
        self.chromedriver = "chromedriver.exe"
        
        #set the environment
        os.environ["webdriver.chrome.driver"] = self.chromedriver
    
        #add the profile to options
        self._chrome_options.add_argument('--profile-directory=Default')
        self._chrome_options.add_argument("user-data-dir={path}".format(path = self._GOOGLE_PROFILE_PATH))
        
        #create the bot driver
        try:
            self.driver = webdriver.Chrome(self.chromedriver, options = self._chrome_options)
        except:
            print("An error occured in attempt to use the WebDriver.")
            print("--Make sure you have set <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini.")
            print("--Make sure NO OTHER CHROME INSTANCES ARE RUNNNING before using the bot..")
            print("or TRY making sure you have the correct chromedriver.exe in the program folder.")
            input("Exiting Program.. Press Enter to Exit..")
            exit()

        #ok setup the results varaiables
        self._likes = 0
        self._skips = 0

        self._enabled = True
        self._paused = False

        self._state = "OFF"
        
   
        
    #config getters and setters ------------
    def get_GOOGLE_PROFILE_PATH():
        return _GOOGLE_PROFILE_PATH
    def set_GOOGLE_PROFILE_PATH(GOOGLE_PROFILE_PATH):
        _GOOGLE_PROFILE_PATH = GOOGLE_PROFILE_PATH
    def get_LIKE_LIMIT_PER_CATGEORY():
        return _LIKE_LIMIT_PER_CATGEORY
    def set_LIKE_LIMIT_PER_CATGEORY(LIKE_LIMIT_PER_CATGEORY):
        _LIKE_LIMIT_PER_CATGEORY
    def get_LIKE_DELAY_RANGE():
        return _LIKE_DELAY_RANGE
    def set_LIKE_DELAY_RANGE(LIKE_DELAY_RANGE):
        _LIKE_DELAY_RANGE = LIKE_DELAY_RANGE
    def get_CATEGORIES():
        return _CATEGORIES
    def set_CATEGORIES(CATEGORIES):
        _CATEGORIES = CATEGORIES

    def get_state(self):
        return (self._state)

    #results getter
    def get_results_list():
        return [self._likes,self._skips,self._grabbed]


    #creates a template CONFIG.ini | user then tailors it to their needs
    def create_example_ini(self):
         if not os.path.exists('config.ini'):
            print("Creating config file: Results.ini")
            date = datetime.datetime.now()
            config = configparser.ConfigParser()
            config['CONFIG'] = {}
            config['CONFIG']['GOOGLE_PROFILE_PATH'] = "C:\\Users\\YOUR_USER_NAME\\AppData\\Local\\Google\\Chrome\\User Data" 
            config['CONFIG']['LIKE_LIMIT_PER_CATGEORY'] = '5'
            config['CONFIG']['LIKE_DELAY_RANGE'] = '15 60'
            config['CONFIG']['SCROLL_COUNT'] = '5'
            config['CONFIG']['CATEGORIES'] = "#Fractals #FractalArt #prettyArt"
            with open('CONFIG.ini', 'w') as configfile:
                config.write(configfile)
            print("Created CONFIG.ini")
            print("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program")
            input("Press Enter to continue...")
            exit()

    #reads CONFIG.ini and sets proper values
    def set_config_from_ini(self):
        if os.path.exists('config.ini'):  
            #create configuration file if not exist
            #pull from the config file
            config = configparser.ConfigParser()
            config.read('CONFIG.ini')
            
            self._GOOGLE_PROFILE_PATH     = config['CONFIG']['GOOGLE_PROFILE_PATH']
            self._LIKE_LIMIT_PER_CATGEORY = int(config['CONFIG']['LIKE_LIMIT_PER_CATGEORY'])
            self._LIKE_DELAY_RANGE        = list(map(int,config['CONFIG']['LIKE_DELAY_RANGE'].split()))
            self._SCROLL_COUNT            = int(config['CONFIG']['SCROLL_COUNT'])
            self._CATEGORIES              = config['CONFIG']['CATEGORIES'].split()

            #make sure user has been set correctly
            if('YOUR_USER_NAME' in self._GOOGLE_PROFILE_PATH):
                 print("!! -- Replace <YOUR_USER_NAME> in GOOGLE_PROFILE_PATH in CONFIG.ini then rerun program")
                 print("Exiting Program")
                 input("Press Enter to Exit Program...")
                 exit()
        else:
            print("error.. missing CONFIG.ini")

    #creates Results.txt with results of run <<----this needs to be adjusted for every run in case of error
    def create_results_file(self):
        print("Creating results file: Results.txt")
        date = datetime.datetime.now()
        config = configparser.ConfigParser()
        config['Results_{}'.format(date)] = {}
        config['Results_{}'.format(date)]['LIKES'] = str(self._likes)
        config['Results_{}'.format(date)]['SKIPS'] = str(self._skips)

        with open('Results.txt', 'a') as configfile:
            config.write(configfile)
        print("Created results file.")

    #custom sleep function to handle in possible range
    def sleep(self,_from,_to):
        sleep_time = randint(_from,_to)
        print('sleeping for {} seconds'.format(sleep_time)) 
        time.sleep(sleep_time)

    #opens to instagram.com 
    def open_instagram(self):
        print('opening instagram')
        self.driver.get('https://www.instagram.com/')

    #clicks on search, enters search value, then 
    #presses down to select first from drop down then hits enter for search
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

    #scroll down to botton of document body
    def scroll(self):
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    #querys database to see if url exist or not
    def _is_used_url(self,url):
        t = (url,) #safer then python string functions according to SquliteDoc
        self.c.execute("SELECT url FROM tblUrlsVisted WHERE url = '{}'".format(url))
        if(self.c.fetchone() is not None):
            return True
        return False

    #gets a list of urls from search results page
    def get_posts_urls(self):
        print('getting url list..')
        #gets urls listed on page
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        count = 0
        url_list = []
        for elem in elems:
            state = self._manage_state()
            if(state == "OFF"):
                break
            url = elem.get_attribute("href")
            #grab on post with /p which means its a user post
            if('.com/p' in url):
                #check if url is already exist in DB
                if(self._is_used_url(url)):
                    self._skips = self._skips + 1
                else:
                    url_list.append(url)
                    print(url)
        #count add to total grabbed            
        return url_list

    #likes all post urls in a url list and uses range of manage like speed
    def like_posts(self,post_list_urls):
        count = 0
        for post in post_list_urls:
            state = self._manage_state()
            if(state == "OFF"):
                break
            if (count == self._LIKE_LIMIT_PER_CATGEORY):
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
                print('{i} liked post {p}'.format(p = post, i = self._likes + 1))         
                self.c.execute(sql,[post])
                self.conn.commit()
                #self.ltd = self.ltd + 1      #likes to date
                self._likes = self._likes + 1  #likes this session
            elif(elem.get_attribute("aria-label") == "Unlike"): 
                #we have already liked this in the past sorted added to the DB
                self.c.execute(sql,[post])
                self.conn.commit()
                #self.ltd = self.ltd + 1     #likes to date
                self._skips = self._skips + 1
                print('Skipping {}'.format(post))
            else:
                print("Something isnt right.. not loaded or not were im supposed to be. Moving on..")
                continue
            #sleep for moment to keep bot human like    
            self.sleep(self._LIKE_DELAY_RANGE[0],self._LIKE_DELAY_RANGE[1])

    #main bot driver
    def run(self):
        self._state = "ON"
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


        
        self.open_instagram()
        for c in self._CATEGORIES:
            state = self._manage_state()
            if(state == "OFF"):
                break
            print("Searching..")
            self.search(c)
            #scroll down to get more results
            for x in range(0, self._SCROLL_COUNT):
                self.scroll()
                time.sleep(1)
            #get all urls_post on page
            urls = self.get_posts_urls()
            self.like_posts(urls)
            self.create_results_file()
        print("Finished Running")

    def _manage_state(self):
        if(not self._enabled):
            print("break")
            self._state == "OFF"
            return self._state
        if(self._paused):
                print("PAUSED")
        while(self._paused):
            self._state ="PAUSED"
            time.sleep(1)
            self._state = "ON"
        return self._state
        
    def pause(self, v):
        self._paused = v

    def enabled(self,v):
        self._enabled = v


        
#int main---------------------------------------------still testing class above
        #with threading functionality
i = instagram_automation()
t = threading.Thread(target=i.run)
t.start()

def cmd_in():
    while(True):
        state = i.get_state()
        print("Enter Commands at any time\n")
        r = input("!!-----------COMMANDS-------------\n\n-----PAUSE\n-----RESUME\n-----STOP\n-----EXIT\n\n")
        r = r.lower()
        if(r == "stop"):
            i.enabled(False)
            if(i.get_state() == "OFF"):
                return
        elif(r == "pause"):
            i.pause(True)
            if(i.get_state() == "PAUSED"):
                continue
        elif(r == "resume"):
            i.pause(False)
            if(i.get_state() == "ON"):
                continue
        else:
            continue
        while(i.get_state() == state):
            time.sleep(1)

if __name__ == "__main__":    
    cmd_in()
    del i
    input("Program finished press enter to exit...")
    exit()
        







    





