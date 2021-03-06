import requests
from selenium.webdriver import Chrome, Firefox
import prettytable
import time
import sys


class Action:
    def __init__(self):
        self.cmoney_url = "https://www.cmoney.tw/member/login/?url=https%3a%2f%2fwww.cmoney.tw%2fvt%2faccount-manage.aspx"
        self.driver = None
        self.account_boxes = {}

    def start_browser(self, user_id, user_pw):
        # 輸入帳密
        self.driver = Chrome("./chromedriver.exe")
        # self.driver = Firefox(executable_path="./geckodriver")
        self.driver.get(self.cmoney_url)
        self.login(id_, pw_)

    def login(self, user_id, user_pw):
        self.driver.find_element_by_id("account").clear()
        self.driver.find_element_by_id("account").send_keys(user_id)
        self.driver.find_element_by_id("pw").send_keys(user_pw)
        self.driver.find_element_by_id("ContentPlaceHolder1_loginBtn").click()
        time.sleep(0.2)
        if self.driver.current_url == self.cmoney_url:
            return False
        return True


    def login_ok(self):
        account_boxes = self.driver.find_elements_by_css_selector(".mabox")
        try:
            for account_title in account_boxes:
                account_title.find_element_by_css_selector("a").get_attribute("title")

        except:
            add_account = str.lower(input("是否創建帳號?\n如果是請按y\n否請按n:"))
            try:
                if add_account == "y":
                    self.create_account()
                elif add_account == "n":
                    self.select_account()
            except:
                print("請輸入指示之文字")

        self.select_account()

    def create_account(self):
        # 新增帳號半成品

        # 第一次登入
        try:
            self.driver.find_element_by_name("ctl00$ContentPlaceHolder1$ctl01").click()
            self.driver.find_element_by_id("bindFacebook").click()
            self.driver.find_element_by_class_name("current-role").click()
            self.driver.find_element_by_id("submitBtn").click()
        except:
            pass

        try:
            try:
                self.driver.find_element_by_id("addAccountLeftMenu").click()
                self.select_account()
            except:
                pass

        except:

            print("fuck")

            self.create_account()

    def select_account(self):
        self.driver.find_element_by_css_selector("a[class='v2']").click()
        account_boxes = self.driver.find_elements_by_css_selector(".mabox")
        # print(account_boxes)
        for i, m in enumerate(account_boxes):
            self.account_boxes[str(i)] = account_boxes[i].find_element_by_css_selector("a").get_attribute("title")

        while True:
            for i, m in enumerate(self.account_boxes):
                print('您的帳戶:', i, self.account_boxes[m])
            try:
                account_number = int(input("選擇以上帳戶:"))
                break
            except:
                print("請輸入數字:")
        try:
            path = "//*[text()[normalize-space(.) = '{}']]"
            self.driver.find_element_by_xpath(
                path.format(
                    account_boxes[account_number].find_element_by_css_selector("a").get_attribute("title"))).click()

            # 幹掉彈跳視窗
            self.close_pop_up_window()
        except:
            if account_number > len(account_boxes):
                print("沒那麼多帳號")
            else:
                print("帳戶有誤")
            self.select_account()

    def close_pop_up_window(self):
        # 關掉他媽的彈跳視窗
        print("處理中請稍後.....")
        time.sleep(4)
        try:
            # driver.find_element_by_css_selector("a.fancybox-item.fancybox-close").click()
            self.driver.refresh()
        except:
            pass
        self.trade_stock_system()

    def trade_stock_system(self):
        time.sleep(2.5)
        account_table = self.driver.find_element_by_id("AccountTabs")

        # 帳戶概覽
        def view_account():

            account_table.find_element_by_css_selector("a[title='帳戶概覽']").click()

            # account_table.find_element_by_css_selector("a[href='#AI']").click()
            time.sleep(0.5)
            # 顯示帳戶股票配置

            big_table = self.driver.find_element_by_css_selector(".tabCon1")
            small_table = big_table.find_element_by_css_selector(".chart")
            stock_data = small_table.get_attribute("chartdata")
            clean_stock_data = stock_data. \
                replace('{"data":[', ''). \
                replace('"', ''). \
                replace(']}', ''). \
                replace('[', ''). \
                replace(']', ''). \
                split(',')
            pre_table = ["股票名稱or現金資產", '市值', '報酬率/%', '名稱']
            pre = prettytable.PrettyTable(pre_table, encoding='utf-8')

            for n in range(0, len(clean_stock_data), 4):
                pre.add_row(clean_stock_data[n:n + 4])
            print(pre)

            # 顯示帳戶資產配置
            asset_deploy_table = self.driver.find_element_by_css_selector(".tabCon1.alldata")
            asset_deploy_tr = asset_deploy_table.find_elements_by_tag_name('tr')

            pre = prettytable.PrettyTable()
            asset_deploy = []
            price = []

            for row in asset_deploy_tr:

                asset_deploy_th = row.find_elements_by_tag_name('th')
                asset_deploy_td = row.find_elements_by_tag_name('td')

                for col1 in asset_deploy_th:
                    asset_deploy += col1.text.split('ú')

                for col2 in asset_deploy_td:
                    price += col2.text.split('ú')

            pre.add_column("資產配置", asset_deploy)
            pre.add_column("價格", price)
            print(pre)

        # 委託查詢
        def order_search():
            account_table.find_element_by_css_selector("a[title='委託查詢']").click()
            time.sleep(0.5)
            order_grid_title = []
            order_grid = []
            order_grid2 = []
            small_table = self.driver.find_element_by_css_selector(".detailframe.recTb1Div")

            small_table_tr = small_table.find_elements_by_tag_name("tr")
            for row1 in small_table_tr:
                small_table_th = row1.find_elements_by_tag_name("th")
                for col1 in small_table_th:
                    c1 = col1.text.replace('\n(名稱)', '(名稱)').replace('交易\n類別', '交易&類別').split(" ")
                    order_grid_title += c1

                break

            small_table2 = self.driver.find_elements_by_id('EntrustQueryListInfo')
            for row2 in small_table2:
                small_table2 = row2.find_elements_by_tag_name("td")
                for col2 in small_table2:
                    c2 = col2.text.replace('\n', ' ').split('ú')
                    order_grid += c2

                break

            big_table = self.driver.find_element_by_css_selector(".detailframe.recTb2Div")
            big_table_tr = big_table.find_elements_by_tag_name("tr")

            for row3 in big_table_tr:
                big_table_th = row3.find_elements_by_tag_name("th")
                for col3 in big_table_th:
                    c3 = col3.text. \
                        replace(' / ', '/'). \
                        replace('買入成本\n預估賣出收入', '買入成本&預估賣出收入') \
                        .split(' ')
                    order_grid_title += c3

                break

            big_table2 = self.driver.find_elements_by_id('EntrustQueryListData')
            for row4 in big_table2:
                big_table2_td = row4.find_elements_by_tag_name("td")
                for col4 in big_table2_td:
                    c4 = col4.text. \
                        replace('/ ', '/').replace('\n', ' ').split('ú')

                    order_grid2 += c4

                break

            # print(order_grid_title)
            # print(order_grid)
            new_order_grid = []
            new_order_grid2 = []
            order_table = []

            for order_grid_len in range(0, len(order_grid), 2):
                new_order_grid.append(order_grid[order_grid_len:order_grid_len + 2])

            for order_grid2_len in range(0, len(order_grid2), 6):
                new_order_grid2.append(order_grid2[order_grid2_len:order_grid2_len + 6])

            for i in range(len(new_order_grid)):
                order_table.append(new_order_grid[i] + new_order_grid2[i])

            pre = prettytable.PrettyTable(order_grid_title, encoding='utf-8')

            for i in range(len(order_table)):
                pre.add_row(order_table[i])
            print(pre)

        # 交易紀錄
        def trade_record():
            account_table.find_element_by_css_selector("a[title='交易紀錄']").click()
            # 下拉選單
            self.driver.find_element_by_css_selector("i[class='fa fa-chevron-down']").click()
            self.driver.find_element_by_css_selector("a[filtervalue='Season']").click()
            self.driver.find_element_by_id("submitfilter").click()
            record_grid_title = []
            record_grid = []
            record_grid2 = []

            small_table = self.driver.find_element_by_css_selector(".detailframe.recTb1Div")

            small_table_tr = small_table.find_elements_by_tag_name("tr")

            for row1 in small_table_tr:
                small_table_th = row1.find_elements_by_tag_name("th")
                for col1 in small_table_th:
                    c1 = col1.text.replace('\n(名稱)', '(名稱)') \
                        .replace('\n', '&') \
                        .split("ú")
                    record_grid_title += c1

                break

            small_table2 = self.driver.find_elements_by_id('OrderRecordListInfo')
            for row2 in small_table2:

                small_table2 = row2.find_elements_by_tag_name("td")
                for col2 in small_table2:
                    c2 = col2.text.replace('\n', ' ').split('ú')
                    record_grid += c2
                break

            big_table = self.driver.find_element_by_css_selector(".detailframe.recTb2Div")
            big_table_tr = big_table.find_elements_by_tag_name("tr")

            for row3 in big_table_tr:

                big_table_th = row3.find_elements_by_tag_name("th")

                for col3 in big_table_th:
                    c3 = col3.text.replace('\n((名稱)', '(名稱)'). \
                        replace('交易\n類別', '交易&類別'). \
                        replace('成交價\n(元)', '成交價(元)'). \
                        replace('手續費\n(張)', '手續費(張)'). \
                        replace('證交稅\n(元)', '證交稅(元)'). \
                        replace('借券費\n(元)', '借券費(元)') \
                        .split('ú')

                    record_grid_title += c3

                break
            big_table2 = self.driver.find_elements_by_id('OrderRecordListData')
            for row4 in big_table2:
                big_table2_td = row4.find_elements_by_tag_name("td")
                for col4 in big_table2_td:
                    c4 = col4.text.replace('\n', ' ').split('ú')

                    record_grid2 += c4

                break
            new_record_grid = []
            new_record_grid2 = []
            record_table = []

            for order_grid_len in range(0, len(record_grid), 2):
                new_record_grid.append(record_grid[order_grid_len:order_grid_len + 2])

            for order_grid2_len in range(0, len(record_grid2), 7):
                new_record_grid2.append(record_grid2[order_grid2_len:order_grid2_len + 7])

            for i in range(len(new_record_grid)):
                record_table.append(new_record_grid[i] + new_record_grid2[i])

            pre = prettytable.PrettyTable(record_grid_title, encoding='utf-8')

            for i in range(len(record_table)):
                pre.add_row(record_table[i])
            print(pre)

        # 庫存明細
        def stock_detail():
            account_table.find_element_by_css_selector("a[title='庫存明細']").click()

            time.sleep(0.5)
            detail_grid_title = []
            detail_grid = []
            detail_grid2 = []
            small_table = self.driver.find_element_by_css_selector(".detailframe.recTb1Div")

            small_table_tr = small_table.find_elements_by_tag_name("tr")
            for row1 in small_table_tr:
                small_table_th = row1.find_elements_by_tag_name("th")
                for col1 in small_table_th:
                    c1 = col1.text.replace('\n(名稱)', '(名稱)').split(" ")
                    detail_grid_title += c1

                break

            small_table2 = self.driver.find_elements_by_id('InventoryDetailListInfo')
            for row2 in small_table2:
                small_table2 = row2.find_elements_by_tag_name("td")
                for col2 in small_table2:
                    c2 = col2.text.replace('\n', ' ').split('ú')
                    detail_grid += c2

                break

            big_table = self.driver.find_element_by_css_selector(".detailframe.recTb2Div")
            big_table_tr = big_table.find_elements_by_tag_name("tr")

            for row3 in big_table_tr:
                big_table_th = row3.find_elements_by_tag_name("th")
                for col3 in big_table_th:
                    c3 = col3.text.replace('\n(可平倉)', '(可平倉)'). \
                        replace(' / ', '/'). \
                        replace('買入成本\n預估賣出收入', '買入成本&預估賣出收入') \
                        .split(' ')
                    detail_grid_title += c3

                break

            big_table2 = self.driver.find_elements_by_id('InventoryDetailListData')
            for row4 in big_table2:
                big_table2_td = row4.find_elements_by_tag_name("td")
                for col4 in big_table2_td:
                    c4 = col4.text. \
                        replace('/ ', '/').replace('\n', ' ').split('ú')

                    detail_grid2 += c4

                break

            new_detail_grid = []
            new_detail_grid2 = []
            detail_table = []

            for order_grid_len in range(0, len(detail_grid), 2):
                new_detail_grid.append(detail_grid[order_grid_len:order_grid_len + 2])

            for order_grid2_len in range(0, len(detail_grid2), 7):
                new_detail_grid2.append(detail_grid2[order_grid2_len:order_grid2_len + 7])

            for i in range(len(new_detail_grid)):
                detail_table.append(new_detail_grid[i] + new_detail_grid2[i])

            pre = prettytable.PrettyTable(detail_grid_title, encoding='utf-8')

            for i in range(len(detail_table)):
                pre.add_row(detail_table[i])
            print(pre)

        # 損益試算
        def loss_profit():
            account_table.find_element_by_css_selector("a[title='損益試算']").click()
            try:
                select_loss_profit = int(input("未實現損益:選擇0\n實現損益:選擇1:"))
            except:
                print("請輸入數字")
                function_category()
            try:
                if select_loss_profit == 0:
                    fund_grid_title = []
                    fund_grid = []
                    fund_grid2 = []
                    small_table = self.driver.find_element_by_id("Div1")
                    small_table_tr = small_table.find_elements_by_tag_name("tr")
                    for row1 in small_table_tr:
                        small_table_th = row1.find_elements_by_tag_name("th")
                        for col1 in small_table_th:
                            c1 = col1.text.replace('\n(名稱)', '(名稱)').split(" ")
                            fund_grid_title += c1

                        break

                    small_table2 = self.driver.find_elements_by_id('UnaccomplishedProfitLossListInfo')
                    for row2 in small_table2:
                        small_table2 = row2.find_elements_by_tag_name("td")
                        for col2 in small_table2:
                            c2 = col2.text.replace('\n', '').split('ú')
                            fund_grid += c2

                        break

                    big_table = self.driver.find_element_by_id("Div2")
                    big_table_tr = big_table.find_elements_by_tag_name("tr")

                    for row3 in big_table_tr:
                        big_table_th = row3.find_elements_by_tag_name("th")
                        for col3 in big_table_th:
                            c3 = col3.text.replace('\n(可平倉)', '(可平倉)'). \
                                replace('買賣均價\n現價', '買賣均價&現價'). \
                                replace('買入成本\n預估賣出收入', '買入成本&預估賣出收入') \
                                .split(' ')
                            fund_grid_title += c3

                        break

                    big_table2 = self.driver.find_elements_by_id('UnaccomplishedProfitLossListData')
                    for row4 in big_table2:
                        big_table2_td = row4.find_elements_by_tag_name("td")
                        for col4 in big_table2_td:
                            c4 = col4.text.replace('\n', '&').replace('\n', '').split('ú')

                            fund_grid2 += c4

                        break

                    new_fund_grid = []
                    new_fund_grid2 = []
                    detail_fund_table = []

                    for fund_grid_len in range(0, len(fund_grid), 2):
                        new_fund_grid.append(fund_grid[fund_grid_len:fund_grid_len + 2])

                    for fund_grid2_len in range(0, len(fund_grid2), 7):
                        new_fund_grid2.append(fund_grid2[fund_grid2_len:fund_grid2_len + 7])

                    for i in range(len(new_fund_grid)):
                        detail_fund_table.append(new_fund_grid[i] + new_fund_grid2[i])

                    pre = prettytable.PrettyTable(fund_grid_title, encoding='utf-8')

                    for i in range(len(detail_fund_table)):
                        pre.add_row(detail_fund_table[i])
                    print(pre)

                elif select_loss_profit == 1:
                    # 下拉選單
                    self.driver.find_element_by_css_selector("a[filtervalue='accomplished']").click()
                    self.driver.find_element_by_css_selector("i[class='fa fa-chevron-down']").click()
                    self.driver.find_element_by_css_selector("a[filtervalue='Season']").click()
                    time.sleep(0.5)
                    small_table = self.driver.find_element_by_id("detailframeareaInfo")

                    big_table = self.driver.find_element_by_id("detailframeareaData")

                    fund_grid_title = []
                    fund_grid = []
                    fund_grid2 = []

                    big_table_tr = big_table.find_elements_by_tag_name("tr")
                    small_table_tr = small_table.find_elements_by_tag_name("tr")
                    for row1 in small_table_tr:
                        small_table_th = row1.find_elements_by_tag_name("th")
                        small_table_td = row1.find_elements_by_tag_name("td")
                        for col1 in small_table_th:
                            c1 = col1.text.replace('\n(名稱)', '(名稱)').split(" ")
                            fund_grid_title += c1

                        for col2 in small_table_td:
                            c2 = col2.text.replace('\n', '').split('ú')
                            fund_grid += c2

                    for row2 in big_table_tr:
                        big_table_th = row2.find_elements_by_tag_name("th")
                        big_table2_td = row2.find_elements_by_tag_name("td")
                        for col3 in big_table_th:
                            c3 = col3.text.replace('\n(可平倉)', '(可平倉)').replace('買入成本\n賣出收入', '買入成本&賣出收入').split(' ')
                            fund_grid_title += c3
                        for col5 in big_table2_td:
                            c5 = col5.text.replace('\n', '').split('ú')
                            fund_grid2 += c5

                    new_fund_grid = []
                    new_fund_grid2 = []
                    detail_fund_table = []

                    for fund_grid_len in range(0, len(fund_grid), 2):
                        new_fund_grid.append(fund_grid[fund_grid_len:fund_grid_len + 2])

                    for fund_grid2_len in range(0, len(fund_grid2), 6):
                        new_fund_grid2.append(fund_grid2[fund_grid2_len:fund_grid2_len + 6])

                    for i in range(len(new_fund_grid)):
                        detail_fund_table.append(new_fund_grid[i] + new_fund_grid2[i])

                    pre = prettytable.PrettyTable(fund_grid_title, encoding='utf-8')

                    for i in range(len(detail_fund_table)):
                        pre.add_row(detail_fund_table[i])
                    print(pre)

            except:
                if select_loss_profit > 1:
                    print("沒這個選項")
                    function_category()
                elif select_loss_profit < 0:
                    print("你這個奧客")
                    self.close_stock_system()
            function_category()

        # 我的通知
        def my_information():
            account_table.find_element_by_css_selector("a[title='我的通知']").click()

        # 績效對決
        def pk_():
            account_table.find_element_by_css_selector("a[title='績效對決']").click()
            # percentile_rank = self.driver.find_element_by_xpath('//*[@id="TabContent"]/div[2]/div[1]/ul[1]/li[10]').find_element_by_tag_name('b')
            # print(percentile_rank.text)

        # 熱門討論
        def top_discussion():
            account_table.find_element_by_css_selector("a[title='熱門討論']").click()

        # 下單功能
        def trade_stock():
            buy_sell_stock = 0
            stock_code = 0
            stock_quantity = 0
            stock_price = 0
            buy_sell_stock = input("買賣股票\n買請按b\n賣請按s:")
            if buy_sell_stock == "b":
                self.driver.find_element_by_id("Bs_B").click()
            elif buy_sell_stock == "s":
                self.driver.find_element_by_id("Bs_S").click()
            else:
                self.driver.close()

            stock_code = input("輸入股票號碼:")
            self.driver.find_element_by_id("textBoxCommkey").clear()
            self.driver.find_element_by_id("textBoxCommkey").send_keys(str(stock_code))
            self.driver.find_element_by_id("textBoxCommkey").click()
            self.driver.find_element_by_id("TextBoxQty").send_keys("輸入張數")
            # self.driver.find_element_by_id("linktofollQtow").click()
            time.sleep(1)

            # 印出五買五賣
            url = "https://www.cmoney.tw/vt/ashx/HandlerGetStockPrice.ashx?q=" + stock_code + "&accountType=7&isSDAndSell=false"
            html = requests.get(url).json()
            best5 = html['StockInfo']

            for i in range(1, 6):
                best5_buy = best5['BuyPr' + str(i)]
                best5_sell = best5['SellPr' + str(i)]
                print('買', i, best5_buy, end=' ')
                print('賣', i, best5_sell, end=' ')
                print('')
            while True:

                while True:
                    try:
                        stock_quantity = int(input("輸入股票張數:"))
                        break
                    except:
                        print("請輸入數字")

                self.driver.find_element_by_id("TextBoxQty").clear()
                self.driver.find_element_by_id("TextBoxQty").send_keys(str(stock_quantity))
                while True:
                    try:
                        stock_price = int(input("輸入買賣之股價:"))
                        break
                    except:
                        print("請輸入數字")
                if stock_quantity <= 0 or stock_price <= 0 or stock_quantity > 499:
                    print("輸入數值有誤")
                else:
                    break

            self.driver.find_element_by_id("TextBoxPrice").clear()
            self.driver.find_element_by_id("TextBoxPrice").send_keys(str(stock_price))

            # 下單前確認一下
            run_mother_fucker = str.lower(input("確定要下單嗎?\n如果是請按y\n否請按n:"))
            if run_mother_fucker == "y":
                self.driver.find_element_by_id("Orderbtn").click()

            elif run_mother_fucker == "n":
                continue_or_exit = str.lower(input("要離開程式嗎?\n如果是請按y\n否請按n:"))

                if continue_or_exit == "y":
                    self.close_stock_system()

                elif continue_or_exit == "n":
                    function_category()
            order_search()

            # 下單完看看要不要離開或繼續玩
            continue_or_exit = str.lower(input("要離開程式嗎?\n如果是請按y\n否請按n:"))
            if continue_or_exit == "y":
                self.close_stock_system()
            elif continue_or_exit == "n":
                function_category()

        # 功能選單

        def function_category():
            function_category_ = ""
            while True:
                try:
                    function_category_ = int(
                        input("選擇功能:\n"
                              "1帳戶概覽\n"
                              "2委託查詢\n"
                              "3交易紀錄\n"
                              "4庫存明細\n"
                              "5損益試算\n"
                              "6重新選擇帳號\n"
                              "88離開程式:"))
                    function_category_dict = {"1": view_account,
                                              "2": order_search,
                                              "3": trade_record,
                                              "4": stock_detail,
                                              "5": loss_profit,
                                              '6': my_information,
                                              '7': pk_,
                                              '8': top_discussion,
                                              '9': trade_stock,
                                              '10': self.select_account,
                                              '88': self.close_stock_system
                                              }
                    function_category_dict[str(function_category_)]()
                    break

                except:
                    if function_category_ > 10 and function_category_ != 88:
                        print("沒有那麼多功能")
                        function_category()
                    elif function_category_ < 1:
                        print("你這個奧客")
                        self.close_stock_system()
                    else:
                        print("請輸入數字")

        function_category()
        self.trade_stock_system()

    def close_stock_system(self):
        self.driver.quit()
        sys.exit(0)


if __name__ == "__main__":
    id_ = "0912001585"
    pw_ = "1qaz2wsx3edc"
    main = Action()
    main.start_browser(id_,pw_)
    main.login_ok()
