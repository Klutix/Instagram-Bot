from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import threading
import configparser 
import datetime
import timeit
import os       #used for working path
import time     #used for sleep
import sys      #used for command line arg

class instagram_automation:
    
    def __init__(self): #path is hardcoded for windows
        #first set up config
        #create example config if none exist
        self.create_example_ini()
        
        #read config
        self.set_config_from_ini()
        
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
        #self._chrome_options.add_argument("--enable-extensions")
    
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

            print("Tables Already Exist")

        #ok setup the results varaiables
        
        self._likes = 0
        self._skips = 0
        self._skips_list = []

        self._enabled = True
        self._paused = False

        self._state = "OFF"

        #more out variables
        self._urls_remaining_count = 0
        self._urls_in_queue = 0
        self._time_remaining = 0
        self._last_url = ''
        self._category_current = ''
        self._date = datetime.date.today()
        self._likes_today = 0
        
        self.cmd_in()
        
          
    #config getters and setters ------------
    def get_GOOGLE_PROFILE_PATH():
        return _GOOGLE_PROFILE_PATH
    def set_GOOGLE_PROFILE_PATH(GOOGLE_PROFILE_PATH):
        self._GOOGLE_PROFILE_PATH = GOOGLE_PROFILE_PATH
    def get_LIKE_LIMIT_PER_CATGEORY():
        return self._LIKE_LIMIT_PER_CATGEORY
    def set_LIKE_LIMIT_PER_CATGEORY(LIKE_LIMIT_PER_CATGEORY):
        self._LIKE_LIMIT_PER_CATGEORY = LIKE_LIMIT_PER_CATGEORY
    def get_LIKE_DELAY_RANGE():
        return self._LIKE_DELAY_RANGE
    def set_LIKE_DELAY_RANGE(LIKE_DELAY_RANGE):
        self._LIKE_DELAY_RANGE = LIKE_DELAY_RANGE
    def get_CATEGORIES():
        return self._CATEGORIES
    def set_CATEGORIES(CATEGORIES):
        self._CATEGORIES = CATEGORIES

    def get_state(self):
        return (self._state)

    #results getter
    def get_results_list():
        return [self._likes,self._skips,self._grabbed]


    #creates a template CONFIG.ini | user then tailors it to their needs
    def create_example_ini(self):
         if not os.path.exists('config.ini'):
            print("Creating config file: Results.ini")
            #config = configparser.ConfigParser()
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
        config['Results_{}'.format(date)]['SKIPS'] = str(self._skips_list)
        config['Results_{}'.format(date)]['CATEGORIES'] = str(self._CATEGORIES)
        config['Results_{}'.format(date)]['LIKES_TODAY'] = str(self._likes_today)

        with open('Results.txt', 'a') as configfile:
            config.write(configfile)

        print("Created results file.")

    def update_likes_today():
        pass

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
            state = self._manage_pause()
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
        self._skips_list.append(self._skips)
        #count add to total grabbed
        self._urls_remaining_count = len(url_list)
        a = self._LIKE_LIMIT_PER_CATGEORY
        if(self._LIKE_LIMIT_PER_CATGEORY <= self._urls_remaining_count):
            self._urls_in_queue = self._LIKE_LIMIT_PER_CATGEORY
        else:
            self._urls_in_queue = a
        return url_list

    #likes all post urls in a url list and uses range of manage like speed
    def like_posts(self,post_list_urls):
        count = 0
        for post in post_list_urls:
            self._last_url = post
            state = self._manage_pause()
            self._print_feedback()
            if(state == "OFF"):
                break
            if (count == self._LIKE_LIMIT_PER_CATGEORY):
                print("like limit reached")
                break
            
            #navigate to url in url list
            self.driver.get(post)
            
            #get the like icon
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR , 'svg')))

            sql = ''' INSERT INTO tblUrlsVisted(url,date) VALUES(?,?) '''
            
            #check if shows "Like or Unlike" if like exist on page then go and like
            if (elem.get_attribute("aria-label") == "Like"):
                elem.click()
                count = count + 1
                print('{i} liked post {p}'.format(p = post, i = self._likes + 1))         
                self.c.execute(sql,[post,self._date])
                self.conn.commit()
                #self.ltd = self.ltd + 1      #likes to date
                self._likes = self._likes + 1  #likes this session
            elif(elem.get_attribute("aria-label") == "Unlike"): 
                #we have already liked this in the past sorted added to the DB
                self.c.execute(sql,[post,self._date])
                self.conn.commit()
                #self.ltd = self.ltd + 1     #likes to date
                self._skips = self._skips + 1
                print('Skipping {}'.format(post))
            else:
                print("Something isnt right.. not loaded or not were im supposed to be. Moving on..")
                continue

            self._urls_remaining_count = self._urls_remaining_count - 1
            self._urls_in_queue = self._urls_in_queue - 1
            #sleep for moment to keep bot human like    
            self._sleep_with_iterupt(self._LIKE_DELAY_RANGE[0],self._LIKE_DELAY_RANGE[1])
            if(not self._enabled):
                return
    #main bot driver
    def run(self):     
        while(True):
            if(self._state == "ON"):
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

                self.set_config_from_ini()
                self._start = timeit.default_timer()
                self._skips = 0
                self.enabled(True)
                self.pause(False)
                self.open_instagram()
                for c in self._CATEGORIES:
                    self._category_current = c
                    state = self._manage_pause()
                    self._print_feedback()
                    if(state == "OFF"):
                        break
                    print("Searching..")
                    self.search(c)
                    #scroll down to get more results
                    for x in range(0, self._SCROLL_COUNT):
                        self._manage_pause()
                        if(not self._enabled):
                            return
                        self.scroll()
                        time.sleep(1)
                    #get all urls_post on page
                    urls = self.get_posts_urls()
                    self.like_posts(urls)
                    
                    if(not self._enabled):
                        break
                self.create_results_file()
                self._state = "DONE"
                self._print_feedback()
                print("Finished Running")
            else:
                time.sleep(1)
                
    #this PAUSED and OFF when set
    def _manage_pause(self):
        if(not self._enabled):
            self._print_feedback()

        while(self._paused):
            self._print_feedback()
            time.sleep(1)
            if(not self._enabled):
                return self._state
        if(self._state != "OFF"):
            self._state = "ON"
        self._paused = False
        
        return self._state
    
    #this counts all likes in the DB the current day
    def count_todays_likes(self):
        sql = "SELECT COUNT(url) from tblUrlsVisted WHERE date = '{}'".format(self._date)
        self.c.execute(sql)
        self._likes_today = self.c.fetchone()[0]
        
    #sets pause flag   
    def pause(self, v):
        self._paused = v
        if(self._paused): 
            self._state = "PAUSED"
        else:
            self._state = "ON"
    #sets enabled flag
    def enabled(self,v):
        self._enabled = v
        if(not self._enabled):            
            self._state = "OFF"
        else:
            self._state = "ON"

    # define our clear function 
    def _clear(self): 
        # for windows 
        if os.name == 'nt': 
            _ = os.system('cls')   
        # for mac and linux(here, os.name is 'posix') 
        else: 
            _ = os.system('clear')
            
    #this is sleep function state inbetween sleep intervals
    def _sleep_with_iterupt(self,_from,_to):
        sleep_time = randint(_from,_to)
        self._time_remaining = sleep_time
        for t in range(0, sleep_time):
            if(not self._enabled):
                return
            time.sleep(1)
            self._time_remaining =  self._time_remaining - 1
            state = self._manage_pause()
            self._print_feedback()

    #this handles the input to the bot when running assigned to thread in run
    def cmd_in(self):       
        t = threading.Thread(target=self.run)
        started = False
        self._print_feedback(False)
        while(True):
            state = self._state         
            r = input()
            r = r.lower()
            if(r == "stop" or r == "4"):
                self.enabled(False)     
                if(self._state == "DONE"): #hmm quarky..maybe bad
                    self._print_feedback(False)
                    t.join()
                    #return
                #return
            elif(r == "pause" or r == "2"):
                if(self._state == "ON"):
                    self.pause(True)
                else:
                    continue
            elif(r == "resume" or r == "3"):
                if(self._state == "PAUSED"):
                    self.pause(False)
                else:
                    continue
            elif(r == "start"or r == "1"):
                if(self._state == "OFF" or self._state == "DONE" ):
                    self.enabled(True)
                    if(not started):
                        t.start()
                        started = True 
                else:
                    continue
            else:
                continue
            while(self._state == state):
                time.sleep(1)
                
    #this prints feedback for bot
    def _print_feedback(self, is_running = True):
        datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
        stop = 0
        if(is_running):
            self.count_todays_likes()
            stop = int(-1*(self._start - timeit.default_timer()))

        out_layout = str("\033[1;33;40m-----------------------Instagram Automation Tool------------------------\n"
            " \033[0;33;40m@ \033[1;35;40mUrls Available:\033[0;33;40m{urls_remaining_count}            \033[94m Runtime:\033[1;37;40m{rn}  \033[92m STATUS:{state}\n" 
            " \033[0;33;40m@ \033[1;35;40mUrls In Queue:\033[0;33;40m{queue}             \033[94m Sleep-Time Remaining:\033[1;37;40m{tm}\n" 
            " \033[0;33;40m@ \033[1;35;40mUrls Skips:\033[0;33;40m{skips}\n"
            " \033[0;33;40m@ \033[1;35;40mUrl Limit:\033[0;33;40m{limit}\n"
            "\n\033[0;33;40m"
            " * \033[1;36;40mLast Url:\033[0;33;40m{last_url}\n"
            " * \033[1;36;40mCatgeorgies:\033[0;33;40m{catgories_list}\n"                       
            " * \033[1;36;40mCurent Category: \033[1;34;40m{current_category}\n"
            "\n"                                                                                            
            " \033[0;33;40m-\033[1;37;40m Likes:\033[1;34;40m{likes}\n"
            " \033[0;33;40m#\033[1;37;40m Total Likes Today :\033[1;34;40m{today_likes}\n"
            "\033[1;33;40m************************************************************************\n"
            "------------------------------------------------------------------------\n"
            " \033[1;34;40mCOMMANDS LIST:\n"                               
            "   \033[1;33;40m1)START\n"
            "   2)PAUSE\n"             
            "   3)RESUME\n"
            "   4)STOP\n\n"            
            "\n"             
            "\033[1;37;40mEnter Command or # at anytime...\n")
        self._clear()
        print(out_layout.format(urls_remaining_count = self._urls_remaining_count,
                                state = self._state,
                                tm = self._time_remaining,
                                last_url = self._last_url,
                                queue = self._urls_in_queue,
                                catgories_list = self._CATEGORIES,
                                current_category = self._category_current,
                                likes = self._likes,
                                skips = self._skips,
                                today_likes = self._likes_today,
                                limit = self._LIKE_LIMIT_PER_CATGEORY,
                                rn = stop))

    

#this is main..duh
if __name__ == "__main__":    
    i = instagram_automation()
    i.cmd_in()
    del i
    exit()
        







    





