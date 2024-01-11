from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time, random, pyautogui as pg
from threading import Thread
from pynput.keyboard import Key, Listener

def thread(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class MonkeyBot:
    # constants
    TIMELIMIT = 6000     # 1 hour timeout
    TIMEINTERVAL = 0.0001  # wait 0.05 between words
    TIMEINT_ERR = 0.00001   # 0.05 +- 0.02
    TYPOS_RATE = 0.005 # 15% percent error
    TIMECONTROL = 30     # Gamemode in monkeytype

    def __init__(self):
        # initalize driver
        self.driver = webdriver.Chrome(options=Options(), service=Service(executable_path='chromedriver.exe'))

    def open_website(self, accept_cookies=False, cookie=''):
        self.driver.get('''https://monkeytype.com/''')
        self.driver.execute_script('alert("Click ~ To Activate The Bot; Hit Enter")')

    @thread
    def enable_fail_safe(self):
        def on_release(key):
            if key == Key.esc:
                self.driver.close()
                return False
        with Listener(on_release=on_release) as listener:
            listener.join()

    def activate_bot(self, human_typing=True, enable_fail_safe=False):
        def find_words():
            temp = self.driver.find_element(by=By.XPATH, value='//*[@id="words"]').text
            print("this is the words :" , temp)
            return temp[temp.find(words[-10:])+10:] if len(words) != 0 else temp

        if enable_fail_safe:
            WebDriverWait(self.driver, self.TIMELIMIT).until_not(EC.alert_is_present())
            self.enable_fail_safe()

        while True:
            WebDriverWait(self.driver, self.TIMELIMIT).until_not(EC.alert_is_present())
            self.driver.execute_script('''
                function keyDownTextField(e) {
                    var keyCode = e.keyCode;
                    console.log(keyCode)
                    if (keyCode == 192) {
                        document.removeEventListener("keydown", keyDownTextField, false);
                        alert("Bot Activated! Hit Enter")
                    }   
                }
                document.addEventListener("keydown", keyDownTextField, false);
            ''')
            WebDriverWait(self.driver, self.TIMELIMIT).until(EC.alert_is_present())
            time.sleep(1.5)

            start, words = time.time(), ''
            if human_typing:
                while time.time() - start < self.TIMECONTROL:
                    words = find_words()
                    self.randomize_typing_speed(words, self.TIMEINTERVAL, self.TIMEINT_ERR, self.TYPOS_RATE)
            else:
                while time.time() - start < self.TIMECONTROL:
                    words = find_words()
                    for i in words.split('\n'):
                        pg.write(i + " ")
            self.driver.execute_script('alert("Bot Finished Typing. Click ~ To Reactivate")')

    def randomize_typing_speed(self, words, intervals, error_rate, typos_rate):
        def add_noise():
            if random.random() > 0.5:
                return intervals+(random.random() * error_rate)
            else:
                return intervals-(random.random() * error_rate)

        def add_errors():
            error_words = ['during','point','place','from','problem','which','world','begin','face','go']
            if random.random() > (1 - typos_rate):
                random_word = random.choice(error_words)
                pg.write(random_word, interval=add_noise())
                pg.press('backspace', presses=len(random_word), interval=add_noise())

        for i in words.split('\n'):
            add_errors()
            pg.write(i + " ", interval=add_noise())


if __name__ == '__main__':
    bot = MonkeyBot()
    bot.open_website(accept_cookies=True, cookie='//*[@id="cookiePopup"]/div[2]/div[2]/button[1]')
    bot.activate_bot(human_typing=True, enable_fail_safe=True)