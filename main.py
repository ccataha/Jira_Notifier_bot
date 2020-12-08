from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time, requests, re


# токен бота в тг
TOKEN = "1309860338:AAFl6kSQxYEAES0kKT8SXiMIOftNczdefmo"


# авторизируемся в жире
def jira_log_in():
    jira_driver = webdriver.Firefox()
    jira_driver.get("https://jira.croc.ru/")
    jira_driver.find_element_by_xpath(
        "/html/body/div/section/div/div/section/div/div[1]/div/a"
    ).click()
    # ввод логина/пароля
    jira_driver.find_element_by_xpath('//*[@id="userNameInput"]').send_keys(
        "dazaytsev@croc.ru"
    )
    jira_driver.find_element_by_xpath('//*[@id="passwordInput"]').send_keys(
        "*"
    )

    jira_driver.find_element_by_xpath('//*[@id="submitButton"]').click()
    jira_driver.implicitly_wait(30)
    jira_driver.find_element_by_xpath('//*[@id="vipSkipBtn"]').click()

    return jira_driver


# получаем последние 5 элементов ленты активности с жиры
def get_activity_board(driver):
    activity_board = []
    wait = WebDriverWait(driver, 55)
    element = wait.until(EC.element_to_be_clickable((By.ID, "gadget-10001")))
    driver.switch_to.frame(element)
    board = driver.find_elements_by_class_name("jira-activity-item")
    for activity_item in board:
        activity_board_item = {}
        tmp = (
            activity_item.text.replace("КомментарийПроголосоватьНаблюдение", "")
            .replace("КомментарийПроголосовать", "")
            .replace("КомментарийНаблюдение", "")
            .replace("Наблюдение", "")
        )
        activity_board_item["time"] = tmp[-16:]
        activity_board_item["text"] = tmp[0:-16]

        activity_board.append(activity_board_item)
    driver.switch_to.default_content()
    return activity_board


def send_to_telegram(array):
    issue_num = ""
    author = ""
    comment = ""
    for elem in array:
        # if elem["text"].find("DCS-") != -1:
        # and elem["text"].find("прокомментировал(а)") != -1
        #        ):
        author = re.search(r"(^\w+\s\w+)|(^\w+@\w+\.\w+)", elem["text"]).group(0)
        # issue_num = re.search(r"DCS-\d+", elem["text"]).group(0)
        comment = elem["text"].split("\n")
        del comment[0]
        comment = "\n".join(comment)
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}"
            + "/sendMessage?chat_id=140302304"
            + "&parse_mode=Markdown"
            + "&text=*Коллеги, у нас коментарий, возможно инцидент!\n"
            + f"*Время:* {elem['time']}\n*Автор:* {author}\n*Комментарий:* {comment}"
        )
    return 1


driver = jira_log_in()
tmp = ""
index = 0
jira_activity_board = get_activity_board(driver)
while True:
    tmp = jira_activity_board[0]
    jira_activity_board = get_activity_board(driver)
    # не отправляем одни и те же комменты по несколько раз
    for i in range(len(jira_activity_board)):
        if jira_activity_board[i] == tmp:
            index = i
            break
    send_to_telegram(jira_activity_board[0:index])
    print(jira_activity_board[0:index])
    time.sleep(40)  # обновление каждые 40 секунд
    driver.refresh()
