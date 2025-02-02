from webApp.helper import user
from webApp.helper import twilio
from webApp.helper import general
from webApp.helper import product
from webApp.helper.search_engine import primary_language_cortex as plc1
from webApp.helper.search_engine import product as search_engine_prd
from webApp.mysql_connector import use_db, close_mysql_cursor, create_mysql_conn
import re
from webApp.helper import telegram

IMAGE_DOMAIN_NAME = "https://tmpmc.aitanmall.com"

def handle_initiated_message(data:dict):
    try:
        assert isinstance(data, dict), "Data should be in form of dictionary"
        sender_name = data["ProfileName"]
        text_body = data["Body"]
        receiving_number = data["To"]
        sender_number = str(data["From"])
        start_of_sender_number = sender_number.index("+")
        sender_number = sender_number[start_of_sender_number+1:]
        assert receiving_number == "whatsapp:+601157753611", "Only number +601157753611 is allowed."
        #connect to mysql
        db_conn = general.create_general_mysql_conn()
        db_conn_cursor = db_conn.cursor(named_tuple=True)
        #Simple webhook to get started first. Right now we just want to handle product ordering and let the rest work itself.
        #First we detect if user is asking for a product.
        if len(text_body) > 15:
            language = plc1.detect_language(text_body[:15])
        else:
            language = plc1.detect_language(text_body)
        #Make sure language is set
        languages_accepted = ["my", "cn", "eng"]
        if language not in languages_accepted:
            language = "my"
        #Prepare telegram for notification
        telegram_bot_token = telegram.get_token()
        telegram_chat_id = telegram.get_all_orders_chat_id()
        #Select user session if exist 
        select_user_whastapp_session = user.select_whatsapp_session(db_conn_cursor, sender_number)
        assert isinstance(select_user_whastapp_session, list), "Failed to select user whatsapp session"
        session_just_initiated = False
        if len(select_user_whastapp_session) == 0:
            session_just_initiated = True
            create_whatsapp_session_status = user.create_whatsapp_session(db_conn, db_conn_cursor, "initiated", "", sender_number, language)
            assert create_whatsapp_session_status == True, create_whatsapp_session_status
        #Make sure we continue with the language user wanted unless they want to change language
        language = select_user_whastapp_session[0].user_whatsapp_language if len(select_user_whastapp_session) > 0 else language
        #Define succeeded variable for later return value
        succeeded = False
        if '$' not in text_body:
            if session_just_initiated == True:
                answer_text = identifier_not_found_answer(language)
            else:
                agent_name = "NurNadia"
                agent_link = f"https://api.whatsapp.com/send/?phone=601157753538&text=Salam. Nak minta tolong"
                agent_number = "011-5775-3538"
                answer_text = live_agent_help_answer(language, agent_name, agent_link, agent_number)
                user.remove_whatsapp_session(db_conn, db_conn_cursor, sender_number)
            twilio.send_whatsapp(str(answer_text), sender_number)
            
            telegram.send_message(telegram_bot_token, telegram_chat_id, "1 Whatsapp Bot reply:\n\n"+str(answer_text))
            succeeded = True
        else:
            product_matched = search_product(db_conn_cursor, text_body)
            #Define message according to languages
            if language == "my":
                no_prd_matched_msg = "Minta maaf. Tiada product didapatkan.\nSila cuba sekali lagi"
                prd_matched_msg = "🎉 Gendang sila... 🥁\nMemperkenalkan {}! 🎧\nHarga asalnya sebanyak ~RM{}~, tetapi sekarang ia HANYA *RM{}!* 😱\n*Jaminan 365 hari + jaminan pulangan wang selama 7 hari jika ANDA TIDAK PUAS HATI!* 📣\nJom jom buat pesanan! 💨\nUntuk membuat pesanan, sila lawati {} ATAU hubungi ejen kami {} melalui pautan ini {} atau nombor ini {}."
                how_to_shop_msg = "Untuk maklumat lanjut tentang cara untuk membuat pesanan, sila baca Google Slide ini: https://docs.google.com/presentation/d/1-D54XrvsXcVD3BMMKWfHBkGykStN_KLlhIikYHtqVIg/edit?usp=sharing"

            elif language == "cn":
                no_prd_matched_msg = "不好意思亲. 我们没有您说的产品.\n请您再试一试."
                prd_matched_msg = "🎉 请鼓掌... 🥁\n隆重介绍您{}！🎧\n原价为 ~RM{}~, 但是现在只需要 *RM{}* 就可以是你的了！😱\n*365 天保修 + 如果你不满意，我们保证 7 天退款!*📣\n快点抢下这个优惠吧!💨\n要下订单，请访问 {} 或通过此链接 {} 或此号码 {} 联系我们的代理 {}。"
                how_to_shop_msg = "如需了解更多关于如何下订单的信息，请阅读此 Google Slide ：https://docs.google.com/presentation/d/1-D54XrvsXcVD3BMMKWfHBkGykStN_KLlhIikYHtqVIg/edit?usp=sharing"
            else:
                no_prd_matched_msg = "Sorry. I could not match anything by what you specified.\nPlease can you try again."
                prd_matched_msg = "🎉 Drumroll, please... 🥁\nIntroducing the {}! 🎧\nOriginally priced at a cool ~Rm{}~, but guess what?\nNow, they're yours for *ONLY Rm{}!* 😱\n*Warranty 365 days + 7 days money-back guaranteed if YOU ARE NOT HAPPY!* 📣\nHurry, this deal won't last forever! 💨\nTo place an order, please visit {} OR contact our agent {} via link {} or the number {}"
                how_to_shop_msg = "For more information on how to place order, please read this google slide: https://docs.google.com/presentation/d/1-D54XrvsXcVD3BMMKWfHBkGykStN_KLlhIikYHtqVIg/edit?usp=sharing"
            #If no product is matched
            if product_matched == None:
                answer_text = no_prd_matched_msg
                twilio.send_whatsapp(str(answer_text), sender_number)
                succeeded = True
            else:
                #Define all the details from matched product 
                merchant_id = product_matched.merchant_id
                product_id = product_matched.prd_id
                product_matched_name = product_matched.prd_name
                product_matched_original_price = product_matched.prd_price
                product_matched_offer_price = product_matched.prd_offer_price
                product_matched_image = product_matched.prd_image
                #Define main image url and send it
                prd_main_image_url = f"{IMAGE_DOMAIN_NAME}/static/assets/merchant/{merchant_id}/product/{product_id}/{product_matched_image}"
                twilio.send_media_whatsapp("", sender_number, prd_main_image_url)
                #Get all the gallery images based on language
                product_galleries  = product.get_product_gallery(db_conn_cursor, product_id, language)
                assert isinstance(product_galleries, list) and len(product_galleries) > 0, "Failed to get galleries"
                #Loop through and send them all
                for i in range(len(product_galleries)):
                    product_gallery = product_galleries[i]
                    product_gallery_image = product_gallery.prd_image
                    gallery_image_url = f"{IMAGE_DOMAIN_NAME}/static/assets/merchant/{merchant_id}/product/{product_id}/{product_gallery_image}"
                    twilio.send_media_whatsapp("", sender_number, gallery_image_url)
                #Lastly, send the final message
                order_link = f"https://aitanmall.com/products/{merchant_id}/{product_id}"
                agent_name = "NurNadia"
                agent_link = f"https://api.whatsapp.com/send/?phone=601157753538&text=Salam.Saya berminat nak {product_matched_name}"
                agent_number = "011-5775-3538"
                twilio.send_whatsapp(prd_matched_msg.format(product_matched_name, product_matched_original_price,\
                            product_matched_offer_price, order_link, agent_name, agent_link, agent_number), sender_number)
                twilio.send_whatsapp(str(how_to_shop_msg), sender_number)
                telegram.send_message(telegram_bot_token, telegram_chat_id, f"1 Whatsapp Bot for product {product_matched_name}")
                succeeded = True
        if succeeded:
            return True
        return False
    except Exception as e:
        return e
    finally:
        if db_conn_cursor:
            close_mysql_cursor(db_conn_cursor)
        if db_conn:
            close_mysql_cursor(db_conn)

