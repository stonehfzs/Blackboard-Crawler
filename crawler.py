import requests
from lxml import etree
import os
import time

if __name__ == '__main__':
    # 创建文件夹
    if not os.path.exists('./results'):
        os.mkdir('./results')

    session = requests.Session()
    detail_url = 'https://wlkc.ouc.edu.cn'
    # 使用现成的cookie直接绕过登录页面
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'Cookie': 'JSESSIONID=03CAF8C2AF53FC45E2FE7E115D9C6663; session_id=6BA05B378A8C9369E72001F2CE0D481D; s_session_id=A9855031C21091EA8A2B28708004F6E6; web_client_cache_guid=db210d06-c511-4e41-866b-7577ced68e5c',
    }

    # 总尝试页面
    total_url = 'https://wlkc.ouc.edu.cn/webapps/gradebook/do/student/viewAttempts?method=list&course_id=_31230_1&outcome_definition_id=_201467_1&outcome_id=_4601701_1'
    page_text_tot = session.get(url=total_url, headers=headers)
    tree_tot = etree.HTML(page_text_tot.text)
    attempt_list = tree_tot.xpath('//div[@class=" columnStep clearfix"]//a/@href')

    # 为了去重使用字典保存键值对
    danxuan = {}
    duoxuan = {}
    panduan = {}
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0

    fp1 = open('./results/单选.txt', 'w', encoding='utf-8')
    fp2 = open('./results/多选.txt', 'w', encoding='utf-8')
    fp3 = open('./results/判断.txt', 'w', encoding='utf-8')

    times = 0
    print('download started...')
    for attempt in attempt_list:
        time.sleep(0.5)
        times = times + 1
        new_url = detail_url + attempt
        # print(new_url)
        page_text = session.get(url=new_url, headers=headers)
        tree = etree.HTML(page_text.text)
        pro_list = tree.xpath('//ul[@id="content_listContainer"]/li')

        cnt = 0
        # 每次尝试的内容进行爬取
        for li in pro_list:
            cnt = cnt + 1
            pro_name = li.xpath('normalize-space(.//div[@class="vtbegenerated inlineVtbegenerated"])')

            # 获取所有选项和正确答案（适配选择题和判断题）
            option_divs = li.xpath('.//div[contains(@class,"reviewQuestionsAnswerDiv")]')
            option_texts = []
            correct_texts = []
            for div in option_divs:
                # 选择题选项
                label = div.xpath('.//label')
                if label:
                    text = label[0].xpath('normalize-space(.)')
                else:
                    # 判断题选项
                    text = div.xpath('normalize-space(.//p[@class="pAnswerFormat"])')
                    if not text:
                        text = div.xpath('normalize-space(.//div[@class="vtbegenerated inlineVtbegenerated"])')
                # 只保留非空且未重复的选项
                if text and text not in option_texts:
                    option_texts.append(text)
                # 只保留class完全等于correctAnswerFlag的为正确答案
                if div.xpath('.//span[@class="correctAnswerFlag" and not(contains(@class,"incorrectAnswerFlag"))]'):
                    if text and text not in correct_texts:
                        correct_texts.append(text)


            # 分类保存（全部统一处理）
            if cnt <= 5:  # 单选题
                if pro_name not in danxuan:
                    cnt1 += 1
                    answer_info = {
                        'options': option_texts,
                        'correct': correct_texts
                    }
                    danxuan[pro_name] = answer_info
            elif cnt <= 10:  # 多选题
                if pro_name not in duoxuan:
                    cnt2 += 1
                    answer_info = {
                        'options': option_texts,
                        'correct': correct_texts
                    }
                    duoxuan[pro_name] = answer_info
            else:  # 判断题
                if pro_name not in panduan:
                    cnt3 += 1
                    answer_info = {
                        'options': option_texts,
                        'correct': correct_texts
                    }
                    panduan[pro_name] = answer_info
        print('times: ' + str(times) + ' 单选: ' + str(cnt1) + ',多选：' + str(cnt2) + ',判断: ' + str(cnt3) )

    # 将字典进行按key排序实现不同章节分类进行存储
    num = 0
    for pro in sorted(danxuan):
        num = num + 1
        fp1.write(str(num) + '. ' + pro + '\n')
        fp1.write('选项：\n')
        for opt in danxuan[pro]['options']:
            fp1.write('  ' + opt + '\n')
        fp1.write('正确答案：' + str(danxuan[pro]['correct']) + '\n\n')
    
    num = 0
    for pro in sorted(duoxuan):
        num = num + 1
        fp2.write(str(num) + '. ' + pro + '\n')
        fp2.write('选项：\n')
        for opt in duoxuan[pro]['options']:
            fp2.write('  ' + opt + '\n')
        fp2.write('正确答案：' + str(duoxuan[pro]['correct']) + '\n\n')
    
    num = 0
    for pro in sorted(panduan):
        num = num + 1
        fp3.write(str(num) + '. ' + pro + '\n')
        fp3.write('选项：\n')
        for opt in panduan[pro]['options']:
            fp3.write('  ' + opt + '\n')
        fp3.write('正确答案：' + str(panduan[pro]['correct']) + '\n\n')


    fp1.close()
    fp2.close()
    fp3.close()
    print('total: ' + str(cnt1+cnt2+cnt3) + ' problems have been downloaded.')
