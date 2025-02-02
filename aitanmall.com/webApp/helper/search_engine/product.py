import os
from webApp.helper.json_tools import read_json
from webApp.helper import general as gnr

#Developing mode
develope_mode = True
if not develope_mode:
    print_statement = "ERROR404"
else:
    print_statement = ["Start"]
    #read language_detection_map json file
    language_detection_map_path = os.path.join("/var","www/stage-aitanmall.tech"\
        ,"private","data","language_detection_map.json")
    language_detected_dict = read_json(language_detection_map_path)
    # Load product data

    # Define search function
    def search_products(mysql_tuple_list, searched_key, limit):
        #operation algorithm here
        #1 convert search and database names to lower case
        searched_key = searched_key.lower()
        #2 for efficiency purposes, we convert database names to lower case during the loop
        #3 
        #case #1 : If search key is in the one of our name
        #we then just pop it out and take the len of word as number of char matches
        #case #2 : Search key not directly in name so we check letter by letter in order and see the similarity
        #we then add 1 for each matched letter in order and sum the total matches up and compare
        #list from case 2 is prioritize over case 1 so we will add list from case 1 to case 2 in the end
        results = []
        product_name_size = len(mysql_tuple_list)
        i = 0
        while i < product_name_size:
            matches_with_prd_id = []
            prd_name = mysql_tuple_list[i].prd_name
            prd_id = mysql_tuple_list[i].prd_id
            merchant_id = mysql_tuple_list[i].merchant_id
            prd_name = prd_name.lower()
            #case 1
            if searched_key in prd_name:
                matched_value_total = float(len(prd_name))
                mysql_tuple_list.pop(i)
                i -= 1
                product_name_size -= 1
            #case 2
            else:
                tokenized_search_key = gnr.tokenize(searched_key)
                ignore_letters = ["?", "!", ".", ","]
                #for efficiency purposes we dont tokenize each string but we compare directly by index
                for idx in range(len(tokenized_search_key)):
                    matched_value_total = 0.0
                    token_search_key = tokenized_search_key[idx]
                    #if this token needs to be ignored 
                    if token_search_key in ignore_letters:
                        continue
                    try:
                        if prd_name[idx] == token_search_key:
                            matched_value = 1.1
                        else:
                            matched_value = 0.0
                    except:
                        matched_value = 0.0
                    matched_value_total += matched_value
            if matched_value_total > 0:
                matches_with_prd_id.append(matched_value_total)
                matches_with_prd_id.append([prd_id,merchant_id])
                results.append(matches_with_prd_id)
            i += 1
        #sort it
        results = sorted(results, key=lambda data: data[0], reverse=True)
        results = results[:limit]
        results = [val[1] for val in results]
        return results