def identifier_not_found_answer(language):
    try:
        if language == "my":
            return "Assalam! 🤖👋 Saya adalah chatbot WhatsApp anda yang mesra. Superkuasa saya adalah membantu anda mencari produk yang anda minati 🎁🔍 dan menunjukkan anda gambar 📸 dan video 🎥 mereka. Untuk memulakan, sila taipkan nama produk yang anda cari dalam format $nama produk$. Sebagai contoh, anda boleh taip '$Earbuds ANC 2023$'. Mari kita jelajahi bersama! 🌍🚀"
        elif language == "cn":
            return "亲你好！🤖👋 我是你友好的WhatsApp聊天机器人。我的超能力是帮助你找到你感兴趣的产品🎁🔍，并向你展示它们的图片📸和视频🎥。要开始， 请以 $产品名称$ 的格式输入你要查找的产品名称。例如，你可以输入'$Earbuds ANC 2023$'。让我们一起探索吧！🌍🚀"
        return "Hello there! 🤖👋 I'm your friendly WhatsApp chatbot. My superpower is helping you find products you're interested in 🎁🔍 and showing you their images 📸 and videos 🎥. To get started, please type the name of the product you're looking for in the format $product name$. For example, you could type '$Earbuds ANC 2023$'. Let's explore together! 🌍🚀"
    except Exception as e:
        return e
    
