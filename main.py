import os
import time
import warnings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

warnings.filterwarnings("ignore", category=DeprecationWarning)

# JavaScript: HTML5 File drop
# source            : https://gist.github.com/florentbr/0eff8b785e85e93ecc3ce500169bd676
# param1 WebElement : Drop area element
# param2 Double     : Optional - Drop offset x relative to the top/left corner of the drop area. Center if 0.
# param3 Double     : Optional - Drop offset y relative to the top/left corner of the drop area. Center if 0.
# return WebElement : File input
JS_DROP_FILES = "var k=arguments,d=k[0],g=k[1],c=k[2],m=d.ownerDocument||document;for(var e=0;;){var f=d.getBoundingClientRect(),b=f.left+(g||(f.width/2)),a=f.top+(c||(f.height/2)),h=m.elementFromPoint(b,a);if(h&&d.contains(h)){break}if(++e>1){var j=new Error('Element not interactable');j.code=15;throw j}d.scrollIntoView({behavior:'instant',block:'center',inline:'center'})}var l=m.createElement('INPUT');l.setAttribute('type','file');l.setAttribute('multiple','');l.setAttribute('style','position:fixed;z-index:2147483647;left:0;top:0;');l.onchange=function(q){l.parentElement.removeChild(l);q.stopPropagation();var r={constructor:DataTransfer,effectAllowed:'all',dropEffect:'none',types:['Files'],files:l.files,setData:function u(){},getData:function o(){},clearData:function s(){},setDragImage:function i(){}};if(window.DataTransferItemList){r.items=Object.setPrototypeOf(Array.prototype.map.call(l.files,function(x){return{constructor:DataTransferItem,kind:'file',type:x.type,getAsFile:function v(){return x},getAsString:function y(A){var z=new FileReader();z.onload=function(B){A(B.target.result)};z.readAsText(x)},webkitGetAsEntry:function w(){return{constructor:FileSystemFileEntry,name:x.name,fullPath:'/'+x.name,isFile:true,isDirectory:false,file:function z(A){A(x)}}}}}),{constructor:DataTransferItemList,add:function t(){},clear:function p(){},remove:function n(){}})}['dragenter','dragover','drop'].forEach(function(v){var w=m.createEvent('DragEvent');w.initMouseEvent(v,true,true,m.defaultView,0,0,0,b,a,false,false,false,false,0,null);Object.setPrototypeOf(w,null);w.dataTransfer=r;Object.setPrototypeOf(w,DragEvent.prototype);h.dispatchEvent(w)})};m.documentElement.appendChild(l);l.getBoundingClientRect();return l"


# noinspection PyProtectedMember
def drop_files(element, files, offsetX=0, offsetY=0):
    DRIVER = element.parent
    isLocal = not DRIVER._is_remote or '127.0.0.1' in DRIVER.command_executor._url
    paths = []

    # ensure files are present, and upload to the remote server if session is remote
    for file in (files if isinstance(files, list) else [files]):
        if not os.path.isfile(file):
            raise FileNotFoundError(file)
        paths.append(file if isLocal else element._upload(file))

    value = '\n'.join(paths)
    elem_input = DRIVER.execute_script(JS_DROP_FILES, element, offsetX, offsetY)
    elem_input._execute('sendKeysToElement', {'value': [value], 'text': value})


# MAIN PROGRAM #
WebElement.drop_files = drop_files

driver = webdriver.Firefox()

driver.get("https://b.socrative.com/login/teacher/")

WebDriverWait(driver, 1) \
    .until(ec.element_to_be_clickable((By.NAME, 'email'))) \
    .send_keys("EMAIL")

WebDriverWait(driver, 1) \
    .until(ec.element_to_be_clickable((By.NAME, 'password'))) \
    .send_keys("PASSWORD")

# Sign In Pause
input("Please click 'Sign In'... ")

# TODO: Covert to wait until
driver.get("https://b.socrative.com/teacher/#quizzes?v2")
add = driver.find_element(By.XPATH, "//*[text()='Add']")
add.click()

time.sleep(1)

new_quiz = driver.find_element(By.XPATH, "//*[text()='New Quiz']")
new_quiz.click()

time.sleep(1)

mc = driver.find_element(By.XPATH, "//*[text()='MC']")
mc.click()

images_dir = input("Enter images directory: ")
image_prefix = input("Enter image prefix (Ex. '1_9wk A2'): ")
num_questions = int(input("Enter the number of questions: "))
use_e_answer_choice = input("Use (E) answer choice (enter y/n): ")
input("Click enter to start... ")

for quest in range(101, 101 + num_questions):
    print("Question #" + str(quest) + "... ", end='')
    if use_e_answer_choice == 'y':
        e = driver.find_element(By.XPATH, "//*[text()='Add Answer']")
        e.click()

    dropzones = driver.find_elements(By.CLASS_NAME, "image-field__dropzone")

    pic_num = 0
    for zone in dropzones:
        zone.drop_files(images_dir + "\\" + image_prefix + f'{quest:05d}' + str(pic_num) + '.png')
        pic_num += 1

    # mc_num = len(driver.find_elements(By.CLASS_NAME, "quiz-question"))
    multiple_choice = driver.find_element(By.XPATH, "//*[text()='Multiple Choice']")
    while 'text-disable' in multiple_choice.get_attribute('class'):
        time.sleep(0.1)
    multiple_choice.click()

    print('DONE')
    while 'text-disable' in multiple_choice.get_attribute('class'):
        time.sleep(0.1)

print("END OF PROGRAM")