def live_agent_help_answer(language, agent_name, agent_link, agent_number):
    try:
        if language == "my":
            message = f"🙇‍♂️ Maaf, saya rasa saya tidak dapat membantu banyak. Sila hubungi ejen kami {agent_name} di {agent_link} atau melalui nombor {agent_number} untuk bantuan lanjut. 📞"
        elif language == "cn":
            message = f"🙇‍♂️ 很抱歉，我认为我可能无法提供更多帮助。请通过 {agent_link} 或电话号码 {agent_number} 联系我们的代理人 {agent_name} 以获取更多帮助。 📞"
        else:
            message = f"🙇‍♂️ I'm sorry, I don't think I can help much with that. Please contact our agent {agent_name} at {agent_link} or via number {agent_number} for further assistance. 📞"

        return message
    except Exception as e:
        return e

def search_product(mysql_cursor, prompt) -> None | tuple | Exception:
    """
    This method search for a product by find a identifier $ and take it as product name
    :return: named tuple in format: (id, prd_name, prd_status, prd_price, prd_offer_price, prd_image ,prd_quantity, prd_sku, prd_date, prd_level, prd_cost , prd_preorders_status, prd_id, merchant_id)
    """
    try:
        product_name = extract_product_name(prompt)
        use_db(mysql_cursor, "product")
        query = """
        SELECT merchant_id,prd_name,prd_id FROM product
        """
        mysql_cursor.execute(query)
        prd_list = mysql_cursor.fetchall()
        # now use product search engine to get result
        matched_prd_data= search_engine_prd.search_products(prd_list, product_name, 1)
        if len(matched_prd_data) > 0:
            product_id = matched_prd_data[0][0]
            merchant_id = matched_prd_data[0][1]
            matched_prd = general.select_product(mysql_cursor,merchant_id,product_id, by_merchant=False)
        else:
            matched_prd = None

        return matched_prd
    except Exception as e:
        return e
    
def extract_product_name(input_string):
    match = re.search(r'\$(.*?)\$', input_string)
    if match:
        return match.group(1)
    else:
        return None